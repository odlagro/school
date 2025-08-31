from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

# Opcional: constantes de perfis
ROLE_DIRETORIA = "Diretoria"
ROLE_PROFESSOR = "Professor"
ROLE_ALUNO = "Aluno"
ROLE_PAI = "Pai"

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=ROLE_ALUNO)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # Flask-Login usa `get_id()` do UserMixin, então não precisa redefinir
    # Se precisar desativar usuário use o campo `active`; cheque `user.active` no login.
