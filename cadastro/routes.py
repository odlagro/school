# cadastro/routes.py
from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import cadastro_bp
from extensions import db
from models import User, Horario, Mensalidade, ROLE_DIRETORIA

# ---- helpers de permissão ----
def diretoria_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Você precisa estar autenticado.", "warning")
            return redirect(url_for("auth.login"))
        if current_user.role != ROLE_DIRETORIA:
            flash("Acesso restrito à Diretoria.", "warning")
            return redirect(url_for("auth.home"))
        return fn(*args, **kwargs)
    return wrapper

# =========================
# Usuários
# =========================
@cadastro_bp.route("/usuarios", endpoint="usuarios_list")
@cadastro_bp.route("/usuarios/lista")
@login_required
def usuarios_list():
    q = request.args.get("q", "").strip()
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter((User.name.ilike(like)) | (User.email.ilike(like)))
    usuarios = query.order_by(User.name.asc()).all()
    return render_template("cadastro/usuarios_list.html", usuarios=usuarios, q=q)

@cadastro_bp.route("/usuarios/novo", methods=["GET", "POST"], endpoint="usuarios_incluir")
@cadastro_bp.route("/usuarios/incluir", methods=["GET", "POST"])
@login_required
@diretoria_required
def usuarios_incluir():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", ROLE_COLABORADOR).strip() if request.form.get("role") else ROLE_DIRETORIA if request.form.get("role") == ROLE_DIRETORIA else "Colaborador"
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            flash("Preencha nome, e-mail e senha.", "warning")
            return redirect(url_for("cadastro.usuarios_incluir"))

        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "warning")
            return redirect(url_for("cadastro.usuarios_incluir"))

        u = User(name=name, email=email, role=role or "Colaborador", is_active=True)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash("Usuário criado com sucesso.", "success")
        return redirect(url_for("cadastro.usuarios_list"))

    return render_template("cadastro/usuarios_form.html", modo="incluir")

@cadastro_bp.route("/usuarios/<int:user_id>/editar", methods=["GET", "POST"], endpoint="usuarios_editar")
@login_required
@diretoria_required
def usuarios_editar(user_id: int):
    u = User.query.get_or_404(user_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", u.role).strip()
        is_active = request.form.get("is_active") == "on"

        if not name or not email:
            flash("Preencha nome e e-mail.", "warning")
            return redirect(url_for("cadastro.usuarios_editar", user_id=user_id))

        if User.query.filter(User.email == email, User.id != u.id).first():
            flash("E-mail já em uso por outro usuário.", "warning")
            return redirect(url_for("cadastro.usuarios_editar", user_id=user_id))

        u.name = name
        u.email = email
        u.role = role
        u.is_active = is_active

        new_password = request.form.get("password", "").strip()
        if new_password:
            u.set_password(new_password)

        db.session.commit()
        flash("Usuário atualizado.", "success")
        return redirect(url_for("cadastro.usuarios_list"))

    return render_template("cadastro/usuarios_form.html", modo="editar", usuario=u)

@cadastro_bp.route("/usuarios/<int:user_id>/excluir", methods=["POST"], endpoint="usuarios_excluir")
@login_required
@diretoria_required
def usuarios_excluir(user_id: int):
    u = User.query.get_or_404(user_id)
    if u.email.lower() == "diretoria@school.com":
        flash("O usuário padrão não pode ser excluído.", "warning")
        return redirect(url_for("cadastro.usuarios_list"))
    db.session.delete(u)
    db.session.commit()
    flash("Usuário excluído.", "success")
    return redirect(url_for("cadastro.usuarios_list"))

# =========================
# Horários
# =========================
@cadastro_bp.route("/horarios", endpoint="horarios_list")
@cadastro_bp.route("/horarios/lista")
@login_required
def horarios_list():
    horarios = Horario.query.order_by(Horario.hora_inicio.asc()).all()
    return render_template("cadastro/horarios_list.html", horarios=horarios)

@cadastro_bp.route("/horarios/novo", methods=["GET", "POST"], endpoint="horarios_incluir")
@cadastro_bp.route("/horarios/incluir", methods=["GET", "POST"])
@login_required
@diretoria_required
def horarios_incluir():
    if request.method == "POST":
        h_ini = request.form.get("hora_inicio", "").strip()
        h_fim = request.form.get("hora_fim", "").strip()

        if not h_ini or not h_fim:
            flash("Preencha Hora início e Hora fim.", "warning")
            return redirect(url_for("cadastro.horarios_incluir"))

        h = Horario(hora_inicio=h_ini, hora_fim=h_fim)
        db.session.add(h)
        db.session.commit()
        flash("Horário criado.", "success")
        return redirect(url_for("cadastro.horarios_list"))

    return render_template("cadastro/horarios_form.html", modo="incluir")

@cadastro_bp.route("/horarios/<int:hid>/editar", methods=["GET", "POST"], endpoint="horarios_editar")
@login_required
@diretoria_required
def horarios_editar(hid: int):
    h = Horario.query.get_or_404(hid)
    if request.method == "POST":
        h_ini = request.form.get("hora_inicio", "").strip()
        h_fim = request.form.get("hora_fim", "").strip()

        if not h_ini or not h_fim:
            flash("Preencha Hora início e Hora fim.", "warning")
            return redirect(url_for("cadastro.horarios_editar", hid=hid))

        h.hora_inicio = h_ini
        h.hora_fim = h_fim
        db.session.commit()
        flash("Horário atualizado.", "success")
        return redirect(url_for("cadastro.horarios_list"))

    return render_template("cadastro/horarios_form.html", modo="editar", horario=h)

@cadastro_bp.route("/horarios/<int:hid>/excluir", methods=["POST"], endpoint="horarios_excluir")
@login_required
@diretoria_required
def horarios_excluir(hid: int):
    h = Horario.query.get_or_404(hid)
    db.session.delete(h)
    db.session.commit()
    flash("Horário excluído.", "success")
    return redirect(url_for("cadastro.horarios_list"))

# =========================
# Mensalidades
# =========================
@cadastro_bp.route("/mensalidades", endpoint="mensalidade_list")
@cadastro_bp.route("/mensalidades/lista")
@login_required
def mensalidade_list():
    itens = Mensalidade.query.order_by(Mensalidade.serie.asc()).all()
    return render_template("cadastro/mensalidade_list.html", mensalidades=itens)

@cadastro_bp.route("/mensalidades/novo", methods=["GET", "POST"], endpoint="mensalidade_incluir")
@cadastro_bp.route("/mensalidades/incluir", methods=["GET", "POST"])
@login_required
@diretoria_required
def mensalidade_incluir():
    if request.method == "POST":
        serie = request.form.get("serie", "").strip()
        valor_str = request.form.get("valor", "").strip().replace(",", ".")
        if not serie or not valor_str:
            flash("Preencha Série e Valor.", "warning")
            return redirect(url_for("cadastro.mensalidade_incluir"))

        try:
            # Numeric(10,2) aceita Decimal; converter string para Decimal
            from decimal import Decimal
            valor = Decimal(valor_str)
        except Exception:
            flash("Valor inválido.", "warning")
            return redirect(url_for("cadastro.mensalidade_incluir"))

        m = Mensalidade(serie=serie, valor=valor)
        db.session.add(m)
        db.session.commit()
        flash("Mensalidade criada.", "success")
        return redirect(url_for("cadastro.mensalidade_list"))

    return render_template("cadastro/mensalidade_form.html", modo="incluir")

@cadastro_bp.route("/mensalidades/<int:mid>/editar", methods=["GET", "POST"], endpoint="mensalidade_editar")
@login_required
@diretoria_required
def mensalidade_editar(mid: int):
    m = Mensalidade.query.get_or_404(mid)
    if request.method == "POST":
        serie = request.form.get("serie", "").strip()
        valor_str = request.form.get("valor", "").strip().replace(",", ".")
        if not serie or not valor_str:
            flash("Preencha Série e Valor.", "warning")
            return redirect(url_for("cadastro.mensalidade_editar", mid=mid))

        try:
            from decimal import Decimal
            valor = Decimal(valor_str)
        except Exception:
            flash("Valor inválido.", "warning")
            return redirect(url_for("cadastro.mensalidade_editar", mid=mid))

        m.serie = serie
        m.valor = valor
        db.session.commit()
        flash("Mensalidade atualizada.", "success")
        return redirect(url_for("cadastro.mensalidade_list"))

    return render_template("cadastro/mensalidade_form.html", modo="editar", mensalidade=m)

@cadastro_bp.route("/mensalidades/<int:mid>/excluir", methods=["POST"], endpoint="mensalidade_excluir")
@login_required
@diretoria_required
def mensalidade_excluir(mid: int):
    m = Mensalidade.query.get_or_404(mid)
    db.session.delete(m)
    db.session.commit()
    flash("Mensalidade excluída.", "success")
    return redirect(url_for("cadastro.mensalidade_list"))
