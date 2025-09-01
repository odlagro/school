# app.py
from flask import Flask, redirect, url_for, render_template
from flask_login import current_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from jinja2 import TemplateNotFound

from config import Config
from extensions import db, login_manager, csrf

from auth import auth_bp
from cadastro import cadastro_bp


def _seed_default_admin():
    from models import User, ROLE_DIRETORIA
    try:
        admin = User.query.filter_by(email="diretoria@school.com").first()
        if not admin:
            admin = User(
                name="Diretoria",
                email="diretoria@school.com",
                role=ROLE_DIRETORIA,
                active=True,
            )
            admin.set_password("123456")
            db.session.add(admin)
            db.session.commit()
    except Exception:
        db.session.rollback()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)                         # /login, /logout, /home
    app.register_blueprint(cadastro_bp, url_prefix="/cadastro")

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("auth.home"))
        return redirect(url_for("auth.login"))

    @app.route("/home")
    @login_required
    def home_alias():
        return redirect(url_for("auth.home"))

    # Healthchecks
    @app.route("/healthz")
    def healthz():
        return "ok", 200

    @app.route("/_health")
    def health_alt():
        return "ok", 200

    # Handlers de erro com fallback se o template faltar
    @app.errorhandler(404)
    def not_found(e):
        try:
            return render_template("404.html"), 404
        except TemplateNotFound:
            return "404 - Página não encontrada", 404

    @app.errorhandler(500)
    def server_error(e):
        try:
            return render_template("500.html"), 500
        except TemplateNotFound:
            return "500 - Erro interno", 500

    with app.app_context():
        db.create_all()
        _seed_default_admin()
        # Loga o mapa de rotas para debug
        app.logger.info("Rotas: %s", [r.rule for r in app.url_map.iter_rules()])

    app.logger.info(f"App iniciado em {datetime.utcnow().isoformat()}")
    return app


app = create_app()
