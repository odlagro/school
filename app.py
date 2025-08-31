# app.py
from __future__ import annotations

import os
from datetime import datetime
from flask import Flask, render_template, render_template_string, url_for
from flask_login import login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db, login_manager, csrf


# =========================
# Configuração
# =========================
try:
    from config import Config as ExternalConfig  # type: ignore
except Exception:
    ExternalConfig = None


class FallbackConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///school.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


Config = ExternalConfig or FallbackConfig


# =========================
# Factory
# =========================
def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Reverse proxy (Railway/Render/Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # Models/Loader
    from models import User  # noqa: WPS433

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Helper: evita BuildError se endpoint ainda não existir
    def url_or_hash(endpoint: str, **values) -> str:
        from werkzeug.routing import BuildError
        try:
            return url_for(endpoint, **values)
        except BuildError:
            return "#"

    app.jinja_env.globals["url_or_hash"] = url_or_hash
    app.jinja_env.globals["now"] = datetime.utcnow

    # Registrar blueprints se existirem
    def _safe_register(import_path: str, bp_attr: str):
        try:
            mod = __import__(import_path, fromlist=[bp_attr])
            bp = getattr(mod, bp_attr)
            app.register_blueprint(bp)
        except Exception:
            pass

    _safe_register("auth", "auth_bp")
    _safe_register("users", "users_bp")
    _safe_register("cadastro", "cadastro_bp")

    # Rotas básicas
    @app.route("/")
    @login_required
    def home():
        try:
            return render_template("home.html")
        except Exception:
            return render_template_string(
                """
                {% extends "base.html" %}
                {% block title %}Início{% endblock %}
                {% block content %}
                  <div class="container mt-4">
                    <h2>Bem-vindo ao School</h2>
                    <p>Use o menu <strong>Cadastro</strong> para acessar as funcionalidades.</p>
                  </div>
                {% endblock %}
                """
            )

    # Criar tabelas + SEED do usuário padrão
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"db.create_all() falhou: {e}")

        # --------- SEED: usuário padrão Diretoria ----------
        try:
            from sqlalchemy import select

            default_email = "diretoria@school.com"
            existing = db.session.execute(
                select(User).filter_by(email=default_email)
            ).scalar_one_or_none()

            if existing is None:
                user = User(
                    email=default_email,
                    role="Diretoria",
                    is_active=True,
                )
                user.set_password("123456")  # senha padrão
                db.session.add(user)
                db.session.commit()
                app.logger.info(
                    "Usuário padrão criado: diretoria@school.com / 123456"
                )
            else:
                changed = False
                if existing.role != "Diretoria":
                    existing.role = "Diretoria"
                    changed = True
                if not existing.is_active:
                    existing.is_active = True
                    changed = True
                if changed:
                    db.session.commit()
                    app.logger.info("Usuário padrão ajustado (role/ativo).")
        except Exception as e:
            app.logger.warning(f"Seed do usuário padrão falhou: {e}")
        # ---------------------------------------------------

    return app


# =========================
# Execução local
# =========================
app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=True,
    )
