# importing necessary modules
import hmac
import sqlite3

from flask import Flask, request, jsonify, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


# creating a class called users, part of the flask application configuration
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# creating a table to register new users, connecting it to a database called point-of-sale
def register():
    conn = sqlite3.connect('notused.db')                                          # connecting sqlite to the database
    print("Opened Database Successfully")                                         # checking if database was created

    conn.execute("CREATE TABLE IF NOT EXISTS Register(ID_Number TEXT NOT NULL, "  # executing the command to create the table
                 "Name TEXT NOT NULL,"
                 "Surname TEXT NOT NULL,"
                 "Email TEXT NOT NULL,"
                 "Cell TEXT NOT NULL,"
                 "Address TEXT NOT NULL,"
                 "Username TEXT NOT NULL PRIMARY KEY,"
                 "Password TEXT NOT NULL)")
    print("Register table created successfully")                                 # checking if table was created
    conn.close()


register()                                                                       # calling the function register


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
                 "Type TEXT NOT NULL,"
                 "Description TEXT NOT NULL,"  
                 "Price TEXT NOT NULL,"    
                 "Image IMAGE NOT NULL)")
    print("Products table created successfully")
    conn.close()


products()


# creating a function to get all the users from the register table
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


# a function to check if username and password is correct
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# part of the identification
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


# starting the Flask app
app = Flask(__name__)
CORS(app)                                           # allows you to use api
app.debug = True                                    # when finds a bug, it continues to run
app.config['SECRET_KEY'] = 'super-secret'           # a random key used to encrypt your web app

jwt = JWT(app, authenticate, identity)              # using authenticate and identity functions for jwt


@app.route('/protected')                            # a route to use the generated token
@jwt_required()                                     # route only works if you have the generated token
def protected():                                    # a function called protected for the route
    return '%s' % current_identity                  #


# a route with a function to register the users
@app.route('/api/register/', methods=["POST"])
def registration():
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
                           "Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                           (id_numb, name, surname, email, cell, address, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


# a route  that requires a token with a function to add products
@app.route('/api/add-product/', methods=["POST"])
@jwt_required()
def add_products():
    response = {}

    if request.method == "POST":
        name = request.form['Name']
        type = request.form['Type']
        description = request.form['Description']
        price = request.form['Price']
        image = request.form['Image']

        with sqlite3.connect('notused.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Products("
                           "Name,"
                           "Type,"
                           "Description,"
                           "Price,"
                           "Image) VALUES(?, ?, ?, ?, ?)",
                           (name, type, description, price, image))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product added successfully"
        return response


if __name__ == '__main__':
    app.run()
