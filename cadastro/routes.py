from functools import wraps
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from . import cadastro_bp
from .forms import UsuarioForm, HorarioForm, MensalidadeForm
from models import db, User, Horario, Mensalidade, ROLE_DIRETORIA


def diretoria_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != ROLE_DIRETORIA:
            abort(403)
        return view(*args, **kwargs)
    return wrapper


# ===========================
# Usuários
# ===========================

@cadastro_bp.route("/usuarios")
@login_required
def usuarios_list():
    usuarios = User.query.order_by(User.email.asc()).all()
    return render_template("usuarios_list.html", usuarios=usuarios)


@cadastro_bp.route("/usuarios/novo", methods=["GET", "POST"])
@login_required
@diretoria_required
def usuarios_create():
    form = UsuarioForm()
    if form.validate_on_submit():
        try:
            user = User(
                email=form.email.data.strip(),
                role=form.role.data,
                active=form.active.data is True,
            )
            if form.password.data:
                user.set_password(form.password.data)
            else:
                # senha padrão se não informar
                user.set_password("123456")
            db.session.add(user)
            db.session.commit()
            flash("Usuário criado com sucesso.", "success")
            return redirect(url_for("cadastro.usuarios_list"))
        except SQLAlchemyError as exc:
            db.session.rollback()
            flash(f"Erro ao criar usuário: {exc}", "danger")
    return render_template("usuarios_form.html", form=form, titulo="Incluir Usuário")


@cadastro_bp.route("/usuarios/<int:user_id>/editar", methods=["GET", "POST"])
@login_required
@diretoria_required
def usuarios_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UsuarioForm(obj=user)
    if form.validate_on_submit():
        try:
            user.email = form.email.data.strip()
            user.role = form.role.data
            user.active = form.active.data is True
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            flash("Usuário atualizado com sucesso.", "success")
            return redirect(url_for("cadastro.usuarios_list"))
        except SQLAlchemyError as exc:
            db.session.rollback()
            flash(f"Erro ao atualizar usuário: {exc}", "danger")
    return render_template("usuarios_form.html", form=form, titulo="Editar Usuário")


@cadastro_bp.route("/usuarios/<int:user_id>/excluir", methods=["POST"])
@login_required
@diretoria_required
def usuarios_delete(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash("Usuário excluído com sucesso.", "success")
    except SQLAlchemyError as exc:
        db.session.rollback()
        flash(f"Erro ao excluir usuário: {exc}", "danger")
    return redirect(url_for("cadastro.usuarios_list"))


# ===========================
# Horários
# ===========================

@cadastro_bp.route("/horarios")
@login_required
def horarios_list():
    itens = Horario.query.order_by(Horario.hora_inicio.asc()).all()
    return render_template("horarios_list.html", itens=itens)


@cadastro_bp.route("/horarios/novo", methods=["GET", "POST"])
@login_required
@diretoria_required
def horarios_create():
    form = HorarioForm()
    if form.validate_on_submit():
        try:
            h = Horario(hora_inicio=form.hora_inicio.data, hora_fim=form.hora_fim.data)
            db.session.add(h)
            db.session.commit()
            flash("Horário incluído com sucesso.", "success")
            return redirect(url_for("cadastro.horarios_list"))
        except SQLAlchemyError as exc:
            db.session.rollback()
            flash(f"Erro ao incluir horário: {exc}", "danger")
    return render_template("horarios_form.html", form=form, titulo="Incluir Horário")


@cadastro_bp.route("/horarios/<int:item_id>/editar", methods=["GET", "POST"])
@login_required
@diretoria_required
def horarios_edit(item_id):
    h = Horario.query.get_or_404(item_id)
    form = HorarioForm(obj=h)
    if form.validate_on_submit():
        try:
            h.hora_inicio = form.hora_inicio.data
            h.hora_fim = form.hora_fim.data
            db.session.commit()
            flash("Horário atualizado com sucesso.", "success")
            return redirect(url_for("cadastro.horarios_list"))
        except SQLAlchemyError as exc:
            db.session.rollback()
            flash(f"Erro ao atualizar horário: {exc}", "danger")
    return render_template("horarios_form.html", form=form, titulo="Editar Horário")


@cadastro_bp.route("/horarios/<int:item_id>/excluir", methods=["POST"])
@login_required
@diretoria_required
def horarios_delete(item_id):
    h = Horario.query.get_or_404(item_id)
    try:
        db.session.delete(h)
        db.session.commit()
        flash("Horário excluído com sucesso.", "success")
    except SQLAlchemyError as exc:
        db.session.rollback()
        flash(f"Erro ao excluir horário: {exc}", "danger")
    return redirect(url_for("cadastro.horarios_list"))


# ===========================
# Mensalidades
# ===========================

@cadastro_bp.route("/mensalidades")
@login_required
def mensalidades_list():
    itens = Mensalidade.query.order_by(Mensalidade.serie.asc()).all()
    return render_template("mensalidades_list.html", itens=itens)


@cadastro_bp.route("/mensalidades/novo", methods=["GET", "POST"])
@login_required
@diretoria_required
def mensalidades_create():
    form = MensalidadeForm()
    if form.validate_on_submit():
        try:
            m = Mensalidade(serie=form.serie.data.strip(), valor=form.valor.data)
            db.session.add(m)
            db.session.commit()
            flash("Mensalidade incluída com sucesso.", "success")
            return redirect(url_for("cadastro.mensalidades_list"))
        except SQLAlchemyError as exc:
            db.session.rollback()
            flash(f"Erro ao incluir mensalidade: {exc}", "danger")
    return render_template("mensalidades_form.html", form=form, titulo="Incluir Mensalidade")


@cadastro_bp.route("/mensalidades/<int:item_id>/editar", methods=["GET", "POST"])
@login_required
@diretoria_required
def mensalidades_edit(item_id):
    m = Mensalidade.query.get_or_404(item_id)
    form = MensalidadeForm(obj=m)
    if form.validate_on_submit():
        try:
            m.serie = form.serie.data.strip()
            m.valor = form.valor.data
            db.session.commit()
            flash("Mensalidade atualizada com sucesso.", "success")
            return redirect(url_for("cadastro.mensalidades_list"))
        except SQLAlchemyError as exc:
            db.session.rollback()
            flash(f"Erro ao atualizar mensalidade: {exc}", "danger")
    return render_template("mensalidades_form.html", form=form, titulo="Editar Mensalidade")


@cadastro_bp.route("/mensalidades/<int:item_id>/excluir", methods=["POST"])
@login_required
@diretoria_required
def mensalidades_delete(item_id):
    m = Mensalidade.query.get_or_404(item_id)
    try:
        db.session.delete(m)
        db.session.commit()
        flash("Mensalidade excluída com sucesso.", "success")
    except SQLAlchemyError as exc:
        db.session.rollback()
        flash(f"Erro ao excluir mensalidade: {exc}", "danger")
    return redirect(url_for("cadastro.mensalidades_list"))
