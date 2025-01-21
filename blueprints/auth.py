from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login_get():
    if current_user != None and current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("login.html")


@auth_bp.post("/login")
def login_post():
    user = User.query.filter_by(username=request.form.get("username")).first()
    if user != None and user.check_password(request.form.get("password")):
        login_user(user=user)
        return redirect(url_for("index"))
    flash("Incorrect username or password.")
    return render_template("login.html")


@auth_bp.get("/register")
def register_get():
    if current_user != None and current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("register.html")


@auth_bp.post("/register")
def register_post():
    user = User.query.filter_by(username=request.form.get("username")).first()
    if user != None:
        flash("That username is already taken - choose another one...")
    else:
        if request.form.get("password") == request.form.get("confirm_password"):
            new_user = User(
                request.form.get("name"),
                request.form.get("username"),
                request.form.get("password"),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("index"))
        else:
            flash("Passwords don't match...")
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
