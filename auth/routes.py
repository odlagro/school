from urllib.parse import urlparse, urljoin
from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user
from extensions import db
from . import auth_bp
from .forms import LoginForm
from models import User

def _is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ("http", "https")) and (ref_url.netloc == test_url.netloc)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # NÃO proteger essa rota com @login_required
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(form.password.data):
            flash("Credenciais inválidas.", "danger")
            return render_template("login.html", form=form), 401

        if not user.active:
            flash("Usuário inativo. Procure a Diretoria.", "warning")
            return render_template("login.html", form=form), 403

        login_user(user, remember=form.remember.data)
        next_url = request.args.get("next")
        if _is_safe_url(next_url):
            return redirect(next_url)
        return redirect(url_for("index"))

    return render_template("login.html", form=form)

@auth_bp.route("/logout", methods=["GET"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("auth.login"))
