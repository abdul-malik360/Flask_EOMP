import hmac
import sqlite3

from flask import Flask, request, jsonify, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# creating a table to register new users, connecting it to a database called ...
def register():
    conn = sqlite3.connect('notused.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS Register(ID_Number TEXT NOT NULL, "
                 "Name TEXT NOT NULL,"
                 "Surname TEXT NOT NULL,"
                 "Email TEXT NOT NULL,"
                 "Cell TEXT NOT NULL,"
                 "Address TEXT NOT NULL,"
                 "Username TEXT NOT NULL PRIMARY KEY,"
                 "Password TEXT NOT NULL)")
    print("Register table created successfully")
    conn.close()


register()


# creating a table for the registered users to log in, using their username and password
def login():
    conn = sqlite3.connect('notused.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS Login(Log_ID INTEGER PRIMARY KEY AUTOINCREMENT, "                 
                 "Username TEXT NOT NULL,"
                 "Password TEXT NOT NULL,  FOREIGN KEY(Username) REFERENCES Register(Username))")
    print("Log table created successfully")
    conn.close()


login()


# creating a table for the products
def products():
    conn = sqlite3.connect('notused.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS Products(prod_list INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "Name TEXT NOT NULL,"
                 "type TEXT NOT NULL,"
                 "Description TEXT NOT NULL,"  
                 "Price TEXT NOT NULL,"    
                 "Image IMAGE NOT NULL)")
    print("Products table created successfully")
    conn.close()


products()


def fetch_users():
    with sqlite3.connect('notused.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Register")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[6], data[7]))
    return new_data


users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        id_numb = request.form['ID_Number']
        name = request.form['Name']
        surname = request.form['Surname']
        email = request.form['Email']
        cell = request.form['Cell']
        address = request.form['Address']
        username = request.form['Username']
        password = request.form['Password']

        with sqlite3.connect("notused.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Register("
                           "ID_Number,"
                           "Name,"
                           "Surname,"
                           "Email,"
                           "Cell,"
                           "Address,"
                           "Username,"
                           "Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (id_numb, name, surname, email, cell, address, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


if __name__ == '__main__':
    app.run()
