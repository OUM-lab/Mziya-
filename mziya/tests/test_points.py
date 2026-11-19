"""Tests du système de calcul et d'attribution de points simulés et QR code."""

import pytest

from services.auth_service import get_user_by_id, register_user
from services.points_service import (
    award_points,
    calculate_points,
    get_client_notifications,
    get_client_transactions,
)
from services.qr_service import get_client_qr_payload


def test_calculate_points_rule():
    assert calculate_points(50) == 5
    assert calculate_points(100) == 10
    assert calculate_points(95) == 9
    with pytest.raises(ValueError):
        calculate_points(0)
    with pytest.raises(ValueError):
        calculate_points(-25)


def test_award_points_and_qr_payload(temp_db):
    _, _, client = register_user(
        full_name="Sara El Fassi",
        email="sara@mziya.ma",
        phone="0612340001",
        password="Password123!",
        role="client",
        neighborhood="Dakhla",
        db_path=temp_db,
    )
    _, _, merchant = register_user(
        full_name="Brahim",
        email="brahim@mziya.ma",
        phone="0612340002",
        password="Password123!",
        role="merchant",
        neighborhood="Dakhla",
        business_name="Supérette Dakhla",
        business_type="Supérette",
        address="Avenue des FAR, Agadir",
        db_path=temp_db,
    )

    qr_payload = get_client_qr_payload(client["id"], client["qr_code"])
    assert qr_payload.startswith("MZIYA-CLIENT-")
    assert "sara@mziya.ma" not in qr_payload

    ok, _, info = award_points(
        client["id"], merchant["merchant_id"], 120.0, "Achat test", db_path=temp_db
    )
    assert ok is True
    assert info["points_earned"] == 12
    assert info["new_balance"] == 12
    assert info["is_simulation"] is True

    updated_client = get_user_by_id(client["id"], db_path=temp_db)
    assert updated_client["points_balance"] == 12

    txs = get_client_transactions(client["id"], db_path=temp_db)
    assert len(txs) == 1
    assert txs[0]["is_simulation"] == 1

    notifs = get_client_notifications(client["id"], db_path=temp_db)
    assert len(notifs) == 1

    # Blocage montant négatif ou nul
    bad_ok, _, _ = award_points(
        client["id"], merchant["merchant_id"], -10.0, "Invalide", db_path=temp_db
    )
    assert bad_ok is False
    zero_ok, _, _ = award_points(
        client["id"], merchant["merchant_id"], 0.0, "Nul", db_path=temp_db
    )
    assert zero_ok is False
