# from connect import start_session
from database.connect import start_session
# from schema import *
from database.schema import *
from typing import Dict, List, Tuple
from uuid import UUID
from decimal import Decimal
from sqlalchemy import desc

from functools import wraps

session = start_session()

def session_committer(func):
    """Decorator to commit the DB session.

    Use this from high-level functions such as handler so that the session is always committed or
    closed.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            commit_session()

    return wrapper


def commit_session(_raise=True):
    if not session:
        return
    try:
        session.commit()
    except Exception:
        session.rollback()
        if _raise:
            raise

def get_customers()->Tuple[Customer]:
    customers = session.query(Customer).all()
    return [customer.to_json() for customer in customers]

def get_customer(id: UUID)->Customer:
    if(id != None):
        return session.query(Customer).get(id)
    return 

def create_customer(customer_data)->Customer:
    customer = Customer(**customer_data)
    session.add(customer)
    session.commit()
    return customer
    
def get_user_investments(user_id:UUID)->Tuple[Investment]:
    if(user_id != None):
        return session.query(Investment).\
            filter(Investment.customer_id == user_id).\
                all()
    return None

def create_investment(investment_data)->Investment:
    investment = Investment(**investment_data)
    session.add(investment)
    session.commit()
    return investment



def get_last_balance(user_id:UUID)->Balance:
    if(user_id != None):
        return session.query(Balance).\
                filter(Balance.customer_id == user_id).\
                    order_by(desc(Balance.date_time)).\
                        first()
    return None

def add_amount_to_balance(user_id:UUID, amount:Decimal)->Balance:
    user = get_customer(user_id)
    oldAmount=0
    if(user != None):
        balance=get_last_balance(user_id)
        if(balance != None):
            oldAmount=balance.amount
        newBalance=Balance(
            customer_id=user_id,
            amount=oldAmount+amount,
            balance_type="InterimAvailable")    
        session.add(newBalance)
        session.commit()
        return newBalance

def get_transactions(user_id:UUID)->Tuple[Transaction]:
    if(user_id != None):
        return session.query(Transaction).\
                filter(Transaction.customer_id == user_id).\
                    all()
    return None


def get_last_transactions(user_id:UUID, rows=5)->Tuple[Transaction]:
    if(user_id != None):
        return session.query(Transaction).\
                filter(Transaction.customer_id == user_id).\
                    limit(rows).\
                        all()
    return None

def get_transactions_by_investment(invest_id)->Tuple[Transaction]:
    if(invest_id != None):
        return session.query(Transaction).\
            filter(Transaction.investment_id == invest_id).\
                all()
    return None

def get_investment_invested_amount(invest_id)->Decimal:
    if(invest_id != None):
        investments = get_transactions_by_investment(invest_id)
        amount=0
        for investment in investments:
            amount += investment.amount
        return amount
    return None

def create_transaction(transaction_data)->Transaction:
    transaction = Transaction(**transaction_data)
    session.add(transaction)
    session.commit()
    return transaction

def get_investment_type(investment_type_id:int)->InvestmentType:
    return session.query(InvestmentType).\
        filter(InvestmentType.id == investment_type_id).\
            first()

def get_investment_types():
    return session.query(InvestmentType).all()

def create_investment_type(investment_type_data)->InvestmentType:
    invest_type = InvestmentType(**investment_type_data)
    session.add(invest_type)
    session.commit()
    return invest_type

def get_goal(goal_id: UUID):
    return session.query(Goal).\
        filter(Goal.id == goal_id).\
            first()

def get_user_goals(user_id:UUID):
    return session.query(Goal).\
        filter(Goal.customer_id == user_id).\
            all()

def get_goal_children(goal_id):
    return session.query(Goal).\
        filter(Goal.parent_id == goal_id).\
            all()

def create_goal(goal_data)-> Goal:
    goal = Goal(**goal_data)
    session.add(goal)
    session.commit()
    return goal

def get_all_goal_types()->Tuple[GoalType]:
    return session.query(GoalType).\
        all()

def get_goal_type(goal_type_id:int)->GoalType:
    return session.query(GoalType).\
        filter(GoalType.id == goal_type_id).\
            first()

def create_goal_type(goal_type_data)->GoalType:
    goal_type = GoalType(**goal_type_data)
    session.add(goal_type)
    session.commit()
    return goal_type

def get_goal_total_invested(goal_id:UUID)->Decimal:
    invested=0
    goal = get_goal(goal_id)
    if(goal != None):
        children = get_goal_children(goal_id)
        goals_ids = [child.id for child in children]
        goals_ids.append(goal_id)
        transactions = get_transactions(goal.customer_id)
        for transaction in transactions:
            if(transaction.goal_id in goals_ids):
                invested+=transaction.amount
    return invested

def get_goal_completion(goal_id:UUID)->Decimal:
    goal = get_goal(goal_id)
    invested=0
    if(goal != None):
        invested=get_goal_total_invested(goal_id)
        if(goal.amount > 0):
            return invested/goal.amount
    return 0


def complete_goal(goal_id:UUID)-> Goal:
    if(goal_id != None):
        goal:Goal = session.query(Goal).get(goal_id)
        if(goal != None):
            goal.completed = True
            session.commit()
            return goal
    return None

def deactivate_goal(goal_id:UUID)->Goal:
    if(goal_id != None):
        goal:Goal = session.query(Goal).get(id)
        if(goal != None): 
            goal.active = False
            session.commit()
            return goal
    return None







