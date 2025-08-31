# users/routes.py
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import select
from extensions import db
from models import User
from .forms import UserCreateForm, UserEditForm, PasswordChangeForm, DeleteForm
from . import users_bp
from auth.utils import roles_required  # já existente no seu projeto (Diretoria-only)

@users_bp.get("/")
@login_required
@roles_required("Diretoria")
def list_users():
    users = db.session.scalars(select(User).order_by(User.created_at.desc())).all()
    delete_form = DeleteForm()
    return render_template("users/list.html", users=users, delete_form=delete_form)

@users_bp.route("/create", methods=["GET", "POST"])
@login_required
@roles_required("Diretoria")
def create_user():
    form = UserCreateForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User(email=email, role=form.role.data, is_active=True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Usuário criado com sucesso.", "success")
        return redirect(url_for("users.list_users"))
    return render_template("users/create.html", form=form)

@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("Diretoria")
def edit_user(user_id):
    user = db.session.get(User, user_id) or abort(404)
    form = UserEditForm(original_email=user.email, obj=user)
    if form.validate_on_submit():
        # Mantemos email como eventual atualização validada; no template deixamos readonly
        user.email = form.email.data.strip().lower()
        user.role = form.role.data
        user.is_active = bool(form.is_active.data)
        db.session.commit()
        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for("users.list_users"))
    # Preenche defaults
    form.email.data = user.email
    form.role.data = user.role
    form.is_active.data = user.is_active
    return render_template("users/edit.html", form=form, user=user)

@users_bp.post("/<int:user_id>/delete")
@login_required
@roles_required("Diretoria")
def delete_user(user_id):
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400, description="CSRF inválido.")
    user = db.session.get(User, user_id) or abort(404)
    if user.id == current_user.id:
        flash("Você não pode excluir a si mesmo.", "warning")
        return redirect(url_for("users.list_users"))
    db.session.delete(user)
    db.session.commit()
    flash("Usuário excluído com sucesso.", "success")
    return redirect(url_for("users.list_users"))

@users_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Senha atual incorreta.", "danger")
            return render_template("users/change_password.html", form=form)
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Senha atualizada com sucesso.", "success")
        return redirect(url_for("home"))  # ajusta para sua rota de home
    return render_template("users/change_password.html", form=form)
