# cadastro/__init__.py
from flask import Blueprint

cadastro_bp = Blueprint("cadastro", __name__, template_folder="templates")
# IMPORTANTE: NÃO registre rota "/" aqui sem prefixo.
from . import routes  # noqa: E402,F401
