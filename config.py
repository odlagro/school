import os
from pathlib import Path

def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")

class Config:
    # Chave de sessão
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # Banco (SQLite por padrão; se tiver DATABASE_URL no Railway, usa)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        data_dir = os.getenv("DATA_DIR", "./instance")
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(data_dir) / 'school.db'}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookies e proxy (produção = HTTPS)
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", True)
    REMEMBER_COOKIE_SECURE = _bool_env("REMEMBER_COOKIE_SECURE", True)
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")

    # WTForms/CSRF
    WTF_CSRF_ENABLED = True
