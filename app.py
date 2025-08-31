import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from flask_login import login_required
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import db, login_manager, csrf
from models import User

# Blueprints obrigatórios / opcionais
from auth import auth_bp  # login/logout/troca de senha/CRUD de usuários
try:
    # Caso você tenha o módulo "cadastro" (horários / mensalidades), registramos também
    from cadastro import cadastro_bp  # opcional
except Exception:
    cadastro_bp = None


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Para ambientes por trás de proxy (Railway/Render/etc.)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Flask-Login
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        if not user_id:
            return None
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="")
    if cadastro_bp is not None:
        app.register_blueprint(cadastro_bp, url_prefix="/cadastro")

    # Rotas básicas
    @app.route("/")
    @login_required
    def home():
        return render_template("home.html")

    # Contexto global (ex.: ano atual)
    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    # Criação de tabelas + seed do usuário padrão
    with app.app_context():
        db.create_all()
        _seed_default_admin(app)

    return app


def _seed_default_admin(app: Flask) -> None:
    """
    Cria o usuário padrão (Diretoria) caso não exista.
    Email: diretoria@school.com
    Senha: 123456
    """
    try:
        email = "diretoria@school.com"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, role="Diretoria", is_active=True)
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()
            app.logger.info("Usuário padrão criado: %s", email)
    except Exception as e:
        # Logar com stacktrace para facilitar debug no deploy
        app.logger.exception("Seed do usuário padrão falhou")
        # Não levantamos a exceção aqui para não derrubar o app em produção.
        # Se preferir falhar duro durante o deploy, troque para: raise


# Ponto de entrada
if __name__ == "__main__":
    app = create_app()
    # Em produção (Railway/Render) use o servidor do PaaS; localmente pode usar debug.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=debug)
