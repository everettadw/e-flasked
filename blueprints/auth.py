from flask import Blueprint, render_template, session, request

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    return render_template()
