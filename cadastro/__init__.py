from flask import Blueprint

cadastro_bp = Blueprint("cadastro", __name__, template_folder="../templates")

from . import routes  # noqa: E402,F401
