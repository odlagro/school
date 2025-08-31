# models.py
from __future__ import annotations

from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from extensions import db

# =========================
# Usuário
# =========================
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="Aluno")  # Diretoria, Professor, Aluno, Pai
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Métodos de senha
    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    # Flask-Login: ativo?
    def is_active_user(self) -> bool:
        return bool(self.is_active)

    # Flask-Login usa is_active como property
    @property
    def is_active(self):  # type: ignore[override]
        return self.__dict__["is_active"]

    @is_active.setter
    def is_active(self, value: bool):
        self.__dict__["is_active"] = bool(value)

    def __repr__(self) -> str:  # debug
        return f"<User {self.id} {self.email} ({self.role})>"


# =========================
# Horários
# =========================
class Horario(db.Model):
    __tablename__ = "horarios"

    id = db.Column(db.Integer, primary_key=True)
    hora_inicio = db.Column(db.Time, nullable=False)  # time
    hora_fim = db.Column(db.Time, nullable=False)     # time

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def as_range_str(self) -> str:
        def fmt(t: time) -> str:
            return t.strftime("%H:%M")
        return f"{fmt(self.hora_inicio)} - {fmt(self.hora_fim)}"

    def __repr__(self) -> str:
        return f"<Horario {self.id} {self.as_range_str()}>"


# =========================
# Mensalidade
# =========================
class Mensalidade(db.Model):
    __tablename__ = "mensalidades"

    id = db.Column(db.Integer, primary_key=True)
    serie = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Mensalidade {self.id} {self.serie} R${self.valor}>"
