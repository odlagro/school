from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, text

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Perfis: Diretoria, Professor, Aluno, Pai
    role = db.Column(db.String(20), nullable=False, server_default="Aluno", default="Aluno")

    # >>> CHAVE DA CORREÇÃO <<<
    # Coluna booleana real; NÃO crie @property is_active.
    is_active = db.Column(db.Boolean, nullable=False, server_default=text("TRUE"), default=True)

    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=datetime.utcnow,
    )

    # Helpers de senha
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


# ====== Demais modelos do sistema (caso você já os utilize) ======

class Horario(db.Model):
    __tablename__ = "horarios"

    id = db.Column(db.Integer, primary_key=True)
    hora_inicio = db.Column(db.String(5), nullable=False)  # formato "HH:MM"
    hora_fim = db.Column(db.String(5), nullable=False)     # formato "HH:MM"

    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<Horario {self.hora_inicio}-{self.hora_fim}>"


class Mensalidade(db.Model):
    __tablename__ = "mensalidades"

    id = db.Column(db.Integer, primary_key=True)
    serie = db.Column(db.String(120), nullable=False)     # Ex.: "6º Ano", "1ª Série"
    valor = db.Column(db.Numeric(10, 2), nullable=False)  # Ex.: 999.99

    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<Mensalidade {self.serie} R${self.valor}>"
