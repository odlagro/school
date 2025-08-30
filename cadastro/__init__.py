# school/cadastro/__init__.py
from flask import Blueprint

cadastro_bp = Blueprint("cadastro", __name__, template_folder="../templates/cadastro")

from . import routes  # noqa: E402,F401
