"""Espace Commerçant Mziya — Gestion du commerce, points simulés, offres et statistiques."""

from datetime import date, timedelta

import streamlit as st

from components.cards import (
    render_contact_form,
    render_logo_header,
    render_simulation_banner,
    render_stat_card,
)
from components.charts import (
    build_transactions_evolution_chart,
    get_merchant_kpis,
)
from components.tables import render_generic_table, render_transactions_table
from services.auth_service import (
    get_merchant_by_owner,
    require_role,
    update_merchant_description,
)
from services.message_service import get_merchant_messages
from services.points_service import (
    award_points,
    calculate_points,
    get_merchant_transactions,
    search_clients,
)
from services.promotion_service import (
    create_promotion,
    get_promotions,
    toggle_promotion_status,
    update_promotion,
)
from services.reward_service import (
    create_reward,
    create_simulated_gift_card,
    disable_gift_card,
    get_gift_cards,
    get_rewards,
    toggle_reward_status,
    update_reward,
)
from translations import get_text
from utils.constants import AGADIR_NEIGHBORHOODS, REWARD_TYPES
from utils.formatting import format_mad


def render_merchant_page() -> None:
    """Affiche l'espace commerçant limité exclusivement à son propre commerce."""
    lang = st.session_state.get("language", "fr")
    if not require_role("merchant"):
        st.error("Accès refusé. Veuillez vous connecter avec un compte commerçant actif.")
        return

    user = st.session_state["user"]
    merchant = get_merchant_by_owner(int(user["id"]))
    if not merchant:
        st.error("Aucun commerce associé à ce compte.")
        return
    if int(merchant["is_active"]) != 1:
        st.error("Votre commerce est actuellement désactivé.")
        return

    merchant_id = int(merchant["id"])
    render_logo_header(lang)
    render_simulation_banner(lang)

    st.markdown(
        f"### 🏪 {merchant['business_name']} — 📍 {merchant['neighborhood']}, Agadir"
    )
    st.caption(f"Adresse : {merchant['address']} • Type : {merchant['business_type']}")

    tabs = st.tabs(
        [
            f"📊 {get_text('dashboard', lang)} & {get_text('statistics', lang)}",
            f"💳 {get_text('record_purchase', lang)}",
            f"🎁 {get_text('rewards', lang)}",
            f"🔥 {get_text('promotions', lang)}",
            f"🎟️ {get_text('gift_cards', lang)}",
            f"💬 {get_text('messages', lang)}",
            f"⚙️ {get_text('business', lang)}",
        ]
    )

    kpis = get_merchant_kpis(merchant_id)
    merchant_txs = get_merchant_transactions(merchant_id)

    # 1. Tableau de bord & Statistiques commerçant
    with tabs[0]:
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            render_stat_card("Clients fidèles", kpis["clients"])
        with k2:
            render_stat_card("Transactions", kpis["transactions"])
        with k3:
            render_stat_card("Points distribués", kpis["points_distributed"])
        with k4:
            render_stat_card("Récompenses utilisées", kpis["redemptions"])
        with k5:
            render_stat_card("Promotions actives", kpis["active_promotions"])

        fig = build_transactions_evolution_chart(merchant_id=merchant_id)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_text("no_results", lang))

        st.subheader("Historique des transactions de mon commerce")
        render_transactions_table(merchant_txs, lang, include_client=True)

    # 2. Enregistrer un achat simulé & attribuer des points
    with tabs[1]:
        st.subheader(f"💳 {get_text('record_purchase', lang)}")
        st.info("Règle de simulation : 1 point attribué par tranche de 10 MAD dépensés.")

        search_q = st.text_input(
            get_text("search_client", lang), key="merchant_client_search"
        )
        clients = search_clients(search_q, active_only=True)
        if not clients:
            st.warning("Aucun client actif trouvé.")
        else:
            client_labels = {
                f"{c['full_name']} ({c['qr_code']} • {c['neighborhood']} • {c['points_balance']} pts)": c[
                    "id"
                ]
                for c in clients
            }
            with st.form("merchant_award_points_form"):
                selected_client_label = st.selectbox(
                    get_text("client", lang), list(client_labels.keys())
                )
                amount = st.number_input(
                    get_text("amount_mad", lang),
                    min_value=1.0,
                    max_value=50000.0,
                    value=100.0,
                    step=10.0,
                )
                preview_pts = calculate_points(amount)
                st.caption(f"Aperçu des points simulés à attribuer : **{preview_pts} pts**")
                desc = st.text_input(
                    get_text("description", lang),
                    value="Achat simulé en magasin",
                )
                if st.form_submit_button(
                    "✅ Valider l'achat simulé et attribuer les points",
                    type="primary",
                    use_container_width=True,
                ):
                    ok, msg, _ = award_points(
                        client_id=client_labels[selected_client_label],
                        merchant_id=merchant_id,
                        purchase_amount=amount,
                        description=desc,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # 3. Récompenses (Ajouter, Modifier, Désactiver)
    with tabs[2]:
        st.subheader(f"🎁 {get_text('rewards', lang)}")
        with st.expander(f"➕ {get_text('add', lang)} une récompense simulée", expanded=False):
            with st.form("add_reward_form", clear_on_submit=True):
                r1, r2 = st.columns(2)
                with r1:
                    rw_title = st.text_input("Titre de la récompense")
                    rw_type = st.selectbox("Type de récompense", REWARD_TYPES)
                    rw_points = st.number_input(
                        "Points nécessaires", min_value=10, max_value=10000, value=100, step=10
                    )
                with r2:
                    rw_discount = st.number_input(
                        "Valeur simulée (MAD)", min_value=0.0, max_value=5000.0, value=10.0, step=5.0
                    )
                    rw_stock = st.number_input("Stock disponible", min_value=0, max_value=1000, value=20)
                    rw_exp = st.date_input(
                        "Date d'expiration", value=date.today() + timedelta(days=180)
                    )
                rw_desc = st.text_area(get_text("description", lang))
                if st.form_submit_button(get_text("save", lang), use_container_width=True):
                    ok, msg, _ = create_reward(
                        merchant_id=merchant_id,
                        title=rw_title,
                        description=rw_desc,
                        points_required=int(rw_points),
                        discount_value=float(rw_discount),
                        reward_type=rw_type,
                        stock=int(rw_stock),
                        expiration_date=rw_exp.isoformat(),
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        my_rewards = get_rewards(merchant_id=merchant_id, active_only=False)
        if my_rewards:
            for rw in my_rewards:
                status_txt = "Active" if int(rw["is_active"]) == 1 else "Désactivée"
                with st.expander(
                    f"🎁 {rw['title']} — {rw['points_required']} pts • Stock: {rw['stock']} ({status_txt})"
                ):
                    with st.form(f"edit_rw_form_{rw['id']}"):
                        e_title = st.text_input("Titre", value=rw["title"], key=f"rwt_{rw['id']}")
                        e_desc = st.text_area(
                            "Description", value=rw["description"], key=f"rwd_{rw['id']}"
                        )
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            e_pts = st.number_input(
                                "Points requis",
                                min_value=1,
                                value=int(rw["points_required"]),
                                key=f"rwp_{rw['id']}",
                            )
                        with c2:
                            e_val = st.number_input(
                                "Valeur (MAD)",
                                min_value=0.0,
                                value=float(rw["discount_value"]),
                                key=f"rwv_{rw['id']}",
                            )
                        with c3:
                            e_stock = st.number_input(
                                "Stock",
                                min_value=0,
                                value=int(rw["stock"]),
                                key=f"rws_{rw['id']}",
                            )
                        e_type = st.selectbox(
                            "Type",
                            REWARD_TYPES,
                            index=REWARD_TYPES.index(rw["reward_type"])
                            if rw["reward_type"] in REWARD_TYPES
                            else 0,
                            key=f"rwty_{rw['id']}",
                        )
                        e_exp = st.text_input(
                            "Expiration (YYYY-MM-DD)",
                            value=rw["expiration_date"],
                            key=f"rwe_{rw['id']}",
                        )
                        if st.form_submit_button(get_text("save", lang)):
                            ok, msg = update_reward(
                                rw["id"],
                                merchant_id,
                                e_title,
                                e_desc,
                                int(e_pts),
                                float(e_val),
                                e_type,
                                int(e_stock),
                                e_exp,
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                    is_act = int(rw["is_active"]) == 1
                    btn_label = get_text("disable", lang) if is_act else get_text("enable", lang)
                    if st.button(btn_label, key=f"toggle_rw_{rw['id']}"):
                        ok, msg = toggle_reward_status(rw["id"], not is_act, merchant_id=merchant_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info(get_text("no_results", lang))

    # 4. Promotions (Ajouter, Modifier, Désactiver)
    with tabs[3]:
        st.subheader(f"🔥 {get_text('promotions', lang)} — Agadir")
        with st.expander(f"➕ {get_text('add', lang)} une promotion locale", expanded=False):
            with st.form("add_promo_form", clear_on_submit=True):
                p1, p2 = st.columns(2)
                with p1:
                    p_title = st.text_input("Titre de la promotion")
                    p_pct = st.number_input(
                        "Réduction (%)", min_value=1.0, max_value=100.0, value=15.0, step=5.0
                    )
                    p_nb = st.selectbox(
                        f"{get_text('neighborhood', lang)} (Agadir)",
                        AGADIR_NEIGHBORHOODS,
                        index=AGADIR_NEIGHBORHOODS.index(merchant["neighborhood"])
                        if merchant["neighborhood"] in AGADIR_NEIGHBORHOODS
                        else 0,
                    )
                with p2:
                    p_start = st.date_input("Date de début", value=date.today())
                    p_end = st.date_input(
                        "Date d'expiration", value=date.today() + timedelta(days=30)
                    )
                p_desc = st.text_area(get_text("description", lang))
                if st.form_submit_button(get_text("save", lang), use_container_width=True):
                    ok, msg, _ = create_promotion(
                        merchant_id=merchant_id,
                        title=p_title,
                        description=p_desc,
                        discount_percentage=float(p_pct),
                        neighborhood=p_nb,
                        start_date=p_start.isoformat(),
                        end_date=p_end.isoformat(),
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        my_promos = get_promotions(merchant_id=merchant_id, active_only=False)
        if my_promos:
            for pr in my_promos:
                status_txt = "Active" if int(pr["is_active"]) == 1 else "Désactivée"
                with st.expander(
                    f"🔥 {pr['title']} (-{pr['discount_percentage']:.0f}% • {pr['neighborhood']}) — {status_txt}"
                ):
                    with st.form(f"edit_pr_form_{pr['id']}"):
                        ep_title = st.text_input("Titre", value=pr["title"], key=f"prt_{pr['id']}")
                        ep_desc = st.text_area(
                            "Description", value=pr["description"], key=f"prd_{pr['id']}"
                        )
                        c1, c2 = st.columns(2)
                        with c1:
                            ep_pct = st.number_input(
                                "Réduction (%)",
                                min_value=1.0,
                                max_value=100.0,
                                value=float(pr["discount_percentage"]),
                                key=f"prp_{pr['id']}",
                            )
                            ep_nb = st.selectbox(
                                "Quartier (Agadir)",
                                AGADIR_NEIGHBORHOODS,
                                index=AGADIR_NEIGHBORHOODS.index(pr["neighborhood"])
                                if pr["neighborhood"] in AGADIR_NEIGHBORHOODS
                                else 0,
                                key=f"prnb_{pr['id']}",
                            )
                        with c2:
                            ep_start = st.text_input(
                                "Date début (YYYY-MM-DD)",
                                value=pr["start_date"],
                                key=f"prs_{pr['id']}",
                            )
                            ep_end = st.text_input(
                                "Date fin (YYYY-MM-DD)",
                                value=pr["end_date"],
                                key=f"pre_{pr['id']}",
                            )
                        if st.form_submit_button(get_text("save", lang)):
                            ok, msg = update_promotion(
                                pr["id"],
                                merchant_id,
                                ep_title,
                                ep_desc,
                                float(ep_pct),
                                ep_nb,
                                ep_start,
                                ep_end,
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                    is_act = int(pr["is_active"]) == 1
                    btn_label = get_text("disable", lang) if is_act else get_text("enable", lang)
                    if st.button(btn_label, key=f"toggle_pr_{pr['id']}"):
                        ok, msg = toggle_promotion_status(
                            pr["id"], not is_act, merchant_id=merchant_id
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info(get_text("no_results", lang))

    # 5. Cartes cadeaux simulées
    with tabs[4]:
        st.subheader(f"🎟️ {get_text('gift_cards', lang)}")
        st.warning(f"ℹ️ {get_text('gift_card_disclaimer', lang)}")

        clients = search_clients("", active_only=True)
        with st.form("merchant_gift_card_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                c_opts = {None: "Carte générique (non attribuée)"}
                for c in clients:
                    c_opts[c["id"]] = f"{c['full_name']} ({c['qr_code']})"
                sel_client_id = st.selectbox(
                    get_text("client", lang),
                    list(c_opts.keys()),
                    format_func=lambda cid: c_opts[cid],
                )
            with c2:
                m_gc_amount = st.number_input(
                    get_text("amount_mad", lang),
                    min_value=10.0,
                    max_value=5000.0,
                    value=100.0,
                    step=10.0,
                )
            with c3:
                m_gc_exp = st.date_input(
                    "Date d'expiration",
                    value=date.today() + timedelta(days=180),
                    key="m_gc_exp",
                )
            if st.form_submit_button("➕ Générer une carte cadeau simulée", use_container_width=True):
                ok, msg, _ = create_simulated_gift_card(
                    merchant_id=merchant_id,
                    amount=m_gc_amount,
                    expiration_date=m_gc_exp.isoformat(),
                    client_id=sel_client_id,
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        m_cards = get_gift_cards(merchant_id=merchant_id)
        if m_cards:
            for gc in m_cards:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(
                        f"""
                        <div class="mziya-card">
                            <strong>🎟️ {gc['gift_code']}</strong> — Montant : <strong>{format_mad(gc['amount'])}</strong> • Statut : <code>{gc['status']}</code> • Expire : {gc['expiration_date']}<br/>
                            <small style="color:#b45309;">{get_text("gift_card_disclaimer", lang)}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_b:
                    if gc["status"] == "active":
                        if st.button(get_text("disable", lang), key=f"m_dis_gc_{gc['id']}"):
                            ok, msg = disable_gift_card(gc["id"])
                            if ok:
                                st.success(msg)
                                st.rerun()
        else:
            st.info(get_text("no_results", lang))

    # 6. Messages liés au commerce
    with tabs[5]:
        st.subheader(f"💬 Messages liés à {merchant['business_name']}")
        m_msgs = get_merchant_messages(merchant["business_name"], int(user["id"]))
        render_generic_table(
            m_msgs,
            ["id", "name", "email", "subject", "message_type", "message", "status", "admin_response", "created_at"],
            lang,
        )
        st.divider()
        render_contact_form(lang, current_user=user, key_prefix="merchant")

    # 7. Infos du commerce (Modifier la description)
    with tabs[6]:
        st.subheader(f"⚙️ {merchant['business_name']}")
        with st.form("merchant_info_form"):
            st.text_input("Quartier (Agadir)", value=merchant["neighborhood"], disabled=True)
            new_addr = st.text_input(get_text("address", lang), value=merchant["address"])
            new_phone = st.text_input(get_text("phone", lang), value=merchant["phone"])
            new_desc = st.text_area(
                get_text("description", lang), value=merchant["description"], height=120
            )
            if st.form_submit_button(
                f"💾 {get_text('save', lang)}",
                type="primary",
                use_container_width=True,
            ):
                ok, msg = update_merchant_description(
                    merchant_id, new_desc, phone=new_phone, address=new_addr
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
