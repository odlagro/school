# school/app.py
from flask import Flask, render_template
from flask_login import login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime

from config import Config
from extensions import db, login_manager, csrf
from models import User
from auth import auth_bp
from auth.utils import roles_required
from cadastro import cadastro_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Útil se publicar atrás de proxy (Render/Railway)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cadastro_bp, url_prefix="/cadastro")

    # Criação automática do banco + seed inicial
    with app.app_context():
        db.create_all()
        seed_admin()

    # Rotas principais
    @app.route("/")
    @login_required
    def index():
        return render_template(
            "index.html",
            user=current_user,
            now=datetime.utcnow(),
        )

    # Áreas de exemplo com RBAC
    @app.route("/area-diretoria")
    @login_required
    @roles_required("Diretoria")
    def area_diretoria():
        return render_template(
            "index.html",
            user=current_user,
            custom_title="Área da Diretoria",
        )

    @app.route("/area-professor")
    @login_required
    @roles_required("Diretoria", "Professor")
    def area_professor():
        return render_template(
            "index.html",
            user=current_user,
            custom_title="Área do Professor",
        )

    # Tratamento simples para 403
    @app.errorhandler(403)
    def forbidden(_):
        return (
            render_template(
                "index.html",
                user=current_user,
                custom_title="Acesso negado (403)",
            ),
            403,
        )

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def seed_admin():
    """Cria um usuário default da Diretoria se não existir."""
    if not User.query.filter_by(email="diretoria@school.com").first():
        u = User(email="diretoria@school.com", name="Diretor(a) School", role="Diretoria")
        u.set_password("123456")
        db.session.add(u)
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
