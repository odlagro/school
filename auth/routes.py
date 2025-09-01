# auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# ... imports que você já tem

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # sua lógica atual de login...
    # após sucesso:
    next_url = request.args.get("next")
    return redirect(next_url or url_for("auth.home"))

@auth_bp.route("/home")
@login_required
def home():
    # Mostra o dashboard / menus
    return render_template("home.html")
