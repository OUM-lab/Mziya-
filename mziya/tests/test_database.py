"""Tests de la base SQLite, du seed idempotent, des messages et des traductions."""

from database.database import db_session
from database.seed import seed_database
from services.auth_service import authenticate_user
from services.message_service import create_message, get_messages, update_message_status
from translations import get_text


def test_schema_tables_created(temp_db):
    expected_tables = {
        "users",
        "merchants",
        "transactions",
        "rewards",
        "redemptions",
        "promotions",
        "gift_cards",
        "messages",
        "notifications",
    }
    with db_session(temp_db) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    found = {r["name"] for r in rows}
    assert expected_tables.issubset(found)


def test_seed_idempotency_and_demo_accounts(temp_db):
    seed_database(db_path=temp_db)
    with db_session(temp_db) as conn:
        u1 = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        t1 = conn.execute("SELECT COUNT(*) AS c FROM transactions").fetchone()["c"]

    # Deuxième exécution : aucun doublon créé
    seed_database(db_path=temp_db)
    with db_session(temp_db) as conn:
        u2 = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        t2 = conn.execute("SELECT COUNT(*) AS c FROM transactions").fetchone()["c"]

    assert u1 == u2
    assert t1 == t2

    for email, pw, role in (
        ("admin@mziya.ma", "Admin123!", "admin"),
        ("client@mziya.ma", "Client123!", "client"),
        ("merchant@mziya.ma", "Merchant123!", "merchant"),
    ):
        ok, _, user = authenticate_user(email, pw, db_path=temp_db)
        assert ok is True
        assert user["role"] == role


def test_messages_and_complaints_workflow(temp_db):
    empty_ok, _, _ = create_message(
        name="Ali",
        email="ali@mziya.ma",
        subject="Test",
        message_type="Réclamation",
        message="   ",
        db_path=temp_db,
    )
    assert empty_ok is False

    ok, _, msg_id = create_message(
        name="Ali",
        email="ali@mziya.ma",
        subject="Problème points",
        message_type="Réclamation",
        message="Mes points ne se sont pas affichés après mon passage.",
        db_path=temp_db,
    )
    assert ok is True
    assert msg_id is not None

    upd_ok, _ = update_message_status(
        msg_id, "Traité", "Points vérifiés et ajoutés en simulation.", db_path=temp_db
    )
    assert upd_ok is True

    msgs = get_messages(message_type="Réclamation", status="Traité", db_path=temp_db)
    assert len(msgs) == 1
    assert msgs[0]["admin_response"] == "Points vérifiés et ajoutés en simulation."


def test_multilingual_translations():
    assert get_text("home", "fr") == "Accueil"
    assert get_text("home", "en") == "Home"
    assert get_text("home", "ar") == "الرئيسية"
    assert get_text("Accueil", "en") == "Home"
