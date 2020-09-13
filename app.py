from flask import Flask, jsonify, request
import pyodbc
# from database.connect import *
from database.schema import Customer
from database.queries import *
from flask_cors import CORS



from util.all import json_response

app = Flask(__name__)
CORS(app)



@app.route("/")
def index():
    return "<h1>Hello Azure!</h1>"


@app.route("/customer", methods=['POST'])
def new_customer():
    content = request.get_json()
    customer=create_customer(content)
    return json_response(customer.to_json(), 201)

if __name__ == '__main__':
    app.run(debug=True)
