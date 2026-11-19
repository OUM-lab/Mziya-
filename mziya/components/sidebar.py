"""Barre latérale de navigation et sélecteur de langue pour Mziya."""

import streamlit as st

from services.auth_service import logout_user
from translations import LANGUAGE_LABELS, get_text


def render_sidebar() -> None:
    """Affiche la barre latérale avec sélecteur de langue et navigation par rôle."""
    if "language" not in st.session_state:
        st.session_state["language"] = "fr"
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "home"

    lang = st.session_state["language"]
    user = st.session_state.get("user")

    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.4rem 0 0.75rem 0;">
                <div class="mziya-logo-wordmark">
                    <span class="mziya-logo-badge">M</span>
                    <span>Mziya</span>
                </div>
                <div style="font-size:0.82rem;color:#64748b;margin-top:0.25rem;">
                    📍 Agadir • Maroc
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Sélecteur de langue visible
        selected_lang = st.selectbox(
            f"🌐 {get_text('language', lang)}",
            options=["fr", "en", "ar"],
            index=["fr", "en", "ar"].index(lang),
            format_func=lambda code: LANGUAGE_LABELS.get(code, code),
            key="sidebar_lang_selector",
        )
        if selected_lang != lang:
            st.session_state["language"] = selected_lang
            st.rerun()

        lang = st.session_state["language"]
        st.divider()
        st.caption(get_text("navigation", lang))

        if st.button(f"🏠 {get_text('home', lang)}", use_container_width=True):
            st.session_state["current_page"] = "home"
            st.rerun()

        if user is None:
            if st.button(f"🔐 {get_text('login', lang)}", use_container_width=True):
                st.session_state["current_page"] = "auth"
                st.session_state["auth_mode"] = "login"
                st.rerun()
            if st.button(
                f"👤 {get_text('register_client', lang)}", use_container_width=True
            ):
                st.session_state["current_page"] = "auth"
                st.session_state["auth_mode"] = "register_client"
                st.rerun()
            if st.button(
                f"🏪 {get_text('register_merchant', lang)}", use_container_width=True
            ):
                st.session_state["current_page"] = "auth"
                st.session_state["auth_mode"] = "register_merchant"
                st.rerun()
        else:
            role = user.get("role")
            st.info(
                f"**{user.get('full_name')}**\n\n"
                f"Rôle : `{get_text(role, lang)}` • 📍 {user.get('neighborhood', 'Agadir')}"
            )

            if role == "client":
                if st.button(f"💳 {get_text('dashboard', lang)}", use_container_width=True):
                    st.session_state["current_page"] = "client"
                    st.rerun()
            elif role == "merchant":
                if st.button(f"🏪 {get_text('dashboard', lang)}", use_container_width=True):
                    st.session_state["current_page"] = "merchant"
                    st.rerun()
            elif role == "admin":
                if st.button(f"🛡️ {get_text('admin', lang)}", use_container_width=True):
                    st.session_state["current_page"] = "admin"
                    st.rerun()

            if st.button(f"🚪 {get_text('logout', lang)}", use_container_width=True):
                logout_user()
                st.rerun()

        st.divider()
        st.caption("⚠️ Prototype de démonstration — Données et récompenses simulées.")
