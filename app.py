# app.py
from flask import Flask, render_template, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import logging
import os

from config import Config
from extensions import db, login_manager, csrf
from models import User
from auth import auth_bp  # seu blueprint de autenticação
from cadastro import cadastro_bp  # seus cadastros (usuarios/horarios/mensalidades)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Proxy fix para plataforma (X-Forwarded-Proto/For/Host)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)        # /login, /logout etc
    app.register_blueprint(cadastro_bp)    # /cadastro/... (usuarios, horarios, mensalidades)

    # Páginas
    @app.route("/")
    def index():
        # Se quiser redirecionar p/ home autenticada:
        return redirect(url_for("auth.home"))

    # Cria as tabelas e seed
    with app.app_context():
        db.create_all()
        _seed_default_admin(app)

    # Logs básicos
    app.logger.setLevel(logging.INFO)
    app.logger.info("App iniciado às %s", datetime.utcnow().isoformat())

    return app

def _seed_default_admin(app: Flask):
    """
    Cria o usuário padrão 'Diretoria' se não existir.
    E-mail: diretoria@school.com
    Senha: 123456
    """
    try:
        exists = User.query.filter_by(email="diretoria@school.com").first()
        if not exists:
            u = User(
                name="Diretoria",
                email="diretoria@school.com",
                role="Diretoria",
            )
            u.set_password("123456")
            u.is_active = True  # garante campo setado
            db.session.add(u)
            db.session.commit()
            app.logger.info("Usuário padrão criado.")
        else:
            app.logger.info("Usuário padrão já existe.")
    except Exception as e:
        db.session.rollback()
        app.logger.warning("Seed do usuário padrão falhou: %r", e)

# Se precisar expor a app p/ gunicorn como 'app:app'
app = create_app()

if __name__ == "__main__":
    # Para rodar local
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
