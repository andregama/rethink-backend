# from connect import start_session
from database.connect import start_session
# from schema import Customer
from database.schema import *
from typing import Dict, List, Tuple
from uuid import UUID
from decimal import Decimal

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

# def get_customers()->Tuple[Customer]:
#     customers = session.query(Customer).all()
#     return (customer.to_json() for customer in customers)

def get_customer(id: uuid)->Customer:
    if(id != None):
        return session.query(Customer).get(id)
    return None

# def create_customer(account_id: str, email:str, first_name:str, last_name:str,
# phone:str, address_cep:str, address_street:str, address_number:str,
# address_additional_details:str, address_city_area:str, address_city:str,
#  address_state:str)->Customer:
#     customer = Customer(account_id=account_id, email=email, first_name=first_name,
#     last_name=last_name, phone=phone, address_cep=address_cep,
#     address_street=address_street, address_number=address_number,
#     address_additional_details=address_additional_details, 
#     address_city_area=address_city_area, address_city=address_city,
#     address_state=address_state)
#     session.add(customer)
#     session.commit()
#     return customer

def create_customer(customer_data)->Customer:
    customer = Customer(**customer_data)
    session.add(customer)
    session.commit()
    return customer



def create_investment(customerId: UUID, investmentTypeId: int)->Investment:
    investment = Investment(customer_id=customerId, investment_type_id = investmentTypeId)
    session.add(investment)
    session.commit()
    return investment

def create_transaction(investment_id: UUID, amount:Decimal, goal_id:uuid=None)->Transaction:
    transaction = Transaction(investment_id=investment_id, amount=amount, goal_id = goal_id)
    session.add(investment)
    session.commit()
    return investment

def create_investment_type(title:str, description:str=None)->InvestmentType:
    invest_type = InvestmentType(title=title, description=description)
    session.add(invest_type)
    session.commit()
    return invest_type

def create_goal(customer_id:UUID, goal_type_id: int, title:str, amount:Decimal, parent_id:UUID=None,
 completed:bool=False, active:bool=True, description:str=None)-> Goal:
    goal = Goal(customer_id = customer_id, goal_type_id = goal_type_id, title=title,
    amount=amount, parent_id=parent_id, completed=completed, active=active,
    description=description)
    session.add(goal)
    session.commit()
    return goal

def create_goal_type(title:str, description:str=None, image:str=None)->GoalType:
    goal_type = GoalType(title=title, description=description, image=image)
    session.add(goal_type)
    session.commit()
    return goal_type

def complete_goal(goal_id:UUID):
    if(goal_id != None):
        goal:Goal = session.query(Goal).get(id)
        if(goal != None):
            goal.completed = True
            session.commit()

def deactivate_goal(goal_id:UUID):
    if(goal_id != None):
        goal:Goal = session.query(Goal).get(id)
        if(goal != None): 
            goal.active = False
            session.commit()






