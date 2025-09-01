# app.py
import os
from datetime import datetime
from flask import Flask, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from config import Config
from extensions import db, login_manager, csrf
from models import User, ROLE_DIRETORIA


def _seed_default_admin(app: Flask) -> None:
    """
    Cria o usuário padrão apenas uma vez, evitando corrida entre workers.
    Email: diretoria@school.com | Senha: 123456 | Papel: Diretoria
    """
    lock_path = "/tmp/seed_school.lock"
    try:
        # criação atômica do lock; se já existir, outro worker já semeou
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        app.logger.info("Seed já realizado por outro worker.")
        return

    with app.app_context():
        admin = User.query.filter_by(email="diretoria@school.com").first()
        if admin:
            app.logger.info("Usuário padrão já existe.")
            return
        try:
            admin = User(
                name="Diretoria",
                email="diretoria@school.com",
                role=ROLE_DIRETORIA,
                is_active=True,
            )
            admin.set_password("123456")
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Usuário padrão criado com sucesso.")
        except IntegrityError as e:
            db.session.rollback()
            app.logger.warning(f"Seed do usuário padrão falhou: {e!r}")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Para proxies (Railway/Render/etc.)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # Blueprints
    from auth import auth_bp           # login/logout/etc (seu arquivo atual)
    from cadastro import cadastro_bp   # usuários/horários/mensalidades
    app.register_blueprint(auth_bp)
    app.register_blueprint(cadastro_bp)

    # Cria tabelas e faz seed do admin
    with app.app_context():
        db.create_all()
        _seed_default_admin(app)

    # Rotas básicas
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            # Redireciona para algo que existe com certeza
            return redirect(url_for("cadastro.usuarios_list"))
        return redirect(url_for("auth.login"))

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "ts": datetime.utcnow().isoformat()}

    app.logger.info(f"App iniciado em {datetime.utcnow().isoformat()}")
    return app


app = create_app()

if __name__ == "__main__":
    # Execução local
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=bool(os.environ.get("FLASK_DEBUG")))
