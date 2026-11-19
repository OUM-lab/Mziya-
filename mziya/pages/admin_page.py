"""Page Administration Mziya — Gestion complète, statistiques SQLite et réclamations."""

import streamlit as st

from components.cards import (
    render_logo_header,
    render_simulation_banner,
    render_stat_card,
)
from components.charts import (
    build_active_neighborhoods_chart,
    build_top_merchants_chart,
    build_transactions_evolution_chart,
    build_users_by_role_chart,
    get_admin_kpis,
)
from components.tables import render_generic_table, render_transactions_table
from services.auth_service import (
    get_all_merchants,
    get_all_users,
    register_user,
    require_role,
    set_user_active_status,
)
from services.message_service import get_messages, update_message_status
from services.points_service import get_all_transactions
from services.promotion_service import get_promotions, toggle_promotion_status
from services.reward_service import get_rewards, toggle_reward_status
from translations import get_text
from utils.constants import (
    AGADIR_NEIGHBORHOODS,
    BUSINESS_TYPES,
    MESSAGE_STATUSES,
    MESSAGE_TYPES,
)


def render_admin_page() -> None:
    """Affiche le panneau d'administration réservé au rôle admin."""
    lang = st.session_state.get("language", "fr")
    if not require_role("admin"):
        st.error("Accès refusé. Cette page est réservée à l'équipe d'administration.")
        return

    current_admin = st.session_state["user"]
    render_logo_header(lang)
    render_simulation_banner(lang)

    st.markdown(f"### 🛡️ {get_text('admin', lang)} — Mziya Agadir")

    tabs = st.tabs(
        [
            f"📊 {get_text('statistics', lang)}",
            f"👥 {get_text('users', lang)}",
            f"🏪 {get_text('businesses', lang)}",
            f"💳 {get_text('transactions', lang)}",
            f"🎁 {get_text('rewards', lang)} & {get_text('promotions', lang)}",
            f"📩 {get_text('complaints', lang)}",
        ]
    )

    # 1. Statistiques générales
    with tabs[0]:
        kpis = get_admin_kpis()
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            render_stat_card("Clients", kpis["clients"])
        with k2:
            render_stat_card("Commerçants", kpis["merchants"])
        with k3:
            render_stat_card("Transactions", kpis["transactions"])
        with k4:
            render_stat_card("Points distribués", kpis["points_distributed"])
        with k5:
            render_stat_card("Récompenses utilisées", kpis["redemptions"])

        c1, c2 = st.columns(2)
        with c1:
            fig_roles = build_users_by_role_chart()
            if fig_roles is not None:
                st.plotly_chart(fig_roles, use_container_width=True)
        with c2:
            fig_nb = build_active_neighborhoods_chart()
            if fig_nb is not None:
                st.plotly_chart(fig_nb, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            fig_m = build_top_merchants_chart()
            if fig_m is not None:
                st.plotly_chart(fig_m, use_container_width=True)
        with c4:
            fig_ev = build_transactions_evolution_chart()
            if fig_ev is not None:
                st.plotly_chart(fig_ev, use_container_width=True)

    # 2. Gestion des utilisateurs (Clients & Commerçants)
    with tabs[1]:
        st.subheader(f"👥 {get_text('users', lang)}")

        add_c_col, add_m_col = st.columns(2)
        with add_c_col:
            with st.expander(f"➕ {get_text('add', lang)} un client", expanded=False):
                with st.form("admin_add_client_form", clear_on_submit=True):
                    c_name = st.text_input("Nom complet", key="adm_c_name")
                    c_email = st.text_input("Email", key="adm_c_email")
                    c_phone = st.text_input("Téléphone", key="adm_c_phone")
                    c_nb = st.selectbox("Quartier (Agadir)", AGADIR_NEIGHBORHOODS, key="adm_c_nb")
                    c_pw = st.text_input("Mot de passe", type="password", key="adm_c_pw")
                    if st.form_submit_button("Créer le client"):
                        ok, msg, _ = register_user(
                            full_name=c_name,
                            email=c_email,
                            phone=c_phone,
                            password=c_pw,
                            role="client",
                            neighborhood=c_nb,
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        with add_m_col:
            with st.expander(f"➕ {get_text('add', lang)} un commerçant", expanded=False):
                with st.form("admin_add_merchant_form", clear_on_submit=True):
                    m_name = st.text_input("Nom du gérant", key="adm_m_name")
                    m_email = st.text_input("Email", key="adm_m_email")
                    m_phone = st.text_input("Téléphone", key="adm_m_phone")
                    m_bname = st.text_input("Nom du commerce", key="adm_m_bname")
                    m_btype = st.selectbox("Type de commerce", BUSINESS_TYPES, key="adm_m_btype")
                    m_nb = st.selectbox("Quartier (Agadir)", AGADIR_NEIGHBORHOODS, key="adm_m_nb")
                    m_addr = st.text_input("Adresse", key="adm_m_addr")
                    m_pw = st.text_input("Mot de passe", type="password", key="adm_m_pw")
                    if st.form_submit_button("Créer le commerçant"):
                        ok, msg, _ = register_user(
                            full_name=m_name,
                            email=m_email,
                            phone=m_phone,
                            password=m_pw,
                            role="merchant",
                            neighborhood=m_nb,
                            business_name=m_bname,
                            business_type=m_btype,
                            address=m_addr,
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        role_filter = st.selectbox(
            "Filtrer par rôle",
            ["ALL", "client", "merchant", "admin"],
            key="adm_role_filter",
        )
        users = get_all_users(role=None if role_filter == "ALL" else role_filter)
        render_generic_table(
            users,
            [
                "id",
                "full_name",
                "email",
                "phone",
                "role",
                "neighborhood",
                "points_balance",
                "qr_code",
                "is_active",
            ],
            lang,
        )

        st.subheader("Désactiver / Réactiver un compte (avec confirmation)")
        manageable = [u for u in users if int(u["id"]) != int(current_admin["id"])]
        if manageable:
            u_map = {
                f"#{u['id']} — {u['full_name']} ({u['role']} • {'Actif' if int(u['is_active']) == 1 else 'Inactif'})": u
                for u in manageable
            }
            sel_label = st.selectbox("Sélectionner un utilisateur", list(u_map.keys()))
            target_u = u_map[sel_label]
            currently_active = int(target_u["is_active"]) == 1

            if currently_active:
                confirm_chk = st.checkbox(
                    f"Je confirme vouloir désactiver le compte de {target_u['full_name']} (aucune suppression définitive).",
                    key=f"confirm_dis_{target_u['id']}",
                )
                if st.button(
                    f"⛔ {get_text('disable', lang)}",
                    disabled=not confirm_chk,
                    key=f"btn_dis_{target_u['id']}",
                ):
                    ok, msg = set_user_active_status(target_u["id"], False)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                if st.button(
                    f"✅ {get_text('enable', lang)}",
                    key=f"btn_en_{target_u['id']}",
                ):
                    ok, msg = set_user_active_status(target_u["id"], True)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # 3. Commerces
    with tabs[2]:
        st.subheader(f"🏪 {get_text('businesses', lang)} — Agadir")
        merchants = get_all_merchants(active_only=False)
        render_generic_table(
            merchants,
            [
                "id",
                "business_name",
                "business_type",
                "neighborhood",
                "address",
                "owner_name",
                "owner_email",
                "phone",
                "is_active",
            ],
            lang,
        )

    # 4. Toutes les transactions
    with tabs[3]:
        st.subheader(f"💳 {get_text('transactions', lang)}")
        txs = get_all_transactions()
        render_transactions_table(txs, lang, include_client=True)

    # 5. Toutes les récompenses et promotions
    with tabs[4]:
        st.subheader(f"🎁 {get_text('rewards', lang)}")
        all_rewards = get_rewards(active_only=False)
        render_generic_table(
            all_rewards,
            [
                "id",
                "business_name",
                "neighborhood",
                "title",
                "points_required",
                "stock",
                "is_active",
            ],
            lang,
        )
        if all_rewards:
            rw_map = {f"#{r['id']} {r['title']} ({r['business_name']})": r for r in all_rewards}
            sel_rw = st.selectbox("Gérer une récompense", list(rw_map.keys()))
            rw_obj = rw_map[sel_rw]
            rw_act = int(rw_obj["is_active"]) == 1
            if st.button(
                get_text("disable", lang) if rw_act else get_text("enable", lang),
                key="adm_toggle_rw_btn",
            ):
                ok, msg = toggle_reward_status(rw_obj["id"], not rw_act)
                if ok:
                    st.success(msg)
                    st.rerun()

        st.divider()
        st.subheader(f"🔥 {get_text('promotions', lang)}")
        all_promos = get_promotions(active_only=False)
        render_generic_table(
            all_promos,
            [
                "id",
                "business_name",
                "neighborhood",
                "title",
                "discount_percentage",
                "start_date",
                "end_date",
                "is_active",
            ],
            lang,
        )
        if all_promos:
            pr_map = {f"#{p['id']} {p['title']} ({p['business_name']})": p for p in all_promos}
            sel_pr = st.selectbox("Gérer une promotion", list(pr_map.keys()))
            pr_obj = pr_map[sel_pr]
            pr_act = int(pr_obj["is_active"]) == 1
            if st.button(
                get_text("disable", lang) if pr_act else get_text("enable", lang),
                key="adm_toggle_pr_btn",
            ):
                ok, msg = toggle_promotion_status(pr_obj["id"], not pr_act)
                if ok:
                    st.success(msg)
                    st.rerun()

    # 6. Réclamations et messages
    with tabs[5]:
        st.subheader(f"📩 {get_text('complaints', lang)} & {get_text('messages', lang)}")
        f1, f2 = st.columns(2)
        with f1:
            t_filter = st.selectbox(
                get_text("message_type", lang),
                ["ALL"] + MESSAGE_TYPES,
                key="adm_msg_type_filter",
            )
        with f2:
            s_filter = st.selectbox(
                get_text("status", lang),
                ["ALL"] + MESSAGE_STATUSES,
                key="adm_msg_status_filter",
            )

        msgs = get_messages(message_type=t_filter, status=s_filter)
        if not msgs:
            st.info(get_text("no_results", lang))
        else:
            for m in msgs:
                with st.expander(
                    f"#{m['id']} [{m['message_type']}] {m['subject']} — {m['name']} ({m['status']})"
                ):
                    st.write(f"**De :** {m['name']} ({m['email']}) • **Date :** {m['created_at']}")
                    st.write(m["message"])
                    with st.form(f"adm_msg_form_{m['id']}"):
                        new_status = st.selectbox(
                            get_text("status", lang),
                            MESSAGE_STATUSES,
                            index=MESSAGE_STATUSES.index(m["status"])
                            if m["status"] in MESSAGE_STATUSES
                            else 0,
                            key=f"adm_ms_{m['id']}",
                        )
                        resp = st.text_area(
                            "Réponse interne / suivi",
                            value=m.get("admin_response", ""),
                            key=f"adm_mr_{m['id']}",
                        )
                        if st.form_submit_button(get_text("save", lang)):
                            ok, feedback = update_message_status(m["id"], new_status, resp)
                            if ok:
                                st.success(feedback)
                                st.rerun()
                            else:
                                st.error(feedback)
