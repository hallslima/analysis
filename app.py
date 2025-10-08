# app.py (Sua nova tela de login)

import streamlit as st

st.set_page_config(
    page_title="Login | Dashboard de Vendas",
    page_icon="🔐",
    layout="centered"
)

def check_password():
    """Retorna True se o usuário fez login, False caso contrário."""
    def password_entered():
        """Verifica se a senha digitada corresponde à senha correta."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não manter a senha em memória
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Layout do formulário de login
    st.image("imagens/logo_usina_white.png", width=300)
    st.title("Dashboard de Performance de Vendas")
    st.text_input(
        "Senha", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Senha incorreta. Tente novamente.")
    return False

if not check_password():
    st.stop()

# --- Se o login for bem-sucedido ---
st.switch_page("pages/1_Visão_Geral.py")