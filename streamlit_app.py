# streamlit_app.py
import streamlit as st
from app import create_app
from models import User, Horario, Mensalidade

st.set_page_config(page_title="School – verificação", layout="wide")

app = create_app()
with app.app_context():
    st.title("School — verificação de banco")
    st.write("Usuários:", User.query.count())
    st.write("Horários:", Horario.query.count())
    st.write("Mensalidades:", Mensalidade.query.count())
    st.info("A UI Flask/Jinja não é servida pelo Streamlit. Para a interface completa, use Render/Railway.")
