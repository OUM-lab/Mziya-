"""Tests des récompenses simulées, promotions d'Agadir et cartes cadeaux simulées."""

from services.auth_service import get_user_by_id, register_user
from services.points_service import award_points
from services.promotion_service import create_promotion, get_promotions
from services.reward_service import (
    create_reward,
    create_simulated_gift_card,
    disable_gift_card,
    get_gift_cards,
    redeem_reward,
)


def _setup_client_and_merchant(temp_db):
    _, _, client = register_user(
        full_name="Mounir Idrissi",
        email="mounir@mziya.ma",
        phone="0612340010",
        password="Password123!",
        role="client",
        neighborhood="Anza",
        db_path=temp_db,
    )
    _, _, merchant = register_user(
        full_name="Latifa",
        email="latifa@mziya.ma",
        phone="0612340011",
        password="Password123!",
        role="merchant",
        neighborhood="Anza",
        business_name="Boulangerie Anza",
        business_type="Boulangerie & Pâtisserie",
        address="Route d'Essaouira, Anza, Agadir",
        db_path=temp_db,
    )
    return client, merchant


def test_redeem_reward_and_block_negative_balance(temp_db):
    client, merchant = _setup_client_and_merchant(temp_db)
    ok_rw, _, rw_id = create_reward(
        merchant_id=merchant["merchant_id"],
        title="Réduction simulée 10 MAD",
        description="Test récompense",
        points_required=100,
        discount_value=10.0,
        reward_type="Réduction immédiate",
        stock=2,
        expiration_date="2027-12-31",
        db_path=temp_db,
    )
    assert ok_rw is True

    # Solde insuffisant (0 < 100) -> bloqué
    fail_ok, fail_msg, _ = redeem_reward(client["id"], rw_id, db_path=temp_db)
    assert fail_ok is False
    assert "insuffisant" in fail_msg.lower()

    # On crédite 120 points (1200 MAD)
    award_points(client["id"], merchant["merchant_id"], 1200.0, "Gros achat", db_path=temp_db)
    ok_red, _, red_info = redeem_reward(client["id"], rw_id, db_path=temp_db)
    assert ok_red is True
    assert red_info["new_balance"] == 20
    assert red_info["redemption_code"].startswith("MZIYA-REW-")

    fresh_client = get_user_by_id(client["id"], db_path=temp_db)
    assert fresh_client["points_balance"] == 20


def test_promotions_agadir_and_filtering(temp_db):
    _, merchant = _setup_client_and_merchant(temp_db)

    bad_ok, bad_msg, _ = create_promotion(
        merchant_id=merchant["merchant_id"],
        title="Promo hors zone",
        description="Test",
        discount_percentage=15.0,
        neighborhood="Rabat",
        start_date="2026-01-01",
        end_date="2026-12-31",
        db_path=temp_db,
    )
    assert bad_ok is False
    assert "Agadir" in bad_msg

    ok_p, _, _ = create_promotion(
        merchant_id=merchant["merchant_id"],
        title="Promo Anza",
        description="Remise locale",
        discount_percentage=20.0,
        neighborhood="Anza",
        start_date="2026-01-01",
        end_date="2027-12-31",
        db_path=temp_db,
    )
    assert ok_p is True

    anza_promos = get_promotions(neighborhood="Anza", db_path=temp_db)
    assert len(anza_promos) == 1
    assert anza_promos[0]["title"] == "Promo Anza"

    founty_promos = get_promotions(neighborhood="Founty", db_path=temp_db)
    assert len(founty_promos) == 0


def test_simulated_gift_card_lifecycle(temp_db):
    client, merchant = _setup_client_and_merchant(temp_db)
    ok, _, card = create_simulated_gift_card(
        merchant_id=merchant["merchant_id"],
        amount=200.0,
        expiration_date="2027-12-31",
        client_id=client["id"],
        db_path=temp_db,
    )
    assert ok is True
    assert card["gift_code"].startswith("MZIYA-GIFT-")
    assert card["is_simulation"] is True

    cards = get_gift_cards(client_id=client["id"], db_path=temp_db)
    assert len(cards) == 1
    assert cards[0]["status"] == "active"

    dis_ok, _ = disable_gift_card(cards[0]["id"], client_id=client["id"], db_path=temp_db)
    assert dis_ok is True
    cards_after = get_gift_cards(client_id=client["id"], db_path=temp_db)
    assert cards_after[0]["status"] == "disabled"
