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

    paycheck_calculator_configs = db.relationship(
        "PaycheckCalculatorConfig", backref="user"
    )

    def __init__(self, name: str, username: str, password: str):
        self.name = name
        self.username = username

        self.set_password(password)

    def set_password(self, password):
        print(len(generate_password_hash("fuckface")))
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PaycheckCalculatorConfig(db.Model):
    __tablename__ = "paycalcconfigs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    base_payrate = db.Column(db.Numeric(scale=2), nullable=False)
    shift_diff_payrate = db.Column(db.Numeric(scale=2), nullable=False)
    base_hours = db.Column(db.Float, nullable=False)
    shift_diff_hours = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(
        self,
        user: User,
        name: str,
        base_pay: float,
        shift_diff_pay: float,
        base_hours: float,
        shift_diff_hours: float,
    ):
        self.name = name
        self.base_payrate = base_pay
        self.shift_diff_payrate = shift_diff_pay
        self.base_hours = base_hours
        self.shift_diff_hours = shift_diff_hours
        self.user_id = user.id
