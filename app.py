import logging
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import db, csrf, login_manager
from models import User, ROLE_DIRETORIA

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Corrige headers atrás de proxy (Railway/Render/nginx/heroku-ps)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Inicializa extensões
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    # Cria tabelas e semeia usuário padrão
    with app.app_context():
        db.create_all()
        _seed_default_admin()

    # ROTA RAIZ – só redireciona ao login se NÃO autenticado
    @app.route("/")
    def index():
        from flask_login import current_user
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return render_template("home.html")

    # Handler de não autorizado do Flask-Login
    @login_manager.unauthorized_handler
    def _unauthorized():
        return redirect(url_for("auth.login", next=request.path))

    return app

def _seed_default_admin():
    """Cria usuário padrão uma única vez (ignora se já existir)."""
    try:
        email = "diretoria@school.com"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, role=ROLE_DIRETORIA, active=True)
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()
    except Exception as exc:
        logging.warning("Seed do usuário padrão falhou: %s", exc)

app = create_app()

if __name__ == "__main__":
    # Para rodar localmente: python app.py
    # Em produção, o Railway usa gunicorn apontando para "app:app"
    app.run(debug=True, host="0.0.0.0", port=8080)
