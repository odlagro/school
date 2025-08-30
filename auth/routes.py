# school/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from . import auth_bp
from .forms import (
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
)
from .utils import generate_reset_token, verify_reset_token, roles_required
from extensions import db
from models import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login realizado com sucesso!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("index"))
        flash("Email ou senha inválidos.", "danger")
    return render_template("login.html", form=form)


# Cadastro de usuário: APENAS Diretoria e APÓS login
@auth_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@roles_required("Diretoria")
def create_user():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Já existe um usuário com este email.", "warning")
            return render_template("register.html", form=form)

        user = User(
            email=email,
            name=form.name.data.strip() if form.name.data else None,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("index"))
    return render_template("register.html", form=form)


# Rota antiga pública -> redireciona para login
@auth_bp.route("/register")
def legacy_register_redirect():
    flash("Criação de conta disponível apenas para Diretoria, após login.", "warning")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Se o email existir, enviaremos instruções de redefinição.", "info")
            return redirect(url_for("auth.login"))

        token = generate_reset_token(email)
        reset_link = url_for("auth.reset_password", token=token, _external=True)
        print(f"[School] Link de redefinição para {email}: {reset_link}")
        flash("Enviamos o link de redefinição (simulado).", "success")
        flash(f"Link: {reset_link}", "secondary")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    email = verify_reset_token(token)
    if not email:
        flash("Token inválido ou expirado.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user.set_password(form.password.data)
        db.session.commit()
        flash("Senha redefinida com sucesso. Faça login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", form=form)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Senha atual incorreta.", "danger")
            return render_template("change_password.html", form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Senha alterada com sucesso!", "success")
        return redirect(url_for("index"))
    return render_template("change_password.html", form=form)
