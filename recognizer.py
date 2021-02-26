import sys
sys.path.append('../insightface/deploy')
sys.path.append('../insightface/src/common')

from mtcnn.mtcnn import MTCNN
from imutils import paths
import face_preprocess
import numpy as np
import face_model
import argparse
import pickle
import time
import dlib
import cv2
import os
import json

ap = argparse.ArgumentParser()

ap.add_argument("--mymodel", default="../src/outputs/knn_model.pkl",
    help="Path to recognizer model")
ap.add_argument("--embeddings", default="../src/outputs/embeddings.pickle",
    help='Path to embeddings')


ap.add_argument('--image-size', default='112,112', help='')
ap.add_argument('--model', default='../insightface/models/model-y1-test2/model,0', help='path to load model.')
ap.add_argument('--ga-model', default='', help='path to load model.')
ap.add_argument('--gpu', default=0, type=int, help='gpu id')
ap.add_argument('--det', default=0, type=int, help='mtcnn option, 1 means using R+O, 0 means detect from begining')
ap.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
ap.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')

args = ap.parse_args()

def recognizer():
    data = pickle.loads(open(args.embeddings, "rb").read())
    labels = data['names']
    embeddings = data['embeddings']
    print(labels)

    model = joblib.load(args.mymodel)

if __name__ == '__main__':
    recognizer()