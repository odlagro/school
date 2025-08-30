# school/config.py
import os
from pathlib import Path

def _get_secret(name: str, default=None):
    """
    Lê primeiro de variáveis de ambiente.
    Se estiver rodando no Streamlit Cloud (st.secrets), tenta buscar lá também.
    """
    val = os.environ.get(name, None)
    if val is not None:
        return val
    try:
        import streamlit as st  # só existe no Streamlit Cloud
        return st.secrets.get(name, default)
    except Exception:
        return default


class Config:
    # SECRET_KEY: pegue de env ou de st.secrets (Streamlit)
    SECRET_KEY = _get_secret("SECRET_KEY", "dev-secret-key-change-me")

    # 1) Se houver DATABASE_URL, usamos (Postgres, etc.)
    db_url = _get_secret("DATABASE_URL")
    if db_url:
        # Compatibilidade com URLs "postgres://"
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # 2) Caso não haja DATABASE_URL, usamos SQLite num diretório gravável
        #    No Streamlit Cloud, /mount/data é o caminho correto.
        data_dir = _get_secret("DATA_DIR")
        if not data_dir:
            default_streamlit_dir = "/mount/data"
            data_dir = default_streamlit_dir if os.path.isdir(default_streamlit_dir) else os.getcwd()

        Path(data_dir).mkdir(parents=True, exist_ok=True)
        db_path = Path(data_dir) / "school.db"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
