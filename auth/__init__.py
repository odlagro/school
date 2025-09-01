# auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="")

# Importa as views após criar o blueprint
from . import routes        # suas rotas existentes (login/logout etc.)
from . import home_view     # adiciona o endpoint auth.home
