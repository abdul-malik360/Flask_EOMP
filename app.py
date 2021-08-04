# importing necessary modules
import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message


# creating a class for all the tables
class PointOfSaleTables:
    def __init__(self):
        self.conn = sqlite3.connect('point_of_sale.db')              # connecting sqlite to the database called point-of-sale
        self.cursor = self.conn.cursor()

    # creating a table to register new users,
    def register(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS Register(ID_Number TEXT NOT NULL, "  # command to create the table
                          "Name TEXT NOT NULL,"
                          "Surname TEXT NOT NULL,"
                          "Email TEXT NOT NULL,"
                          "Cell TEXT NOT NULL,"
                          "Address TEXT NOT NULL,"
                          "Username TEXT NOT NULL PRIMARY KEY,"
                          "Password TEXT NOT NULL)")
        print("Register table created successfully")                                 # checking if table was created
        self.conn.close()

        return self.register                                                         # calling the function register

    # creating a table for the products
    def products(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS Products(prod_list INTEGER PRIMARY KEY AUTOINCREMENT, "
                          "Name TEXT NOT NULL,"
                          "Type TEXT NOT NULL,"
                          "Description TEXT NOT NULL,"  
                          "Price TEXT NOT NULL)")
        print("Products table created successfully")
        self.conn.close()

        return self.products


PointOfSaleTables()


# creating a class called users, part of the flask application configuration
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# creating a function to get all the users from the register table
def fetch_users():
    with sqlite3.connect('point_of_sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Register")
        users = cursor.fetchall()                                      # to fetch all the users

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[6], data[7]))           # getting the id, username and password
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
app.config["JWT_EXPIRATION_DELTA"] = datetime.timedelta(days=1)  # allows token to last a day

app.config['MAIL_SERVER'] = 'smtp.gmail.com'        # following code is used to send email's through flask
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '62545a@gmail.com'
app.config['MAIL_PASSWORD'] = 'Dummy123!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)                                    # end of email code config

jwt = JWT(app, authenticate, identity)              # using authenticate and identity functions for jwt


@app.route('/protected')                            # a route to use the generated token
@jwt_required()                                     # route only works if you have the generated token
def protected():                                    # a function called protected for the route
    return '%s' % current_identity


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

        with sqlite3.connect("point_of_sale.db") as conn:
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
            response["message"] = "success, Check Email"
            response["status_code"] = 201

            msg = Message('Welcome To My Point Of Sale', sender='62545a@gmail.com', recipients=[email])
            msg.body = "Thank You for registering with us " + name + "." + " Don't forget your Username: " + username + " and " "Password: " + password + "."
            mail.send(msg)
        return response


# a route to view all the Registered users
@app.route('/api/show-users/', methods=["GET"])
@jwt_required()
def show_users():
    response = {}

    with sqlite3.connect("point_of_sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Register")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


# a route to view a user
@app.route('/api/view-user/<Username>', methods=["GET"])
@jwt_required()
def view_user(Username):
    response = {}
    with sqlite3.connect('point_of_sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Register WHERE Username='" + str(Username) + "'")
        response["status_code"] = 200
        response["description"] = "User retrieved successfully"
        response["data"] = cursor.fetchone()
    return jsonify(response)


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

        with sqlite3.connect('point_of_sale.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Products("
                           "Name,"
                           "Type,"
                           "Description,"
                           "Price) VALUES(?, ?, ?, ?)",
                           (name, type, description, price))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product added successfully"
        return response


# a route to view all the products added
@app.route('/api/show-products/', methods=["GET"])
def show_products():
    response = {}

    with sqlite3.connect("point_of_sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


# a route to view each product by it's ID
@app.route('/api/view-product/<int:prod_list>', methods=["GET"])
def view_product(prod_list):
    response = {}

    with sqlite3.connect('point_of_sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE prod_list=" + str(prod_list))

        response["status_code"] = 200
        response["description"] = "Product retrieved successfully"
        response["data"] = cursor.fetchone()
    return jsonify(response)


# a route to edit a product
@app.route('/edit-product/<int:prod_list>', methods=["PUT"])
@jwt_required()
def edit_product(prod_list):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('point_of_sale.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("Name") is not None:
                put_data["Name"] = incoming_data.get("Name")

                with sqlite3.connect('point_of_sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET Name =? WHERE prod_list=?", (put_data["Name"], prod_list))
                    conn.commit()
                    response['message'] = "Name update was successful"
                    response['status_code'] = 200

            if incoming_data.get("Type") is not None:
                put_data['Type'] = incoming_data.get('Type')

                with sqlite3.connect('point_of_sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET Type =? WHERE prod_list=?", (put_data["Type"], prod_list))
                    conn.commit()
                    response['message'] = "Type update was successful"
                    response['status_code'] = 200

            if incoming_data.get("Description") is not None:
                put_data["Description"] = incoming_data.get("Description")

                with sqlite3.connect('point_of_sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET Description =? WHERE prod_list=?", (put_data["Description"], prod_list))
                    conn.commit()
                    response['message'] = "Description update was successful"
                    response['status_code'] = 200

            if incoming_data.get("Price") is not None:
                put_data['Price'] = incoming_data.get('Price')

                with sqlite3.connect('point_of_sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET Price =? WHERE prod_list=?", (put_data["Price"], prod_list))
                    conn.commit()
                    response['message'] = "Price update was successful"
                    response['status_code'] = 200

    return response


# a route to delete products
@app.route("/api/delete-product/<int:prod_list>")
@jwt_required()
def delete_product(prod_list):
    response = {}
    with sqlite3.connect('point_of_sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Products WHERE prod_list=" + str(prod_list))
        conn.commit()
        response['status_code'] = 204
        response['message'] = "Product deleted successfully"
    return response


if __name__ == '__main__':
    app.run()
