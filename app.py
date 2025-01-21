from flask import Flask, redirect, render_template
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_wtf import CSRFProtect
from models import *
import tomlkit

from blueprints.paycheck_calculator import pay_calc_bp, pay_calc_api_bp
from blueprints.auth import auth_bp


app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.exempt(pay_calc_api_bp)
app.config.from_file("flask_config.toml", tomlkit.load)

app.register_blueprint(pay_calc_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(pay_calc_api_bp)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login_get"

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/testing")
def testing():
    return render_template("css-testing.html")


@app.route("/pccs")
@login_required
def get_pccs():
    return render_template("pccs.html", pccs=current_user.paycheck_calculator_configs)


@app.route("/creu")
def create_user():
    new_user = User("Everett", "everettdw", "benten")
    db.session.add(new_user)
    db.session.commit()
    return redirect("/login")


@app.route("/pccs/<pcc_name>")
@login_required
def create_paycheck_calc_config(pcc_name):
    new_pcc = PaycheckCalculatorConfig(current_user, pcc_name, 46.5, 2.0, 80, 80)
    db.session.add(new_pcc)
    db.session.commit()
    return redirect("/pccs")
