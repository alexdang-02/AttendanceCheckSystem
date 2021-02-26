import sys
sys.path.append('../insightface/deploy')
sys.path.append('../insightface/src/common')

import os
import cv2
import numpy as np
import face_preprocess
from mtcnn.mtcnn import MTCNN
from imutils import paths
import face_model
import argparse
import pickle
import time
import dlib
import json
import joblib
from datetime import datetime

ap = argparse.ArgumentParser()

ap.add_argument("--mymodel", default="../src/outputs/knn_model.pkl",
    help="Path to recognizer model")


ap.add_argument('--image-size', default='112,112', help='')
ap.add_argument('--model', default='../insightface/models/model-y1-test2/model,0', help='path to load model.')
ap.add_argument('--ga-model', default='', help='path to load model.')
ap.add_argument('--gpu', default=0, type=int, help='gpu id')
ap.add_argument('--det', default=0, type=int, help='mtcnn option, 1 means using R+O, 0 means detect from begining')
ap.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
ap.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')

args = ap.parse_args()

# Initialize faces embedding model
embedding_model = face_model.FaceModel(args)
detector = MTCNN()
ds_factor=0.6   
class VideoCamera(object):
    def __init__(self):
        #capturing video
        self.video = cv2.VideoCapture(0)
        with open('../src/id_name.json', 'r', encoding='utf-8') as f:
           self.id_name = json.load(f)
        self.model = joblib.load(args.mymodel)
        print('Finished loading necessary data')
    
    def __del__(self):
        #releasing camera
        self.video.release()

    def get_frame(self, output, faces):
        ret, frame = self.video.read()
        frame=cv2.resize(frame,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)                    
        max_bbox = np.zeros(4)
        bboxes = detector.detect_faces(frame)

        if len(bboxes) != 0:
            # Get only the biggest face
            max_area = 0
            for bboxe in bboxes:
                bbox = bboxe["box"]
                bbox = np.array([bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3]])
                keypoints = bboxe["keypoints"]
                area = (bbox[2]-bbox[0])*(bbox[3]-bbox[1])
                if area > max_area:
                    max_bbox = bbox
                    landmarks = keypoints
                    max_area = area

            max_bbox = max_bbox[0:4]

            # convert to face_preprocess.preprocess input
            landmarks = np.array([landmarks["left_eye"][0], landmarks["right_eye"][0], landmarks["nose"][0], landmarks["mouth_left"][0], landmarks["mouth_right"][0],
                                 landmarks["left_eye"][1], landmarks["right_eye"][1], landmarks["nose"][1], landmarks["mouth_left"][1], landmarks["mouth_right"][1]])
            landmarks = landmarks.reshape((2,5)).T
            nimg = face_preprocess.preprocess(frame, max_bbox, landmarks, image_size='112,112')
            cv2.imwrite(os.path.join(output, "{}.jpg".format(faces+1)), nimg)
            cv2.rectangle(frame, (max_bbox[0], max_bbox[1]), (max_bbox[2], max_bbox[3]), (255, 0, 0), 2)
            cv2.putText(frame, str(faces+1), (max_bbox[0], max_bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            print("[INFO] {} faces detected".format(faces+1))
            faces += 1
        cv2.imshow("Face detection", frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return faces, jpeg.tobytes()

    def recognizer(self, frames):
        empID = ''
        reco_tock = 0
        ret, frame = self.video.read()
        frame=cv2.resize(frame,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)

        detect_tick = time.time()
        bboxes = detector.detect_faces(frame)
        detect_tock = time.time()
        print("Faces detection time: {}s".format(detect_tock-detect_tick))

        if len(bboxes) != 0:
            for bboxe in bboxes:
                bbox = bboxe['box']
                bbox = np.array([bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3]])
                landmarks = bboxe['keypoints']
                landmarks = np.array([landmarks["left_eye"][0], landmarks["right_eye"][0], landmarks["nose"][0], landmarks["mouth_left"][0], landmarks["mouth_right"][0],
                                     landmarks["left_eye"][1], landmarks["right_eye"][1], landmarks["nose"][1], landmarks["mouth_left"][1], landmarks["mouth_right"][1]])
                landmarks = landmarks.reshape((2,5)).T
                nimg = face_preprocess.preprocess(frame, bbox, landmark=landmarks, image_size='112,112')
                nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
                nimg = np.transpose(nimg, (2,0,1))
                embedding = embedding_model.get_feature(nimg).reshape(1,-1)

                text = "Unknown"

                # Predict class
                preds = self.model.predict(embedding)
                proba = np.max(self.model.predict_proba(embedding))
                empID = preds[0]
                name = self.id_name[empID]
                text = name
                print("Recognized: {} <{:.2f}>".format(name, proba*100))

                y = bbox[1] - 10 if bbox[1] - 10 > 10 else bbox[1] + 10
                cv2.putText(frame, text, (bbox[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,0,0), 2)
                reco_tock = datetime.now()
        cv2.imshow("Frame", frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return empID, reco_tock, jpeg.tobytes()