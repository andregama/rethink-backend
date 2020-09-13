from flask import Flask, jsonify
import pyodbc
# from database.connect import *
from database.schema import Customer
from database.queries import *

from util.all import json_response
app = Flask(__name__)


@app.route("/")
def index():
    return "<h1>Hello Azure!</h1>"


@app.route("/test")
def test():
    return json_response(get_customers())

if __name__ == '__main__':
    app.run(debug=True)
