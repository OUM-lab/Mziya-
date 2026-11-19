"""Page d'authentification (Connexion, Inscription Client, Inscription Commerçant)."""

import streamlit as st

from components.cards import render_logo_header, render_simulation_banner
from services.auth_service import authenticate_user, register_user
from translations import get_text
from utils.constants import AGADIR_NEIGHBORHOODS, BUSINESS_TYPES


def render_auth_page() -> None:
    """Affiche les formulaires de connexion et d'inscription."""
    lang = st.session_state.get("language", "fr")
    mode = st.session_state.get("auth_mode", "login")

    render_logo_header(lang)
    render_simulation_banner(lang)

    modes = ["login", "register_client", "register_merchant"]
    mode_labels = {
        "login": f"🔐 {get_text('login', lang)}",
        "register_client": f"👤 {get_text('register_client', lang)}",
        "register_merchant": f"🏪 {get_text('register_merchant', lang)}",
    }
    selected_mode = st.radio(
        get_text("register", lang),
        options=modes,
        index=modes.index(mode) if mode in modes else 0,
        format_func=lambda m: mode_labels[m],
        horizontal=True,
    )
    st.session_state["auth_mode"] = selected_mode

    if selected_mode == "login":
        col_form, col_demo = st.columns([3, 2], gap="large")
        with col_form:
            st.subheader(f"🔐 {get_text('login', lang)}")
            with st.form("login_form"):
                email = st.text_input(get_text("email", lang))
                password = st.text_input(get_text("password", lang), type="password")
                submitted = st.form_submit_button(
                    get_text("login", lang), type="primary", use_container_width=True
                )
                if submitted:
                    ok, msg, user = authenticate_user(email, password)
                    if ok and user:
                        st.session_state["user"] = user
                        st.session_state["authenticated"] = True
                        st.session_state["language"] = user.get("language", lang)
                        role = user.get("role", "client")
                        st.session_state["current_page"] = role
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col_demo:
            st.markdown(
                """
                <div class="mziya-card" style="border-left:4px solid #0ea5a4;">
                    <h4 style="margin-top:0;color:#0f2942;">Comptes de démonstration</h4>
                    <p style="font-size:0.88rem;color:#475569;margin-bottom:0.5rem;">
                        <strong>👤 Client :</strong><br/>
                        <code>client@mziya.ma</code> / <code>Client123!</code>
                    </p>
                    <p style="font-size:0.88rem;color:#475569;margin-bottom:0.5rem;">
                        <strong>🏪 Commerçant :</strong><br/>
                        <code>merchant@mziya.ma</code> / <code>Merchant123!</code>
                    </p>
                    <p style="font-size:0.88rem;color:#475569;margin-bottom:0;">
                        <strong>🛡️ Administration :</strong><br/>
                        <code>admin@mziya.ma</code> / <code>Admin123!</code>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    elif selected_mode == "register_client":
        st.subheader(f"👤 {get_text('register_client', lang)}")
        st.caption(f"📍 {get_text('city_pilot', lang)}")
        with st.form("register_client_form"):
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input(get_text("full_name", lang))
                email = st.text_input(get_text("email", lang))
                phone = st.text_input(
                    f"{get_text('phone', lang)} (ex: 0612345678)"
                )
            with c2:
                neighborhood = st.selectbox(
                    f"{get_text('neighborhood', lang)} (Agadir)",
                    AGADIR_NEIGHBORHOODS,
                )
                password = st.text_input(get_text("password", lang), type="password")
                confirm_pw = st.text_input(
                    f"{get_text('confirm', lang)} {get_text('password', lang)}",
                    type="password",
                )

            submitted = st.form_submit_button(
                get_text("register_client", lang),
                type="primary",
                use_container_width=True,
            )
            if submitted:
                if password != confirm_pw:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    ok, msg, user = register_user(
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        password=password,
                        role="client",
                        neighborhood=neighborhood,
                        language=lang,
                    )
                    if ok and user:
                        st.session_state["user"] = user
                        st.session_state["authenticated"] = True
                        st.session_state["current_page"] = "client"
                        st.success(f"{msg} QR Code : {user.get('qr_code')}")
                        st.rerun()
                    else:
                        st.error(msg)

    elif selected_mode == "register_merchant":
        st.subheader(f"🏪 {get_text('register_merchant', lang)}")
        st.caption(f"📍 {get_text('city_pilot', lang)}")
        with st.form("register_merchant_form"):
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Nom du gérant")
                email = st.text_input(get_text("email", lang))
                phone = st.text_input(
                    f"{get_text('phone', lang)} (ex: 0612345678)"
                )
                password = st.text_input(get_text("password", lang), type="password")
                confirm_pw = st.text_input(
                    f"{get_text('confirm', lang)} {get_text('password', lang)}",
                    type="password",
                )
            with c2:
                business_name = st.text_input(get_text("business_name", lang))
                business_type = st.selectbox(
                    get_text("business_type", lang), BUSINESS_TYPES
                )
                neighborhood = st.selectbox(
                    f"{get_text('neighborhood', lang)} (Agadir)",
                    AGADIR_NEIGHBORHOODS,
                )
                address = st.text_input(get_text("address", lang))
                description = st.text_area(get_text("description", lang), height=80)

            submitted = st.form_submit_button(
                get_text("register_merchant", lang),
                type="primary",
                use_container_width=True,
            )
            if submitted:
                if password != confirm_pw:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    ok, msg, user = register_user(
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        password=password,
                        role="merchant",
                        neighborhood=neighborhood,
                        language=lang,
                        business_name=business_name,
                        business_type=business_type,
                        address=address,
                        description=description,
                    )
                    if ok and user:
                        st.session_state["user"] = user
                        st.session_state["authenticated"] = True
                        st.session_state["current_page"] = "merchant"
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
