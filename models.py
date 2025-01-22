from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    pto_balance = db.Column(db.Numeric(scale=2), nullable=False)

    base_payrate = db.Column(db.Numeric(scale=2), nullable=False)
    shift_diff_payrate = db.Column(db.Numeric(scale=2), nullable=False)
    benefits_cost = db.Column(db.Numeric(scale=2), nullable=False)
    retirement_cost = db.Column(db.Float, nullable=False)

    recurring_transactions = db.relationship("RecurringTransaction", backref="user")

    def __init__(self, name: str, username: str, password: str):
        self.name = name
        self.username = username

        self.pto_balance = float(0)
        self.base_payrate = float(0)
        self.shift_diff_payrate = float(0)
        self.benefits_cost = float(0)
        self.retirement_cost = float(0)

        self.set_password(password)

    def set_password(self, password):
        print(len(generate_password_hash("fuckface")))
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class RecurringTransaction(db.Model):
    __tablename__ = "recurring_transactions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(scale=2), nullable=False)
    day_of_month = db.Column(db.Integer, nullable=False)
    source = db.Column(db.Integer, nullable=False)
    is_credit = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(
        self,
        user: User,
        name: str,
        amount: float,
        day_of_month: int,
        is_credit: bool = False,
    ):
        self.user_id = user.id
        self.name = name
        self.amount = amount
        self.day_of_month = day_of_month
        self.source = 0
        self.is_credit = is_credit
