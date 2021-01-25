# import required library
import pandas as pd
import numpy as np
from flask import Flask, render_template, request
from flask_restful import Api, Resource, abort

app = Flask(__name__)
api = Api(app)


# page management
@app.route("/")
def main():
    return render_template("index.html")

@app.route('/SignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/SignIn')
def showSignIp():
    return render_template('signin.html')

@app.route('/admin')
def showAdmin():
    pass
    # return render_template('admin.html'')

@app.route('/user')
def showUser():
    pass
    # return render_template('user.html')


# load data for authentication login and store into login_database
# each student data is stored in the form {emp_id : [name, phone, email, dob]}
data = pd.read_excel("ds_process.xlsx", sheet_name="Sheet1")
emp_id = np.array(data["Employee_ID"][0: 60]).astype("int")
name = np.array(data["Name"][0: 60])
phone = np.array([i.replace(" ", "").replace(".","") if isinstance(i, str) else i for i in data["Phone"][0:60]])
dob = data["DOB"][0:60]
email = np.array(data["Email"][0: 60])

data_dict = {}
i = 0 
while i < len(emp_id):
    data_dict[emp_id[i]] = [name[i], phone[i], email[i], dob[i]]
    i += 1

# required info when logging in 
# login_args = reqparse.RequestParser()
# login_args.add_argument("employee_id", type=int, help="Employee ID is required", required=True)
# login_args.add_argument("password", type=int, help="Your phone number registered with Vingroup", required=True)


# api management
# class log_in_authenticate(Resource):
#     # take employee_id in and return system's default password
# 	def put(self, id):
#         pass
        # args = login_args.parse_args()
        # print(args["employee_id"])
        # print(args["password"])
        # return 0

# api.add_resource(log_in_authenticate, "/user")

if __name__ == "__main__":
    app.run(debug=True)

