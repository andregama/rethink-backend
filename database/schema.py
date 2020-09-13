import re
from datetime import datetime
import enum
# from connect import *
from database.connect import *
# from mybaseclass import MyBase
from database.mybaseclass import MyBase
import uuid
import simplejson as json


# from mybaseclass import MyBase
from sqlalchemy import (Boolean, Column, DateTime, Time, ForeignKey, Integer, String, Numeric,
                        Table, Text, event, Enum, SmallInteger)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
# from sqlalchemy_utils import EmailType

Base = declarative_base(cls=MyBase)

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    account_id = Column(String(15), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(100))
    phone = Column(String(50))
    address_cep = Column(String(10))
    address_street = Column(String(200))
    address_number = Column(String(10))
    address_additional_details = Column(String(200))
    address_city_area = Column(String(100))
    address_city = Column(String(45))
    address_state = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow), 

    def to_json(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "account_id": self.account_id
        }

class GoalType(Base):
    __tablename__ = 'goal_type'

    id = Column(Integer, primary_key=True)
    title =  Column(String(50), nullable=False, unique=True)
    description = Column(String(100))
    image = Column(String(150))

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image": self.image
        }


class Goal(Base):
    __tablename__ = 'goal'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('goal.id'))
    parent = relationship('Goal', remote_side=id, backref='sub_goal')
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship('Customer', backref=backref ("goal", lazy="joined"))
    goal_type_id = Column(Integer, ForeignKey('goal_type.id'))
    goal_type = relationship('GoalType', backref=backref("goal", lazy="joined"))
    title = Column(String(100), nullable=False)
    amount = Column(Numeric, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    description = Column(String(200))

    def to_json(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "customer_id": self.customer_id,
            "goal_type_id": self.goal_type_id,
            "title": self.title,
            "amount": self.amount,
            "completed": self.completed,
            "active": self.active,
            "description": self.description
        }


class InvestmentType(Base):
    __tablename__ = 'investment_type'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(200))

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description
        }

class Investment(Base):
    __tablename__ = 'investment'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship('Customer', backref=backref ("investment", lazy="joined"))
    investment_type_id = Column(Integer, ForeignKey('investment_type.id'))
    investment_type = relationship('InvestmentType', backref=backref("investment", lazy="joined"))

    def to_json(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "investment_type_id": self.investment_type_id
        }


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship('Customer', backref=backref ("transaction", lazy="joined"))
    investment_id = Column(UUID(as_uuid=True), ForeignKey('investment.id'))
    investment = relationship('Investment', backref=backref ("transactions", lazy="joined"))
    amount = Column(Numeric, nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey('goal.id'))
    goal = relationship('Goal', backref=backref ("transactions", lazy="joined"))

    def to_json(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "investment_id": self.investment_id,
            "amount": self.amount,
            "goal_id": self.goal_id
        }

class Balance(Base):
    __tablename__ = 'balance'
    
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship('Customer', backref=backref ("balance", lazy="joined"))
    amount = Column(Numeric, nullable=False)
    balance_type = Column(String(50), nullable=False)
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "amount": self.amount,
            "balance_type": self.balance_type,
            "date_time": self.date_time
        }

