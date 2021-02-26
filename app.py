from flask import stream_with_context, Flask, render_template, flash, redirect, request, session, logging, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from camera import VideoCamera
from train import train
import os
import cv2
import json
from datetime import datetime
import time
from sqlalchemy import func

app = Flask(__name__)

app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN'
project_dir = os.path.dirname(os.path.abspath(__file__))
print(os.path.join(project_dir, "attendance.db"))
engine = "sqlite:///{}".format(os.path.join(project_dir, "attendance.db"))
app.config['SQLALCHEMY_DATABASE_URI'] = engine
db = SQLAlchemy(app)



# Defining Table
class User(db.Model):
    __tablename__ = 'User'
    index = db.Column(db.Integer)
    employeeid = db.Column(db.Integer(), primary_key = True, nullable = False)
    name= db.Column(db.String(15), nullable = False)
    email = db.Column(db.String(50), nullable = False)
    phone = db.Column(db.Integer(), nullable = False)
    password = db.Column(db.String(256), default = '12345', nullable = False)
    admin = db.Column(db.Integer(), default = 0, nullable = False)

class CheckIn(db.Model):
    __tablename__ = 'CheckIn'
    index = db.Column(db.Integer, primary_key = True)
    employeeid = db.Column(db.Integer(), db.ForeignKey("User.employeeid"), unique=True, nullable = True)
    time = db.Column(db.DateTime(), nullable = False)

class CheckOut(db.Model):
    __tablename__ = 'CheckOut'
    index = db.Column(db.Integer,primary_key = True)
    employeeid = db.Column(db.Integer(),db.ForeignKey("User.employeeid") , unique=True, nullable = True)
    time = db.Column(db.DateTime(), nullable = False)


@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/home')
def home():
    users_db = User.query.all()
    user = {}
    for u in users_db:
        user[u.employeeid] = u.name

    check_in_info = CheckIn.query.filter(func.date(CheckIn.time) == datetime.now().date()).all()
    check_in_lst = []
    for c in check_in_info:
        check_in_lst.append(
            {
                'name': user[c.employeeid],
                'empID': c.employeeid,
                'time': c.time
            }
        )
    return render_template('home.html', info=check_in_lst)

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    session.clear()
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate:
        user = User.query.filter_by(employeeid = form.employeeid.data).first()
        if user:
            if user.password == form.password.data == "12345":
                session['logged_in'] = True
                session['admin'] = user.admin
                session['name'] = user.name
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
    return render_template('login.html', form = form)

@app.route('/showEmployee/')
def showEmployee():
    info = {}
    info['data'] = []
    users = User.query.all()
    for user in users:
        info['data'].append({
            'name': user.name,
            'email': user.email,
            'empID': user.employeeid,
            'phone': user.phone
        })
    return render_template('show_employee.html', info=info)

@app.route('/getEmployee/', methods=['GET'])
def getEmployee():
    ret = []
    users = User.query.all()
    for user in users:
        ret.append({
            'name': user.name,
            'email': user.email,
            'empID': user.employeeid,
            'phone': user.phone
        })
    return json.dumps(ret)

@app.route('/showRegister/')
def showRegister():
    return render_template('register.html')

@app.route('/register/', methods = ['POST'])
def register():
    name = request.form['inputName']
    email = request.form['inputEmail']
    empID = request.form['inputEmpID']
    phone = request.form['inputPhone']
    if request.method == 'POST':
        new_user = User(
            name = name, 
            employeeid = empID,
            email = email, 
            phone = phone)
        db.session.add(new_user)
        db.session.commit()
        session['empName'] = name
        session['empID'] = empID
        return json.dumps({'status':'OK'})

    return render_template('register.html')

@app.route('/showRemove/')
def showRemove():
    return render_template('remove.html')

# FEEDING CAMERA TO WEB APP
@app.route('/showGetFaces/')
def showGetFaces():
    return render_template('get_faces.html')

def gen(camera, output, max_count=25):
    faces = 0
    while faces < max_count:
        #get camera frame
        faces, frame = camera.get_frame(output, faces)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed', methods=['GET'])
def video_feed():
    id_name = {}
    with open('C:/Users/nhinp3/Face_recognition_insightface/src/id_name.json', 'r') as f:
        id_name = json.load(f)
        empID = session['empID']
        empName = session['empName']
        id_name[empID] = empName
    
    with open('C:/Users/nhinp3/Face_recognition_insightface/src/id_name.json', 'w') as f:
        json.dump(id_name, f)

    # Create output dir
    output = os.path.join('C:/Users/nhinp3/Face_recognition_insightface/src/dataset/train', session['empID'])
    if not(os.path.exists(output)):
        os.makedirs(output) 
    
    camera = VideoCamera()
    flash('Please press Finish button when finished collecting 25 photos.')
    return Response(gen(camera, output),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/train_model', methods=['GET'])
def train_model():
    train()
    flash('Finished training model')
    return redirect(url_for('home'))

@app.route('/showRecognizer/')
def showRecognizer():
    return render_template('recognize_faces.html')

def add_time(empID, time):
    check_in_info = CheckIn.query.filter(CheckIn.employeeid==empID, func.date(CheckIn.time) == time.date()).all()
    if(len(check_in_info) == 0):
        check_in = CheckIn(
            employeeid = empID,
            time = time)
        db.session.add(check_in)
        db.session.commit()

    return

def recognize(camera):
    frames = 0
    while True:
        #get camera frame
        empID, time, frame = camera.recognizer(frames)
        print(empID, time)
        if empID != '' and time != 0:
            add_time(empID, time)
        frames += 1
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/recognize_face', methods=['GET'])
def recognize_face():
    camera = VideoCamera()
    return Response(stream_with_context(recognize(camera)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logout/')
def logout():
    session.clear()
    session['logged_in'] = False
    return redirect(url_for('index'))


if __name__ == '__main__':
    # db.create_all(engine)
    app.run(debug=True)