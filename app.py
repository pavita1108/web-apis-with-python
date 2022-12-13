from flask import Flask, jsonify, request, render_template
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import re 
import jwt
from datetime import datetime, timedelta
from functools import wraps
import config

app = Flask(__name__)

db = MySQL()

api = Api(app)

#Set database credentials in config.
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pavita'
app.config['MYSQL_DATABASE_DB'] = 'tst'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


#Initialize the MySQL extension
db.init_app(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.form['x-access-token']

        try:
            data = jwt.decode(token, config.SECRET_KEY,algorithms=["HS256"])
            _username = data['username']
            val = f"""SELECT * FROM userdata WHERE username = '{_username}'"""
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute(val)
            current_user = cursor.fetchall
            if not current_user:
                return 'Unauthorized Access!', 401
        except:
            return 'Unauthorized Access!', 401
        return f(*args, **kwargs)

    return decorated

@app.get("/view")
@token_required 
def get():
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fertility")
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.post("/create")
def post():
    try:
        conn = db.connect()
        cursor = conn.cursor()
        _id = int(request.form['id'])
        _season = request.form['Season']
        _age = int(request.form['Age'])
        _cd = request.form['Childish diseases']
        _accident = request.form['Accident or serious trauma']
        _surgical = request.form['Surgical intervention']
        _fevers = request.form['High fevers in the last year']
        _alcohol = request.form['Frequency of alcohol consumption']
        _smoking = request.form['Smoking habit']
        _sitting = int(request.form['Number of hours spent sitting per day'])
        _diagnosis = request.form['Diagnosis']

        insertval = f"""INSERT INTO fertility VALUES({_id},{_season}, {_age}, {_cd}, {_accident}, {_surgical}, {_fevers}, {_alcohol}, {_smoking},{_sitting},{_diagnosis})"""
        cursor.execute(insertval)
        conn.commit()
        response = jsonify(message='Data added to the dataset successfully.', id=cursor.lastrowid)
        response.status_code = 200
    except Exception as e:
        print(e)
        response = jsonify('Failed to add data to the dataset.')
        response.status_code = 400
    finally:
        cursor.close()
        conn.close()
        return(response)

@app.put("/update")
def update():
    try:
        conn = db.connect()
        cursor = conn.cursor()
        _id = int(request.form['id'])
        _cd = request.form['Childish diseases']
        _accident = request.form['Accident or serious trauma']
        _surgical = request.form['Surgical intervention']
        _smoking = request.form['Smoking habit']
        _diagnosis = request.form['Diagnosis']   
        updateval = f"""UPDATE fertility SET child = {_cd}, accident = {_accident}, surgical = {_surgical}, smoking = {_smoking}, Diagnosis = {_diagnosis} WHERE id = {_id} """
        print(updateval)  
        cursor.execute(updateval)
        conn.commit()
        response = jsonify(message='Data in the dataset updated successfully.', id=cursor.lastrowid)
        response.status_code = 200
    except Exception as e:
        print(e)
        response = jsonify('Failed to update data in the dataset.')
        response.status_code = 400
    finally:
        cursor.close()
        conn.close()
        return(response)

@app.delete("/remove")
def delete ():
    try:
        conn = db.connect()
        cursor = conn.cursor()
        _id = int(request.form['id'])
        delval = f"""DELETE FROM fertility WHERE id = {_id}"""
        cursor.execute(delval)
        conn.commit()
        response = jsonify(message='Data in the dataset deleted successfully.', id=cursor.lastrowid)
        response.status_code = 200
    except Exception as e:
        print(e)
        response = jsonify('Failed to delete data in the dataset.')
        response.status_code = 400
    finally:
        cursor.close()
        conn.close()
        return(response)


@app.route('/login', methods=['POST'])
def login():
    response = {
        "success" : False,
        "message" : "Invalid parameters",
        "token" : ""
    }
    try:
        _username = request.form['username']
        _password = request.form['password']

        val = f"""SELECT * FROM userdata WHERE username = '{_username}'"""
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(val)
        user = cursor.fetchall()

        if not user:
            response["message"] = "Unauthorized Access!"
            return response, 401

        if user[0][1] == _password :
            token = jwt.encode({
                'username': user[0][0],
                'exp': datetime.utcnow() + timedelta(minutes=30)
            }, config.SECRET_KEY)
            response["message"] = "token generated"
            response["token"] = token
            response["success"] = True
            return response, 200
        response["message"] = 'Invalid emailid or password'
        return response, 403
    except Exception as ex:
        print(str(ex))
        return response, 422

if __name__=="__main__":
    app.run(debug=True)