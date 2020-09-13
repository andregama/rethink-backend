from flask import Flask, jsonify, request
import pyodbc
# from database.connect import *
from database.schema import Customer
from database.queries import *
from flask_cors import CORS
import uuid
from logging import getLogger

from util.all import json_response

app = Flask(__name__)
logger = getLogger(__name__)

CORS(app)


# def get_investment_invested_amount(investments:Tuple[Investment])->Decimal:
#     amount=0
#     for investment in investments:
#         amount += investment.amount
#     return amount

@app.route("/")
def index():
    return "<h1>Hello Azure!</h1>"

@app.route("/customer", methods=['POST'])
def new_customer():
    content = request.get_json()
    customer=create_customer(content)
    return json_response(customer.to_json(), 201)

@app.route("/customer/<id>", methods=['GET'])
def take_customer(id:str):
    if(id != None):
        customer = get_customer(uuid.UUID(id))
        if(customer != None):
            return json_response(data=customer.to_json(), status=200)
    return json_response(data='Customer not found', status=404)

@app.route("/investment", methods=['POST', 'GET'])
def get_create_investment():
    if(request.method == 'POST'):
        content = request.get_json()
        investment=create_investment(content)
        return json_response(investment.to_json(), 201)
    else:
        user_id = request.args.get('customer_id')
        if(user_id != None):
            investments = get_user_investments(uuid.UUID(user_id))
            if(investments != None):
                return json_response(data=[investment.to_json() for investment in investments], status=200)
    return json_response(data='Customer\'s investments not found', status=404)

@app.route("/transaction", methods=['POST', 'GET'])
def get_create_transaction():
    if(request.method == 'POST'):
            content = request.get_json()
            transaction=create_transaction(content)
            add_amount_to_balance(content['customer_id'], content['amount'])
            if(content['goal_id'] != None):
                if(get_goal_completion(transaction.goal.id) > 1):
                    complete_goal(transaction.goal.id)
            return json_response(transaction.to_json(), 201)
    else:
        user_id = request.args.get('customer_id')
        limit= request.args.get('limit')
        if(user_id != None):
            if(limit == None):
                limit=5
            transactions = get_last_transactions(uuid.UUID(user_id), limit)
            if(transactions != None):
                return json_response(
                    data=[transaction.to_json() for transaction in transactions], status=200)
    return json_response(data='Customer\'s transactions nor found', status=404)

@app.route("/investment-transactions", methods=['GET'])
def get_transactions():
    invest_id = request.args.get('investment_id')
    if(invest_id != None):
        transactions = get_transactions_by_investment(uuid.UUID(invest_id))
        if(transactions != None):
            return json_response(
                data=[transaction.to_json() for transaction in transactions], status=200)
    return json_response(data='Customer\'s transactions not found', status=404)

@app.route("/investment-type", methods=['POST', 'GET'])
def get_create_invest_type():
    if(request.method == 'POST'):
            content = request.get_json()
            invest_type=create_investment_type(content)
            return json_response(invest_type.to_json(), 201)
    else:
        invest_type_id = request.args.get('investment_type_id')
        if(invest_type_id != None):
            invest_type = get_investment_type(invest_type_id)
            if(invest_type != None):
                return json_response(data=invest_type.to_json(), status=200)
    return json_response(data='Investment type not found', status=404)


@app.route("/all-investment-types", methods=['GET'])
def get_invest_types():
    invest_types = get_investment_types()
    if(invest_types != None):
            return json_response(data=[invest_type.to_json() for invest_type in invest_types], status=200)
    return json_response(data='Investment types not found', status=404)

@app.route("/balance", methods=['GET'])
def get_balance():
    user_id = request.args.get('customer_id')
    if(user_id != None):
        balance = get_last_balance(user_id)
        if(balance != None):
            return json_response(data=balance.to_json(), status=200)
    return json_response(data='Customer\'s balance not found', status=404)
 

@app.route("/goal", methods=['POST', 'GET'])
def get_create_goal():
    if(request.method == 'POST'):
            content = request.get_json()
            goal=create_goal(content)
            return json_response(goal.to_json(), 201)
    else:
        goal_id = request.args.get('goal_id')
        if(goal_id != None):
            goal = get_goal(uuid.UUID(goal_id))
            if(goal != None):
                return json_response(
                    data=goal.to_json(), status=200)
    return json_response(data='Goal not found', status=404)


@app.route("/user-goals", methods=['GET'])
def user_goals():
    user_id = request.args.get('user_id')
    if(user_id != None):
        goals = get_user_goals(user_id)
        if(goals != None):
            return json_response(data=[goal.to_json() for goal in goals], status=200)
    return json_response(data='User goals not found', status=404)

@app.route("/goal-children", methods=['GET'])
def goal_children():
    goal_id = request.args.get('goal_id')
    if(goal_id != None):
        goals = get_goal_children(goal_id)
        if(goals != None):
            return json_response(data=[goal.to_json() for goal in goals], status=200)
    return json_response(data='Goals not found', status=404)

@app.route("/goal-type", methods=['POST', 'GET'])
def get_create_goal_type():
    if(request.method == 'POST'):
            content = request.get_json()
            goal_type=create_goal_type(content)
            return json_response(goal_type.to_json(), 201)
    else:
        goal_type_id = request.args.get('goal_type_id')
        if(goal_type_id != None):
            goal_type = get_goal_type(goal_type_id)
            if(goal_type != None):
                return json_response(data=goal_type.to_json(), status=200)
    return json_response(data='Goal type not found', status=404)


@app.route("/all-goal-types", methods=['GET'])
def get_goal_types():
    goal_types = get_all_goal_types()
    if(goal_types != None):
            return json_response(data=[goal_type.to_json() for goal_type in goal_types], status=200)
    return json_response(data='Goal types not found', status=404)

@app.route("/goal/<id>/deactivate", methods=["PATCH"])
def goal_deactivate(id:str):
    if(id != None):
        goal = deactivate_goal(uuid.UUID(id))
        if(goal != None):
            return json_response(data=goal.to_json(), status=200)
    return json_response(data='Goal not found', status=404)

@app.route("/goal/<id>/completion", methods=["GET"])
def goal_completion(id:str):
    if(id != None):
        completion = get_goal_completion(uuid.UUID(id))
        if(completion != None):
            return json_response(completion, status=200)
    return json_response(data='Goal not found', status=404)

@app.route("/goal/<id>/invested", methods=["GET"])
def goal_invested(id:str):
    if(id != None):
        invested = get_goal_total_invested(uuid.UUID(id))
        if(invested != None):
            return json_response(invested, status=200)
    return make_response(data='Goal not found', status=404)




if __name__ == '__main__':
    app.run(debug=True)
