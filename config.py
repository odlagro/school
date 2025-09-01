# config.py
import os
from urllib.parse import urlparse

def _normalize_database_url(url: str) -> str:
    """
    Converte postgres:// -> postgresql+psycopg2:// quando necessário.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url

class Config:
    # SECRET_KEY de ambiente, com fallback (troque em produção)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    WTF_CSRF_ENABLED = True

    # DATABASE_URL (Railway Postgres) OU fallback para SQLite em /tmp
    _db_url = os.getenv("DATABASE_URL", "").strip()
    if _db_url:
        SQLALCHEMY_DATABASE_URI = _normalize_database_url(_db_url)
    else:
        # Sempre gravável no Railway
        SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/school.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Outras configs úteis
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = "https"
