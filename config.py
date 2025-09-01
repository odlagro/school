import os
from pathlib import Path


def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _choose_data_dir() -> str:
    """
    Retorna um diretório gravável para o SQLite:
    - DATA_DIR (se definido)
    - RAILWAY_VOLUME_MOUNT_PATH (se você estiver usando Volume no Railway)
    - /tmp/school-data (sempre gravável no container)
    """
    return os.getenv("DATA_DIR") or os.getenv("RAILWAY_VOLUME_MOUNT_PATH") or "/tmp/school-data"


class Config:
    # Sessão/CSRF
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    WTF_CSRF_ENABLED = True

    # Banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL")  # se usar Postgres/MySQL no Railway
    if DATABASE_URL and not DATABASE_URL.startswith("sqlite"):
        # Ex.: postgres://...  / mysql://...
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    else:
        data_dir = _choose_data_dir()
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        db_path = Path(data_dir) / "school.db"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        # Para SQLite sob Gunicorn / threads
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "connect_args": {"check_same_thread": False},
        }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookies/proxy (produção HTTPS)
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", True)
    REMEMBER_COOKIE_SECURE = _bool_env("REMEMBER_COOKIE_SECURE", True)
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")
