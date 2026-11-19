"""Espace Client Mziya — QR code, points simulés, récompenses, promotions et profil."""

from datetime import date, timedelta

import streamlit as st

from components.cards import (
    render_contact_form,
    render_logo_header,
    render_promotion_card,
    render_reward_card,
    render_simulation_banner,
    render_stat_card,
)
from components.tables import render_generic_table, render_transactions_table
from services.auth_service import (
    get_all_merchants,
    get_user_by_id,
    require_role,
    update_client_profile,
)
from services.message_service import get_messages
from services.points_service import (
    get_client_notifications,
    get_client_transactions,
    mark_notifications_read,
)
from services.promotion_service import get_promotions
from services.qr_service import generate_qr_image_bytes, get_client_qr_payload
from services.reward_service import (
    create_simulated_gift_card,
    disable_gift_card,
    get_client_redemptions,
    get_gift_cards,
    get_rewards,
    redeem_reward,
)
from translations import get_text
from utils.constants import AGADIR_NEIGHBORHOODS
from utils.formatting import format_datetime, format_mad, format_points


def render_client_page() -> None:
    """Affiche le tableau de bord client protégé par rôle."""
    lang = st.session_state.get("language", "fr")
    if not require_role("client"):
        st.error("Accès refusé. Veuillez vous connecter avec un compte client actif.")
        return

    session_user = st.session_state["user"]
    fresh_user = get_user_by_id(session_user["id"])
    if not fresh_user or int(fresh_user["is_active"]) != 1:
        st.error("Votre compte est inactif ou introuvable.")
        return
    st.session_state["user"] = fresh_user
    user = fresh_user
    client_id = int(user["id"])

    render_logo_header(lang)
    render_simulation_banner(lang)

    st.markdown(
        f"### 👋 Bienvenue, **{user['full_name']}** — 📍 {user['neighborhood']}, Agadir"
    )

    notifications = get_client_notifications(client_id)
    unread_count = sum(1 for n in notifications if int(n.get("is_read", 0)) == 0)

    tabs = st.tabs(
        [
            f"🏠 {get_text('dashboard', lang)}",
            f"📱 {get_text('my_qr', lang)}",
            f"⭐ {get_text('my_points', lang)}",
            f"🎁 {get_text('my_rewards', lang)}",
            f"🔥 {get_text('promotions', lang)}",
            f"📜 {get_text('history', lang)}",
            f"🔔 {get_text('notifications', lang)} ({unread_count})",
            f"👤 {get_text('my_profile', lang)}",
            f"💬 {get_text('messages_complaints', lang)}",
        ]
    )

    transactions = get_client_transactions(client_id)
    redemptions = get_client_redemptions(client_id)

    # 1. Tableau de bord
    with tabs[0]:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_stat_card(
                get_text("points_balance", lang),
                format_points(user["points_balance"]),
                "Points simulés multi-commerces",
            )
        with c2:
            render_stat_card(
                get_text("neighborhood", lang),
                user["neighborhood"],
                "Ville pilote : Agadir",
            )
        with c3:
            render_stat_card(
                get_text("transactions", lang),
                len(transactions),
                "Achats & échanges simulés",
            )
        with c4:
            render_stat_card(
                get_text("my_rewards", lang),
                len(redemptions),
                "Récompenses obtenues",
            )

        st.subheader("Dernières opérations simulées")
        render_transactions_table(transactions[:5], lang)

    # 2. Mon QR code
    with tabs[1]:
        st.subheader(f"📱 {get_text('my_qr', lang)}")
        qr_payload = get_client_qr_payload(client_id, user.get("qr_code"))
        qr_bytes = generate_qr_image_bytes(qr_payload)

        col_qr, col_info = st.columns([1, 2], gap="large")
        with col_qr:
            st.image(qr_bytes, caption=qr_payload, width=240)
            st.download_button(
                label=f"⬇️ {get_text('download_qr', lang)}",
                data=qr_bytes,
                file_name=f"{qr_payload}.png",
                mime="image/png",
                use_container_width=True,
            )
        with col_info:
            st.markdown(
                f"""
                <div class="mziya-card">
                    <h4 style="margin-top:0;color:#0f2942;">Carte de fidélité digitale Mziya</h4>
                    <p>Identifiant personnel non sensible : <code>{qr_payload}</code></p>
                    <p style="color:#475569;font-size:0.92rem;">
                        Présentez ce QR code au commerçant lors de vos achats à Agadir.
                        Aucune donnée bancaire, mot de passe ou email privé n'est stocké dans ce QR code.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Mes points + Cartes cadeaux simulées
    with tabs[2]:
        st.subheader(f"⭐ {get_text('my_points', lang)}")
        render_stat_card(
            get_text("points_balance", lang),
            format_points(user["points_balance"]),
            "Règle par défaut : 1 point simulé pour chaque tranche de 10 MAD dépensés",
        )

        st.divider()
        st.subheader(f"🎟️ {get_text('gift_cards', lang)}")
        st.warning(f"ℹ️ {get_text('gift_card_disclaimer', lang)}")

        merchants = get_all_merchants(active_only=True)
        if merchants:
            with st.form("client_gift_card_form"):
                gc1, gc2, gc3 = st.columns(3)
                with gc1:
                    m_map = {
                        f"{m['business_name']} ({m['neighborhood']})": m["id"]
                        for m in merchants
                    }
                    selected_m_label = st.selectbox(
                        get_text("business", lang), list(m_map.keys())
                    )
                with gc2:
                    gc_amount = st.number_input(
                        get_text("amount_mad", lang),
                        min_value=10.0,
                        max_value=5000.0,
                        value=100.0,
                        step=10.0,
                    )
                with gc3:
                    gc_exp = st.date_input(
                        "Date d'expiration",
                        value=date.today() + timedelta(days=180),
                    )
                if st.form_submit_button(
                    "➕ Créer une carte cadeau simulée", use_container_width=True
                ):
                    ok, msg, _ = create_simulated_gift_card(
                        merchant_id=m_map[selected_m_label],
                        amount=gc_amount,
                        expiration_date=gc_exp.isoformat(),
                        client_id=client_id,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        gift_cards = get_gift_cards(client_id=client_id)
        if gift_cards:
            for gc in gift_cards:
                c_left, c_right = st.columns([4, 1])
                with c_left:
                    st.markdown(
                        f"""
                        <div class="mziya-card">
                            <strong>🎟️ {gc['gift_code']}</strong> — {gc['business_name']} ({gc['neighborhood']})<br/>
                            Montant simulé : <strong>{format_mad(gc['amount'])}</strong> • Statut : <code>{gc['status']}</code> • Expire le : {gc['expiration_date']}<br/>
                            <small style="color:#b45309;">{get_text("gift_card_disclaimer", lang)}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_right:
                    if gc["status"] == "active":
                        if st.button(
                            get_text("disable", lang),
                            key=f"disable_gc_{gc['id']}",
                            use_container_width=True,
                        ):
                            ok, msg = disable_gift_card(gc["id"], client_id=client_id)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info(get_text("no_results", lang))

    # 4. Mes récompenses
    with tabs[3]:
        st.subheader(f"🎁 {get_text('my_rewards', lang)}")
        f1, f2 = st.columns(2)
        with f1:
            nb_filter = st.selectbox(
                get_text("neighborhood", lang),
                ["ALL"] + AGADIR_NEIGHBORHOODS,
                format_func=lambda x: get_text("all_neighborhoods", lang)
                if x == "ALL"
                else x,
                key="client_reward_nb_filter",
            )
        with f2:
            active_merchants = get_all_merchants(active_only=True)
            merchant_opts = {"ALL": get_text("all_businesses", lang)}
            for m in active_merchants:
                merchant_opts[str(m["id"])] = f"{m['business_name']} ({m['neighborhood']})"
            m_filter = st.selectbox(
                get_text("business", lang),
                list(merchant_opts.keys()),
                format_func=lambda x: merchant_opts[x],
                key="client_reward_m_filter",
            )

        available_rewards = get_rewards(
            merchant_id=None if m_filter == "ALL" else int(m_filter),
            neighborhood=nb_filter,
            active_only=True,
        )

        if available_rewards:
            for rw in available_rewards:
                r_col1, r_col2 = st.columns([4, 1])
                with r_col1:
                    render_reward_card(rw, lang)
                with r_col2:
                    st.write("")
                    can_afford = int(user["points_balance"]) >= int(rw["points_required"])
                    has_stock = int(rw["stock"]) > 0
                    if st.button(
                        f"🎁 {get_text('redeem_reward', lang)}",
                        key=f"redeem_rw_{rw['id']}",
                        disabled=not (can_afford and has_stock),
                        use_container_width=True,
                    ):
                        ok, msg, _ = redeem_reward(client_id, rw["id"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    if not has_stock:
                        st.caption("Stock épuisé")
                    elif not can_afford:
                        st.caption(
                            f"Il manque {int(rw['points_required']) - int(user['points_balance'])} pts"
                        )
        else:
            st.info(get_text("no_results", lang))

        st.divider()
        st.subheader("Mes récompenses simulées déjà obtenues")
        render_generic_table(
            redemptions,
            [
                "redemption_code",
                "reward_title",
                "business_name",
                "neighborhood",
                "points_used",
                "status",
                "redeemed_at",
            ],
            lang,
        )

    # 5. Promotions à Agadir
    with tabs[4]:
        st.subheader(f"🔥 {get_text('promotions', lang)} — Agadir")
        promo_nb = st.selectbox(
            get_text("neighborhood", lang),
            ["ALL"] + AGADIR_NEIGHBORHOODS,
            format_func=lambda x: get_text("all_neighborhoods", lang)
            if x == "ALL"
            else x,
            key="client_promo_nb_filter",
        )
        promos = get_promotions(neighborhood=promo_nb, active_only=True)
        if promos:
            for p in promos:
                render_promotion_card(p, lang)
        else:
            st.info(get_text("no_results", lang))

    # 6. Historique
    with tabs[5]:
        st.subheader(f"📜 {get_text('history', lang)}")
        render_transactions_table(transactions, lang)

    # 7. Notifications
    with tabs[6]:
        st.subheader(f"🔔 {get_text('notifications', lang)}")
        if notifications:
            if st.button(f"✓ {get_text('mark_all_read', lang)}"):
                mark_notifications_read(client_id)
                st.rerun()
            for n in notifications:
                badge = "🆕 " if int(n["is_read"]) == 0 else ""
                st.markdown(
                    f"""
                    <div class="mziya-card">
                        <strong>{badge}{n['title']}</strong><br/>
                        <span style="color:#475569;">{n['message']}</span><br/>
                        <small style="color:#94a3b8;">{format_datetime(n['created_at'])}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info(get_text("no_results", lang))

    # 8. Mon profil
    with tabs[7]:
        st.subheader(f"👤 {get_text('my_profile', lang)}")
        with st.form("client_profile_form"):
            new_name = st.text_input(
                get_text("full_name", lang), value=user["full_name"]
            )
            new_phone = st.text_input(get_text("phone", lang), value=user["phone"])
            nb_idx = (
                AGADIR_NEIGHBORHOODS.index(user["neighborhood"])
                if user["neighborhood"] in AGADIR_NEIGHBORHOODS
                else 0
            )
            new_nb = st.selectbox(
                f"{get_text('neighborhood', lang)} (Agadir)",
                AGADIR_NEIGHBORHOODS,
                index=nb_idx,
            )
            lang_idx = ["fr", "en", "ar"].index(user.get("language", "fr"))
            new_lang = st.selectbox(
                get_text("language", lang), ["fr", "en", "ar"], index=lang_idx
            )
            if st.form_submit_button(
                f"💾 {get_text('save', lang)}",
                type="primary",
                use_container_width=True,
            ):
                ok, msg = update_client_profile(
                    client_id, new_name, new_phone, new_nb, new_lang
                )
                if ok:
                    st.session_state["language"] = new_lang
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # 9. Messages et réclamations
    with tabs[8]:
        render_contact_form(lang, current_user=user, key_prefix="client")
        st.divider()
        st.subheader("Mes messages envoyés")
        my_msgs = get_messages(user_id=client_id)
        render_generic_table(
            my_msgs,
            ["id", "subject", "message_type", "status", "admin_response", "created_at"],
            lang,
        )
