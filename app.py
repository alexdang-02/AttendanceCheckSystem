from flask import Flask, render_template, flash, redirect, request, session, logging, url_for, Response

from flask_sqlalchemy import SQLAlchemy

from forms import LoginForm, RegisterForm

from werkzeug.security import generate_password_hash, check_password_hash

import os

import cv2

app = Flask(__name__)

app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN'
project_dir = os.path.dirname(os.path.abspath(__file__))
engine = "sqlite:///{}".format(os.path.join(project_dir, "attendance.db"))
app.config['SQLALCHEMY_DATABASE_URI'] = engine
db = SQLAlchemy(app)



# Defining Table
class User(db.Model):
    __tablename__ = 'User'
    index = db.Column(db.Integer)
    employeeid = db.Column(db.Integer(), unique=True, primary_key = True, nullable = False)
    name= db.Column(db.String(15), unique=True, nullable = False)
    dob = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(50), unique = True, nullable = False)
    phone = db.Column(db.Integer(), unique = True, nullable = False)
    password = db.Column(db.String(256), nullable = False)


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
def home():
    return render_template('index.html')


@app.route('/login/', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate:
        user = User.query.filter_by(employeeid = form.employeeid.data).first()
        if user:
            if user.password == form.password.data == "12345":
                flash('You have successfully logged in.', "success")
                session['logged_in'] = True
                session['name'] = user.name
                session['employeeid'] = user.employeeid
                flash("Please change default password immediately", "danger")
                return redirect(url_for('home'))
            else:
                flash('Username or Password Incorrect', "danger")
                return redirect(url_for('login'))
    return render_template('login.html', form = form)


@app.route('/register/', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(
            name = form.name.data, 
            employeeid = form.employeeid.data,
            dob = form.dob.data,
            email = form.email.data, 
            phone = form.phone.data,
            password = hashed_password)
        
        session['logged_in'] = True
        session['employeeid'] = form.employeeid.data
        session['name'] = form.name.data
        db.session.add(new_user)
        db.session.commit()
    
        flash('You have successfully registered', 'success')
        return redirect(url_for('home'))

    flash('Error trying to register', "danger")
    return render_template('register.html', form = form)

# @app.route('/delete/', methods = ['DELETE'])
# def delete_account():


# FEEDING CAMERA TO WEB APP





def gen_frames():  # generate frame by frame from camera
    camera = cv2.VideoCapture(0)
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return render_template('scan.html')




@app.route('/logout/')
def logout():
    
    session['logged_in'] = False

    return redirect(url_for('home'))

if __name__ == '__main__':
    # db.create_all(engine)
    app.run(debug=True)