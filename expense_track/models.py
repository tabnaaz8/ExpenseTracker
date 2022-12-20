from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable = False)
    username = db.Column(db.String(20), unique=True, nullable = False)
    password = db.Column(db.String(20),nullable = False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now(),nullable = False)
    budgets = db.relationship('Budget', backref='user', passive_deletes=True)
    expenses = db.relationship('Expense', backref='user', passive_deletes=True)


class Budget(db.Model):
    budget_id = db.Column(db.Integer, primary_key= True)
    month = db.Column(db.String(20), nullable = False)
    year = db.Column(db.String(20), nullable = False)
    amount = db.Column(db.Float, nullable = False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)


class Expense(db.Model):
    expense_id = db.Column(db.Integer, primary_key=True)
    expense_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable = False)
    comments = db.Column(db.String(100),nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    budget = db.Column(db.Integer, db.ForeignKey('budget.budget_id', ondelete="CASCADE"), nullable=False)
    #date_created = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)

