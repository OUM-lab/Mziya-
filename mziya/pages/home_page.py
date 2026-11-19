"""Page d'accueil attractive et moderne de Mziya (Agadir)."""

import streamlit as st

from components.cards import (
    render_contact_form,
    render_logo_header,
    render_promotion_card,
    render_reward_card,
    render_simulation_banner,
)
from services.promotion_service import get_promotions
from services.reward_service import get_rewards
from translations import get_text
from utils.constants import AGADIR_NEIGHBORHOODS


def render_home_page() -> None:
    """Affiche la page d'accueil vitrine de Mziya."""
    lang = st.session_state.get("language", "fr")
    current_user = st.session_state.get("user")

    render_logo_header(lang)
    render_simulation_banner(lang)

    # Hero Section + Illustration carte digitale HTML/CSS
    hero_col1, hero_col2 = st.columns([3, 2], gap="large")
    with hero_col1:
        st.markdown(
            f"""
            <div class="mziya-hero">
                <span class="mziya-hero-tag">🇲🇦 {get_text("city_pilot", lang)} • Fidélité locale</span>
                <h1>{get_text("app_name", lang)}</h1>
                <div class="mziya-hero-slogan">« {get_text("slogan", lang)} »</div>
                <p>{get_text("concept_desc", lang)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Boutons d'action principaux
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button(
                f"👤 {get_text('register_client', lang)}",
                type="primary",
                use_container_width=True,
                key="home_btn_reg_client",
            ):
                st.session_state["current_page"] = "auth"
                st.session_state["auth_mode"] = "register_client"
                st.rerun()
        with b2:
            if st.button(
                f"🏪 {get_text('register_merchant', lang)}",
                use_container_width=True,
                key="home_btn_reg_merchant",
            ):
                st.session_state["current_page"] = "auth"
                st.session_state["auth_mode"] = "register_merchant"
                st.rerun()
        with b3:
            if st.button(
                f"🔐 {get_text('login', lang)}",
                use_container_width=True,
                key="home_btn_login",
            ):
                st.session_state["current_page"] = "auth"
                st.session_state["auth_mode"] = "login"
                st.rerun()

    with hero_col2:
        st.markdown(
            """
            <div class="mziya-virtual-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
                    <span style="font-weight:800;font-size:1.25rem;letter-spacing:0.04em;">MZIYA PASS</span>
                    <span style="background:rgba(255,255,255,0.18);padding:0.2rem 0.6rem;border-radius:999px;font-size:0.75rem;">Agadir</span>
                </div>
                <div class="mziya-virtual-card-chip"></div>
                <div style="font-size:0.85rem;color:#cbd5e1;">ID Client Personnel</div>
                <div style="font-family:monospace;font-size:1.15rem;font-weight:700;letter-spacing:0.08em;margin:0.2rem 0 1rem 0;">
                    MZIYA-CLIENT-0001
                </div>
                <div style="display:flex;justify-content:space-between;align-items:flex-end;">
                    <div>
                        <div style="font-size:0.75rem;color:#94a3b8;">Solde simulé</div>
                        <div style="font-size:1.45rem;font-weight:800;color:#5eead4;">120 pts</div>
                    </div>
                    <div style="text-align:right;font-size:0.78rem;color:#e2e8f0;">
                        1 pt = 10 MAD<br/>Multi-commerces
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Avantages Clients & Commerçants
    c_col, m_col = st.columns(2, gap="large")
    with c_col:
        st.markdown(
            f"""
            <div class="mziya-card" style="border-top:4px solid #0ea5a4;">
                <h3 style="color:#0f2942;margin-top:0;">💳 {get_text("client_benefits_title", lang)}</h3>
                <ul style="padding-left:1.2rem;line-height:1.8;color:#334155;">
                    <li><strong>Un seul QR code personnel</strong> valable dans tous les commerces partenaires d'Agadir.</li>
                    <li><strong>1 point par tranche de 10 MAD</strong> dépensés chez votre épicier, boulanger ou supérette.</li>
                    <li><strong>Récompenses et cartes cadeaux simulées</strong> accessibles dès vos premiers achats.</li>
                    <li><strong>Promotions de proximité</strong> filtrées selon votre quartier à Agadir.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col:
        st.markdown(
            f"""
            <div class="mziya-card" style="border-top:4px solid #0f2942;">
                <h3 style="color:#0f2942;margin-top:0;">🏪 {get_text("merchant_benefits_title", lang)}</h3>
                <ul style="padding-left:1.2rem;line-height:1.8;color:#334155;">
                    <li><strong>Page commerce dédiée</strong> visible par tous les habitants de votre quartier.</li>
                    <li><strong>Fidélisation simple sans matériel coûteux</strong> : attribuez des points en 2 clics.</li>
                    <li><strong>Promotions & récompenses sur mesure</strong> pour dynamiser vos ventes locales.</li>
                    <li><strong>Statistiques en temps réel</strong> sur vos clients, points distribués et offres actives.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Comment ça marche en 3 étapes
    st.subheader(f"⚡ {get_text('how_it_works_title', lang)}")
    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        st.markdown(
            """
            <div class="mziya-card" style="text-align:center;">
                <div style="font-size:2rem;">1️⃣</div>
                <h4 style="color:#0f2942;margin:0.4rem 0;">Créez votre compte</h4>
                <p style="color:#475569;font-size:0.92rem;">Inscrivez-vous en quelques secondes et obtenez immédiatement votre QR code Mziya personnel.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            """
            <div class="mziya-card" style="text-align:center;">
                <div style="font-size:2rem;">2️⃣</div>
                <h4 style="color:#0f2942;margin:0.4rem 0;">Cumulez à Agadir</h4>
                <p style="color:#475569;font-size:0.92rem;">Présentez votre QR code dans les supérettes et commerces partenaires pour cumuler des points simulés.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            """
            <div class="mziya-card" style="text-align:center;">
                <div style="font-size:2rem;">3️⃣</div>
                <h4 style="color:#0f2942;margin:0.4rem 0;">Profitez des avantages</h4>
                <p style="color:#475569;font-size:0.92rem;">Échangez vos points contre des réductions simulées, paniers cadeaux et bons d'achat locaux.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Promotions locales et Récompenses
    promo_col, rew_col = st.columns(2, gap="large")
    with promo_col:
        st.subheader(f"🔥 {get_text('local_promotions_title', lang)}")
        promos = get_promotions(active_only=True)[:4]
        if promos:
            for p in promos:
                render_promotion_card(p, lang)
        else:
            st.info(get_text("no_results", lang))

    with rew_col:
        st.subheader(f"🎁 {get_text('rewards_showcase_title', lang)}")
        rewards = get_rewards(active_only=True)[:4]
        if rewards:
            for r in rewards:
                render_reward_card(r, lang)
        else:
            st.info(get_text("no_results", lang))

    # Quartiers d'Agadir
    st.subheader(f"📍 {get_text('agadir_neighborhoods_title', lang)}")
    pills_html = "".join(
        f'<span class="mziya-neighborhood-pill">📍 {nb}</span>'
        for nb in AGADIR_NEIGHBORHOODS
    )
    st.markdown(f'<div class="mziya-card">{pills_html}</div>', unsafe_allow_html=True)

    # Zone Contact et réclamations
    st.divider()
    render_contact_form(lang, current_user=current_user, key_prefix="home")
