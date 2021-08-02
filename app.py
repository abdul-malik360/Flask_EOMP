import hmac
import sqlite3

from flask import Flask, request, jsonify, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


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


