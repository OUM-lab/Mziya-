"""Service de gestion des points simulés, transactions et notifications."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from config import POINTS_PER_MAD_BLOCK
from database.database import db_session
from utils.validators import validate_positive_amount


def calculate_points(purchase_amount: float) -> int:
    """Calcule les points gagnés : 1 point par tranche de 10 MAD dépensés."""
    ok, err = validate_positive_amount(purchase_amount, "Montant de l'achat")
    if not ok:
        raise ValueError(err)
    return int(float(purchase_amount) // POINTS_PER_MAD_BLOCK)


def award_points(
    client_id: int,
    merchant_id: int,
    purchase_amount: float,
    description: str = "",
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Enregistre un achat simulé, attribue les points au client et crée une notification."""
    ok, err = validate_positive_amount(purchase_amount, "Montant de l'achat")
    if not ok:
        return False, err, {}

    points_earned = calculate_points(purchase_amount)
    clean_amount = round(float(purchase_amount), 2)
    clean_desc = (description or "Achat simulé en boutique").strip()

    with db_session(db_path) as conn:
        client = conn.execute(
            """
            SELECT id, full_name, role, points_balance, is_active
            FROM users
            WHERE id = ? AND role = 'client'
            """,
            (int(client_id),),
        ).fetchone()
        if client is None or int(client["is_active"]) != 1:
            return False, "Client introuvable ou inactif.", {}

        merchant = conn.execute(
            """
            SELECT id, business_name, is_active
            FROM merchants
            WHERE id = ?
            """,
            (int(merchant_id),),
        ).fetchone()
        if merchant is None or int(merchant["is_active"]) != 1:
            return False, "Commerce introuvable ou inactif.", {}

        new_balance = int(client["points_balance"]) + points_earned
        conn.execute(
            "UPDATE users SET points_balance = ? WHERE id = ?",
            (new_balance, int(client_id)),
        )

        tx_cursor = conn.execute(
            """
            INSERT INTO transactions (
                client_id, merchant_id, transaction_type, purchase_amount,
                points, description, status, is_simulation
            )
            VALUES (?, ?, 'earn', ?, ?, ?, 'completed', 1)
            """,
            (
                int(client_id),
                int(merchant_id),
                clean_amount,
                points_earned,
                clean_desc,
            ),
        )
        tx_id = int(tx_cursor.lastrowid)

        notif_title = f"+{points_earned} points simulés chez {merchant['business_name']}"
        notif_msg = (
            f"Achat simulé de {clean_amount:.2f} MAD enregistré ({clean_desc}). "
            f"Nouveau solde : {new_balance} pts."
        )
        conn.execute(
            """
            INSERT INTO notifications (user_id, title, message, notification_type, is_read)
            VALUES (?, ?, ?, 'points', 0)
            """,
            (int(client_id), notif_title, notif_msg),
        )

    return (
        True,
        f"Transaction simulée enregistrée : +{points_earned} points attribués.",
        {
            "transaction_id": tx_id,
            "points_earned": points_earned,
            "new_balance": new_balance,
            "purchase_amount": clean_amount,
            "is_simulation": True,
        },
    )


def search_clients(
    query: str = "",
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Recherche des clients par nom, email ou identifiant QR."""
    sql = """
        SELECT id, full_name, email, phone, neighborhood, points_balance, qr_code, is_active
        FROM users
        WHERE role = 'client'
    """
    params: List[Any] = []
    if active_only:
        sql += " AND is_active = 1"
    if query and query.strip():
        like_term = f"%{query.strip()}%"
        sql += " AND (full_name LIKE ? OR email LIKE ? OR qr_code LIKE ?)"
        params.extend([like_term, like_term, like_term])
    sql += " ORDER BY full_name ASC"

    with db_session(db_path) as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def get_client_transactions(
    client_id: int, db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Retourne l'historique des transactions d'un client."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT t.*, m.business_name, m.neighborhood
            FROM transactions t
            JOIN merchants m ON m.id = t.merchant_id
            WHERE t.client_id = ?
            ORDER BY t.created_at DESC, t.id DESC
            """,
            (int(client_id),),
        ).fetchall()
        return [dict(r) for r in rows]


def get_merchant_transactions(
    merchant_id: int, db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Retourne les transactions liées à un commerce spécifique."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT t.*, u.full_name AS client_name, u.qr_code AS client_qr
            FROM transactions t
            JOIN users u ON u.id = t.client_id
            WHERE t.merchant_id = ?
            ORDER BY t.created_at DESC, t.id DESC
            """,
            (int(merchant_id),),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_transactions(
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Retourne toutes les transactions simulées pour l'administration."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT t.*, u.full_name AS client_name, u.email AS client_email,
                   m.business_name, m.neighborhood
            FROM transactions t
            JOIN users u ON u.id = t.client_id
            JOIN merchants m ON m.id = t.merchant_id
            ORDER BY t.created_at DESC, t.id DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def get_client_notifications(
    user_id: int, db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Retourne les notifications d'un utilisateur."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (int(user_id),),
        ).fetchall()
        return [dict(r) for r in rows]


def mark_notifications_read(
    user_id: int, db_path: Optional[Union[str, Path]] = None
) -> None:
    """Marque toutes les notifications d'un utilisateur comme lues."""
    with db_session(db_path) as conn:
        conn.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ?",
            (int(user_id),),
        )
