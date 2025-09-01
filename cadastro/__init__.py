# cadastro/__init__.py
from flask import Blueprint

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

# importa as rotas depois de criar o blueprint
from . import routes  # noqa: E402,F401
