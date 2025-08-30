# school/cadastro/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from . import cadastro_bp
from .forms import HorarioForm, MensalidadeForm, DeleteForm
from extensions import db
from models import Horario, Mensalidade
from auth.utils import roles_required


# ----------------------
# HORÁRIOS
# ----------------------
@cadastro_bp.route("/horarios")
@login_required
def horarios_list():
    qs = Horario.query.order_by(Horario.hora_inicio.asc()).all()
    delete_form = DeleteForm()
    return render_template("cadastro/horarios_list.html", items=qs, delete_form=delete_form)


@cadastro_bp.route("/horarios/novo", methods=["GET", "POST"])
@login_required
@roles_required("Diretoria")
def horarios_new():
    form = HorarioForm()
    if form.validate_on_submit():
        item = Horario(hora_inicio=form.hora_inicio.data, hora_fim=form.hora_fim.data)
        db.session.add(item)
        db.session.commit()
        flash("Horário criado com sucesso!", "success")
        return redirect(url_for("cadastro.horarios_list"))
    return render_template("cadastro/horario_form.html", form=form, title="Novo Horário")


@cadastro_bp.route("/horarios/<int:item_id>/editar", methods=["GET", "POST"])
@login_required
@roles_required("Diretoria")
def horarios_edit(item_id: int):
    item = Horario.query.get_or_404(item_id)
    form = HorarioForm(obj=item)
    if form.validate_on_submit():
        item.hora_inicio = form.hora_inicio.data
        item.hora_fim = form.hora_fim.data
        db.session.commit()
        flash("Horário atualizado com sucesso!", "success")
        return redirect(url_for("cadastro.horarios_list"))
    return render_template("cadastro/horario_form.html", form=form, title="Editar Horário")


@cadastro_bp.route("/horarios/<int:item_id>/excluir", methods=["POST"])
@login_required
@roles_required("Diretoria")
def horarios_delete(item_id: int):
    item = Horario.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Horário excluído com sucesso!", "success")
    return redirect(url_for("cadastro.horarios_list"))


# ----------------------
# MENSALIDADES
# ----------------------
@cadastro_bp.route("/mensalidades")
@login_required
def mensalidades_list():
    qs = Mensalidade.query.order_by(Mensalidade.serie.asc()).all()
    delete_form = DeleteForm()
    return render_template("cadastro/mensalidades_list.html", items=qs, delete_form=delete_form)


@cadastro_bp.route("/mensalidades/nova", methods=["GET", "POST"])
@login_required
@roles_required("Diretoria")
def mensalidades_new():
    form = MensalidadeForm()
    if form.validate_on_submit():
        item = Mensalidade(serie=form.serie.data.strip(), valor=form.valor.data)
        db.session.add(item)
        db.session.commit()
        flash("Mensalidade criada com sucesso!", "success")
        return redirect(url_for("cadastro.mensalidades_list"))
    return render_template("cadastro/mensalidade_form.html", form=form, title="Nova Mensalidade")


@cadastro_bp.route("/mensalidades/<int:item_id>/editar", methods=["GET", "POST"])
@login_required
@roles_required("Diretoria")
def mensalidades_edit(item_id: int):
    item = Mensalidade.query.get_or_404(item_id)
    form = MensalidadeForm(obj=item)
    if form.validate_on_submit():
        item.serie = form.serie.data.strip()
        item.valor = form.valor.data
        db.session.commit()
        flash("Mensalidade atualizada com sucesso!", "success")
        return redirect(url_for("cadastro.mensalidades_list"))
    return render_template("cadastro/mensalidade_form.html", form=form, title="Editar Mensalidade")


@cadastro_bp.route("/mensalidades/<int:item_id>/excluir", methods=["POST"])
@login_required
@roles_required("Diretoria")
def mensalidades_delete(item_id: int):
    item = Mensalidade.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Mensalidade excluída com sucesso!", "success")
    return redirect(url_for("cadastro.mensalidades_list"))
