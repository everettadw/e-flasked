from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, login_required, current_user
from flask_wtf import CSRFProtect
from models import *
import tomlkit

from blueprints.paycheck_calculator import pay_calc_bp
from blueprints.auth import auth_bp


app = Flask(__name__)
app.config.from_file("flask_config.toml", tomlkit.load)

db.init_app(app)
csrf = CSRFProtect(app)

app.register_blueprint(pay_calc_bp)
app.register_blueprint(auth_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login_get"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/testing")
def testing():
    return render_template("testing.html")


@app.get("/transactions")
@login_required
def get_transactions():
    return render_template("transactions.html")


@app.post("/transactions")
@login_required
def post_transactions():
    new_transaction = RecurringTransaction(
        current_user,
        request.json.get("name"),
        float(request.json.get("amount")),
        int(request.json.get("day_of_month")),
        bool(request.json.get("is_credit")),
    )
    db.session.add(new_transaction)
    db.session.commit()

    resJson = {
        "name": request.json.get("name"),
        "amount": request.json.get("amount"),
        "day_of_month": request.json.get("day_of_month"),
        "is_credit": request.json.get("is_credit"),
    }
    return {"transaction": resJson}, 200


@app.delete("/transactions")
@login_required
def delete_transactions():
    if request.json.get("name") != None and request.json.get("amount") != None:
        transactions = RecurringTransaction.query.filter_by(
            user_id=current_user.id,
            name=request.json.get("name"),
            amount=float(request.json.get("amount")),
        ).delete()
    else:
        RecurringTransaction.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return {}, 200


@app.put("/transactions")
@login_required
def update_transactions():
    updated_transaction = RecurringTransaction.query.filter_by(
        user_id=current_user.id,
        name=request.json.get("old_name"),
        amount=float(request.json.get("old_amount")),
    ).update(
        {
            RecurringTransaction.name: request.json.get("name"),
            RecurringTransaction.amount: float(request.json.get("amount")),
            RecurringTransaction.day_of_month: int(request.json.get("day_of_month")),
            RecurringTransaction.is_credit: bool(request.json.get("is_credit")),
        }
    )

    db.session.commit()

    resJson = {
        "old_name": request.json.get("old_name"),
        "name": request.json.get("name"),
        "amount": request.json.get("amount"),
        "day_of_month": request.json.get("day_of_month"),
        "is_credit": request.json.get("is_credit"),
    }

    return {"transaction": resJson}, 200
