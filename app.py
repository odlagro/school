import logging
import os
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import db, csrf, login_manager
from models import User, ROLE_DIRETORIA


def create_app():
    # Log básico
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Corrige headers atrás de proxy (Railway/NGINX)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Extensões
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    # DB + seed
    with app.app_context():
        db.create_all()
        _seed_or_fix_default_admin()
        _log_db_uri(app)

    # Rota raiz
    @app.route("/")
    def index():
        from flask_login import current_user
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return render_template("home.html")

    # Handler de acesso não autorizado
    @login_manager.unauthorized_handler
    def _unauthorized():
        return redirect(url_for("auth.login", next=request.path))

    return app


def _seed_or_fix_default_admin():
    """
    Garante que o usuário padrão exista e permaneça com os atributos esperados.
    Usuário: diretoria@school.com / Senha: 123456 / role=Diretoria / active=True
    """
    email = "diretoria@school.com"
    try:
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email, role=ROLE_DIRETORIA, active=True)
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()
            logging.info("Usuário padrão criado: %s", email)
        else:
            changed = False
            if user.role != ROLE_DIRETORIA:
                user.role = ROLE_DIRETORIA
                changed = True
            if user.active is not True:
                user.active = True
                changed = True
            # Força manter a senha padrão solicitada
            user.set_password("123456")
            changed = True
            if changed:
                db.session.commit()
                logging.info("Usuário padrão atualizado/normalizado: %s", email)
    except Exception as exc:
        db.session.rollback()
        logging.error("Seed/ajuste do usuário padrão falhou: %s", exc)


def _log_db_uri(app: Flask):
    """Loga (de forma segura) qual banco está em uso e o diretório de dados."""
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        path = uri.replace("sqlite:///", "", 1)
        data_dir = os.path.dirname(path)
        logging.info("SQLite em uso: %s", path)
        logging.info("DATA_DIR: %s", data_dir)
    else:
        logging.info("Banco externo em uso (DATABASE_URL).")


app = create_app()

if __name__ == "__main__":
    # Local: python app.py
    # Produção (Railway): gunicorn app:app -w 1 --timeout 120
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
