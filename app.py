# app.py
from flask import Flask, redirect, url_for, render_template
from flask_login import current_user, login_required
from extensions import db, login_manager, csrf
from auth import auth_bp
from cadastro import cadastro_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Redirecionar não autenticados para /login automaticamente
    login_manager.login_view = "auth.login"

    # Blueprints: cadastro SEMPRE com prefixo '/cadastro'
    app.register_blueprint(auth_bp)                       # /login, /home etc.
    app.register_blueprint(cadastro_bp, url_prefix="/cadastro")

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("auth.home"))
        return redirect(url_for("auth.login"))

    # Alias opcional para /home na app raiz
    @app.route("/home")
    @login_required
    def home_alias():
        return redirect(url_for("auth.home"))

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    with app.app_context():
        db.create_all()

    return app

app = create_app()
