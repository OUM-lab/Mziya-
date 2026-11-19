"""Tests d'authentification, de hachage, de rôles et de limitation à Agadir."""

from services.auth_service import (
    authenticate_user,
    hash_password,
    register_user,
    require_login,
    require_role,
    set_user_active_status,
    verify_password,
)
from utils.constants import AGADIR_NEIGHBORHOODS


def test_password_hashing_never_plaintext():
    pw = "SuperSecret123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert pw not in hashed
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPass!", hashed) is False


def test_register_client_and_login(temp_db):
    ok, msg, user = register_user(
        full_name="Amina Ouarzazi",
        email="amina@mziya.ma",
        phone="0612345678",
        password="Password123!",
        role="client",
        neighborhood="Talborjt",
        db_path=temp_db,
    )
    assert ok is True, msg
    assert user is not None
    assert user["qr_code"].startswith("MZIYA-CLIENT-")

    auth_ok, _, auth_user = authenticate_user("amina@mziya.ma", "Password123!", db_path=temp_db)
    assert auth_ok is True
    assert auth_user["email"] == "amina@mziya.ma"

    bad_ok, _, _ = authenticate_user("amina@mziya.ma", "BadPass", db_path=temp_db)
    assert bad_ok is False


def test_agadir_neighborhood_restriction(temp_db):
    assert "Centre-ville" in AGADIR_NEIGHBORHOODS
    assert "Casablanca" not in AGADIR_NEIGHBORHOODS

    ok, msg, _ = register_user(
        full_name="Test Hors Agadir",
        email="hors@mziya.ma",
        phone="0612345679",
        password="Password123!",
        role="client",
        neighborhood="Casablanca",
        db_path=temp_db,
    )
    assert ok is False
    assert "Agadir" in msg


def test_role_control_and_deactivation(temp_db):
    ok, _, merchant_user = register_user(
        full_name="Rachid Tazi",
        email="rachid@mziya.ma",
        phone="0611112222",
        password="Password123!",
        role="merchant",
        neighborhood="Founty",
        business_name="Épicerie Founty",
        business_type="Épicerie",
        address="Rue de la Plage, Agadir",
        db_path=temp_db,
    )
    assert ok is True

    fake_session = {"user": merchant_user}
    assert require_login(session_state=fake_session) is True
    assert require_role("merchant", session_state=fake_session) is True
    assert require_role("admin", session_state=fake_session) is False

    set_user_active_status(merchant_user["id"], False, db_path=temp_db)
    login_disabled, _, _ = authenticate_user("rachid@mziya.ma", "Password123!", db_path=temp_db)
    assert login_disabled is False
