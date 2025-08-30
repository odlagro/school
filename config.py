# school/config.py
import os
import tempfile

def _get_secret(name: str, default=None):
    # 1º tenta variáveis de ambiente; no Streamlit, st.secrets abaixo
    val = os.environ.get(name)
    if val is not None:
        return val
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default


class Config:
    SECRET_KEY = _get_secret("SECRET_KEY", "dev-secret-key-change-me")

    db_url = _get_secret("DATABASE_URL")
    if db_url:
        # normaliza URLs antigas e força driver psycopg (v3)
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql://") and "+psycopg" not in db_url and "+psycopg2" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Sem DATABASE_URL: usa SQLite num diretório JÁ gravável (sem criar pasta)
        # Ordem de preferência: DATA_DIR (secreto), /tmp, tempdir do SO, $HOME
        candidates = [
            _get_secret("DATA_DIR"),
            "/tmp",
            tempfile.gettempdir(),
            os.path.expanduser("~"),
        ]
        data_dir = next((c for c in candidates if c and os.path.isdir(c) and os.access(c, os.W_OK)), "/tmp")
        db_path = os.path.join(data_dir, "school.db")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
