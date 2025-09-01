# models.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

ROLE_DIRETORIA = "Diretoria"
ROLE_COLABORADOR = "Colaborador"

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=ROLE_COLABORADOR)
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # usado pelo Flask-Login
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:  # para Flask-Login
        return str(self.id)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.email} ({self.role})>"

class Horario(db.Model):
    __tablename__ = "horarios"

    id = db.Column(db.Integer, primary_key=True)
    # Você pode trocar para Time se quiser (db.Time); String é mais simples/portável
    hora_inicio = db.Column(db.String(5), nullable=False)  # "08:00"
    hora_fim = db.Column(db.String(5), nullable=False)     # "12:00"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Horario {self.id} {self.hora_inicio}-{self.hora_fim}>"

class Mensalidade(db.Model):
    __tablename__ = "mensalidades"

    id = db.Column(db.Integer, primary_key=True)
    serie = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Mensalidade {self.id} {self.serie} {self.valor}>"
