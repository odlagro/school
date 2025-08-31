from flask import Blueprint

auth_bp = Blueprint("auth", __name__)
# As rotas ficam em routes.py
from . import routes  # noqa: E402,F401
