"""Cartes visuelles HTML/CSS et formulaire de contact/réclamations réutilisable."""

import html
from typing import Any, Dict, Optional

import streamlit as st

from config import LOGO_PATH
from services.message_service import create_message
from translations import get_text, is_rtl
from utils.constants import MESSAGE_TYPES


def _esc(val: Any) -> str:
    return html.escape("" if val is None else str(val))


def render_rtl_wrapper_start(language: str) -> None:
    """Applique la direction RTL si la langue sélectionnée est l'arabe."""
    if is_rtl(language):
        st.markdown(
            """
            <style>
            .main .block-container { direction: rtl; text-align: right; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def render_simulation_banner(language: str) -> None:
    """Affiche l'avertissement obligatoire de prototype simulé."""
    rtl_cls = "mziya-rtl" if is_rtl(language) else ""
    st.markdown(
        f"""
        <div class="mziya-sim-banner {rtl_cls}">
            ⚠️ <strong>Mode démonstration :</strong> {_esc(get_text("simulation_banner", language))}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_logo_header(language: str) -> None:
    """Affiche le logo (image si présente, sinon wordmark CSS Mziya)."""
    if LOGO_PATH.exists():
        col1, col2 = st.columns([1, 6])
        with col1:
            st.image(str(LOGO_PATH), width=56)
        with col2:
            st.markdown(
                f"""
                <div class="mziya-logo-wordmark">
                    <span>{_esc(get_text("app_name", language))}</span>
                </div>
                <div style="color:#64748b;font-size:0.9rem;">{_esc(get_text("city_pilot", language))}</div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.75rem;margin-bottom:0.75rem;">
                <div class="mziya-logo-wordmark">
                    <span class="mziya-logo-badge">M</span>
                    <span>{_esc(get_text("app_name", language))}</span>
                </div>
                <span class="mziya-badge-teal">📍 {_esc(get_text("city_pilot", language))}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_stat_card(label: str, value: Any, subtitle: str = "") -> None:
    """Affiche une carte statistique fintech."""
    sub_html = f'<div class="mziya-stat-sub">{_esc(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="mziya-stat-card">
            <div class="mziya-stat-label">{_esc(label)}</div>
            <div class="mziya-stat-value">{_esc(value)}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_promotion_card(promo: Dict[str, Any], language: str = "fr") -> None:
    """Affiche une carte promotionnelle locale (Agadir)."""
    status_label = "Active" if int(promo.get("is_active", 1)) == 1 else "Inactive"
    st.markdown(
        f"""
        <div class="mziya-promo-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
                <span class="mziya-badge-orange">🔥 -{float(promo.get("discount_percentage", 0)):.0f}%</span>
                <span class="mziya-badge-teal">📍 {_esc(promo.get("neighborhood", "Agadir"))}</span>
            </div>
            <h4 style="margin:0.6rem 0 0.25rem 0;color:#0f2942;">{_esc(promo.get("title"))}</h4>
            <div style="font-size:0.86rem;font-weight:600;color:#0ea5a4;margin-bottom:0.35rem;">
                🏪 {_esc(promo.get("business_name", ""))}
            </div>
            <p style="font-size:0.9rem;color:#475569;margin:0 0 0.5rem 0;">{_esc(promo.get("description"))}</p>
            <div style="font-size:0.78rem;color:#64748b;">
                📅 {_esc(promo.get("start_date"))} → {_esc(promo.get("end_date"))} • <strong>{_esc(status_label)}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reward_card(reward: Dict[str, Any], language: str = "fr") -> None:
    """Affiche une carte récompense simulée."""
    st.markdown(
        f"""
        <div class="mziya-reward-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
                <span class="mziya-badge-green">🎁 {int(reward.get("points_required", 0))} pts</span>
                <span class="mziya-badge-teal">📍 {_esc(reward.get("neighborhood", "Agadir"))}</span>
            </div>
            <h4 style="margin:0.6rem 0 0.25rem 0;color:#0f2942;">{_esc(reward.get("title"))}</h4>
            <div style="font-size:0.86rem;font-weight:600;color:#0ea5a4;margin-bottom:0.35rem;">
                🏪 {_esc(reward.get("business_name", ""))} • {_esc(reward.get("reward_type", ""))}
            </div>
            <p style="font-size:0.9rem;color:#475569;margin:0 0 0.5rem 0;">{_esc(reward.get("description"))}</p>
            <div style="font-size:0.78rem;color:#64748b;">
                📦 Stock : <strong>{int(reward.get("stock", 0))}</strong> • ⏳ Expire : {_esc(reward.get("expiration_date"))} • <em>Simulation</em>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_contact_form(
    language: str,
    current_user: Optional[Dict[str, Any]] = None,
    key_prefix: str = "contact",
) -> None:
    """Affiche le formulaire « Contact et réclamations » relié à SQLite."""
    st.subheader(f"💬 {get_text('contact_complaints', language)}")
    default_name = current_user.get("full_name", "") if current_user else ""
    default_email = current_user.get("email", "") if current_user else ""
    user_id = current_user.get("id") if current_user else None

    with st.form(key=f"{key_prefix}_message_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(get_text("name", language), value=default_name)
        with col2:
            email = st.text_input(get_text("email", language), value=default_email)

        col3, col4 = st.columns(2)
        with col3:
            subject = st.text_input(get_text("subject", language))
        with col4:
            msg_type = st.selectbox(get_text("message_type", language), MESSAGE_TYPES)

        body = st.text_area(get_text("message_body", language), height=110)
        submitted = st.form_submit_button(
            f"📩 {get_text('send', language)}", use_container_width=True
        )

        if submitted:
            ok, feedback, _ = create_message(
                name=name,
                email=email,
                subject=subject,
                message_type=msg_type,
                message=body,
                user_id=user_id,
            )
            if ok:
                st.success(f"{get_text('operation_success', language)} — {feedback}")
            else:
                st.error(feedback)
