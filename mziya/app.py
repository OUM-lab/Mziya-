"""Point d'entrée principal de l'application Streamlit Mziya."""

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from components.cards import render_rtl_wrapper_start
from components.sidebar import render_sidebar
from config import DATABASE_PATH, STYLE_PATH
from database.database import init_db
from database.seed import seed_database
from pages.admin_page import render_admin_page
from pages.auth_page import render_auth_page
from pages.client_page import render_client_page
from pages.home_page import render_home_page
from pages.merchant_page import render_merchant_page


def load_css() -> None:
    """Charge le fichier style.css dans Streamlit."""
    if STYLE_PATH.exists():
        css = STYLE_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def ensure_database_ready() -> None:
    """Initialise la base SQLite et les données de démonstration si absente."""
    if not DATABASE_PATH.exists():
        seed_database()
    else:
        init_db()


def main() -> None:
    st.set_page_config(
        page_title="Mziya — Fidélité multi-commerces à Agadir",
        page_icon="💳",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    ensure_database_ready()
    load_css()

    if "language" not in st.session_state:
        st.session_state["language"] = "fr"
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "home"

    render_sidebar()
    render_rtl_wrapper_start(st.session_state.get("language", "fr"))

    page = st.session_state.get("current_page", "home")
    user = st.session_state.get("user")

    if page == "home":
        render_home_page()
    elif page == "auth":
        render_auth_page()
    elif page == "client":
        if user and user.get("role") == "client":
            render_client_page()
        else:
            st.session_state["current_page"] = "auth"
            render_auth_page()
    elif page == "merchant":
        if user and user.get("role") == "merchant":
            render_merchant_page()
        else:
            st.session_state["current_page"] = "auth"
            render_auth_page()
    elif page == "admin":
        if user and user.get("role") == "admin":
            render_admin_page()
        else:
            st.session_state["current_page"] = "auth"
            render_auth_page()
    else:
        render_home_page()


if __name__ == "__main__":
    main()
