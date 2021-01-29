from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField, DateField

from wtforms.validators import DataRequired

class LoginForm(Form):

    employeeid = IntegerField("EmployeeID", validators=[validators.Length(min=7, max=7), validators.DataRequired(message="Please Fill This Field")])

    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])


class RegisterForm(Form):
    
    name = StringField("Full Name", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    
    employeeid = IntegerField("Employee ID", validators=[validators.NumberRange(min=3658384, max = 3658443), validators.DataRequired(message="Please Fill This Field")])
    
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address")])
    
    dob = StringField("Date of Birth", validators=[validators.DataRequired(message="Please Fill This Field")])

    password = PasswordField("Password", validators=[
    
        validators.DataRequired(message="Please Fill This Field"),
    
        validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")
    ])
    
    confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")])

