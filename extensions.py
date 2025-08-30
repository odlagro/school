# school/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect


# InstÃ¢ncias globais


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
