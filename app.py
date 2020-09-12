from flask import Flask
import pyodbc
# from database.connect import *
from database.schema import Customer
from database.queries import *

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hello Azure!</h1>"


@app.route("/test")
def test():
    return str(get_customers())
