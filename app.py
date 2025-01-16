from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
import tomlkit

from blueprints.paycheck_calculator import pay_calc_bp
from blueprints.auth import auth_bp


app = Flask(__name__)
app.config.from_file("flask_config.toml", tomlkit.load)

app.register_blueprint(pay_calc_bp)
app.register_blueprint(auth_bp)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    return render_template("index.html")
