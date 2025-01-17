from flask import Blueprint, redirect
from flask_login import login_user, logout_user
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    the_user = User.query.filter_by(username="everettdw").first()
    login_user(the_user, remember=True)
    return redirect("/")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect("/")
