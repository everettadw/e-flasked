from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, login_required, current_user
from flask_wtf import CSRFProtect
from models import *
import tomlkit

from blueprints.paycheck_calculator import pay_calc_bp, pay_calc_api_bp
from blueprints.auth import auth_bp


app = Flask(__name__)
app.config.from_file("flask_config.toml", tomlkit.load)

csrf = CSRFProtect(app)
csrf.exempt(pay_calc_api_bp)

app.register_blueprint(pay_calc_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(pay_calc_api_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login_get"

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/testing")
def testing():
    return render_template("testing.html")


@app.get("/expenses")
@login_required
def get_expenses():
    return render_template("expenses.html")


@app.post("/expenses")
def post_expenses():
    new_expense = Expense(
        request.form.get("name"),
        float(request.form.get("amount")),
        int(request.form.get("day_of_month")),
        int(request.form.get("payment_source")),
        user=current_user,
    )
    db.session.add(new_expense)
    db.session.commit()
    return render_template("expenses.html")
