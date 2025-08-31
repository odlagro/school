# users/__init__.py
from flask import Blueprint

users_bp = Blueprint("users", __name__, url_prefix="/users", template_folder="../templates")

# Importa rotas após criar o blueprint
from . import routes  # noqa: E402,F401
