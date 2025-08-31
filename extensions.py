from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# IMPORTANTÍSSIMO: login_view com nome do endpoint do blueprint
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    # Import tardio para evitar import circular
    from models import User
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None
