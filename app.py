from flask import Flask, render_template, flash, redirect, request, session, logging, url_for

from flask_sqlalchemy import SQLAlchemy, create_engine

from forms import LoginForm, RegisterForm

from werkzeug.security import generate_password_hash, check_password_hash

import os

app = Flask(__name__)

app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

project_dir = os.path.dirname(os.path.abspath(__file__))

engine = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app.config['SQLALCHEMY_DATABASE_URI'] = database_file

db = SQLAlchemy(app)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name= db.Column(db.String(15), unique=True)

    employeeid = db.Column(db.Integer(), unique=True)

    dob = db.Column(db.String(50))

    email = db.Column(db.String(50), unique = True)

    password = db.Column(db.String(256))

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login/', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate:

        user = User.query.filter_by(employeeid = form.employeeid.data).first()

        if user:
            if check_password_hash(user.password, form.password.data):

                flash('You have successfully logged in.', "success")
                
                session['logged_in'] = True

                session['name'] = user.name

                session['employeeid'] = user.employeeid

                return redirect(url_for('home'))

            else:

                flash('Username or Password Incorrect', "Danger")

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
            
            password = hashed_password)
        
        session['logged_in'] = True

        session['employeeid'] = form.employeeid.data

        session['name'] = form.name.data

        db.session.add(new_user)
    
        db.session.commit()
    
        flash('You have successfully registered', 'success')
    
        return redirect(url_for('home'))
    
    else:
        flash('Error trying to register', "Danger")
        return render_template('register.html', form = form)

# @app.route('/delete/', methods = ['DELETE'])
# def delete_account():






@app.route('/logout/')
def logout():
    
    session['logged_in'] = False

    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all(engine)
    app.run(debug=True)