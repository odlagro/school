import os
from datetime import datetime

from flask import Flask, render_template, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import Config
from extensions import db, login_manager, csrf
from models import User

# Blueprints do projeto
from auth import auth_bp
try:
    # Se existir o módulo de cadastros (horários, mensalidades, etc.)
    from cadastro import cadastro_bp
except Exception:
    cadastro_bp = None


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Quando roda atrás de proxy (Railway/Render/etc.)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix="")
    if cadastro_bp is not None:
        app.register_blueprint(cadastro_bp, url_prefix="/cadastro")

    # Rotas simples
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.route("/home")
    def home():
        # Renderiza a página inicial pós-login
        return render_template("home.html")

    # Loader do Flask-Login
    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Cria tabelas e faz seed do usuário padrão
    with app.app_context():
        db.create_all()
        _seed_default_admin(app)

    return app


def _seed_default_admin(app: Flask) -> None:
    """
    Cria o usuário padrão (Diretoria) caso não exista.
    Email: diretoria@school.com
    Senha: 123456
    Protegido contra condições de corrida (vários workers).
    """
    email = "diretoria@school.com"
    try:
        existing = db.session.execute(
            select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if existing is None:
            user = User(email=email, role="Diretoria", is_active=True)
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()
            app.logger.info("Usuário padrão criado: %s", email)
        else:
            app.logger.info("Usuário padrão já existe: %s", email)

    except IntegrityError:
        # Outro worker criou ao mesmo tempo — tudo bem
        db.session.rollback()
        app.logger.info("Usuário padrão já existia (integrity).")
    except Exception:
        db.session.rollback()
        app.logger.exception("Seed do usuário padrão falhou")


# Ponto de entrada para gunicorn:  gunicorn -w 1 "app:create_app()"
if __name__ == "__main__":
    app = create_app()
    # Em produção use gunicorn. Este run é só para dev local.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
