from flask import Blueprint

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")

from . import routes  # mantém essa importação no final
