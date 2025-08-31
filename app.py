# app.py
from __future__ import annotations

import os
from datetime import datetime
from flask import Flask, render_template, render_template_string, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

# Extensões compartilhadas
from extensions import db, login_manager, csrf

# =========================
# Configuração
# =========================
try:
    # Se existir config.py com class Config, usamos.
    from config import Config as ExternalConfig  # type: ignore
except Exception:
    ExternalConfig = None  # fallback mais abaixo


class FallbackConfig:
    """Config padrão caso não exista config.Config.
    - SECRET_KEY: puxa do ambiente ou usa um valor dev
    - DB: SQLite local (ou path relativo)
    """
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///school.db"  # em Railway com volume, ajuste se necessário
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

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login settings
    login_manager.login_view = "auth.login"  # ajuste se seu endpoint for diferente
    login_manager.login_message_category = "warning"

    # Registrar models para o user_loader
    from models import User  # noqa: WPS433 (import dentro da factory)

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Helper para evitar BuildError quando um endpoint ainda não existe
    # Ex.: {{ url_or_hash('users.list_users') }}
    def url_or_hash(endpoint: str, **values) -> str:
        from werkzeug.routing import BuildError
        try:
            return url_for(endpoint, **values)
        except BuildError:
            return "#"

    app.jinja_env.globals["url_or_hash"] = url_or_hash
    app.jinja_env.globals["now"] = datetime.utcnow

    # Registra blueprints de forma segura (só se existirem)
    def _safe_register(import_path: str, bp_attr: str):
        try:
            mod = __import__(import_path, fromlist=[bp_attr])
            bp = getattr(mod, bp_attr)
            app.register_blueprint(bp)
        except Exception:
            # Não interrompe o app se o módulo/blueprint ainda não existir
            pass

    # auth (login/logout)
    _safe_register("auth", "auth_bp")
    # usuários (CRUD + trocar senha)
    _safe_register("users", "users_bp")
    # cadastros (horários/mensalidades) — ajuste ao seu projeto
    _safe_register("cadastro", "cadastro_bp")

    # Rotas básicas
    @app.route("/")
    @login_required
    def home():
        # Tenta renderizar home.html; se não existir, usa um fallback simples
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

    # Cria tabelas automaticamente (útil em dev/local)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # Evita quebrar o app em providers onde não há permissão no FS
            # (ex.: se usar Postgres externo, ignore create_all e use migrations)
            app.logger.warning(f"db.create_all() falhou: {e}")

    return app


# =========================
# Execução local
# =========================
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
