# auth/home_view.py
from flask import render_template
from flask_login import login_required
from . import auth_bp

@auth_bp.route("/home", endpoint="home")
@login_required
def home():
    # Renderiza a sua home. Se já tiver um template próprio, troque o nome abaixo.
    return render_template("home.html")
