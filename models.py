from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="Aluno")
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # fundamental p/ Flask-Login
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Métodos utilitários
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # O UserMixin já provê is_authenticated; manter get_id() explícito:
    def get_id(self) -> str:  # Flask-Login espera string
        return str(self.id)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


# (Opcional) Outros modelos que você já usa no sistema:

class Horario(db.Model):
    __tablename__ = "horarios"

    id = db.Column(db.Integer, primary_key=True)
    hora_inicio = db.Column(db.String(5), nullable=False)  # Ex.: "07:30"
    hora_fim = db.Column(db.String(5), nullable=False)     # Ex.: "11:45"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Horario {self.hora_inicio}-{self.hora_fim}>"


class Mensalidade(db.Model):
    __tablename__ = "mensalidades"

    id = db.Column(db.Integer, primary_key=True)
    serie = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Mensalidade {self.serie} - {self.valor}>"
