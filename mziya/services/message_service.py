"""Service de gestion des messages, suggestions et réclamations."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from database.database import db_session
from utils.validators import validate_message_payload, validate_message_status


def create_message(
    name: str,
    email: str,
    subject: str,
    message_type: str,
    message: str,
    user_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Optional[int]]:
    """Enregistre un message, une question, une suggestion ou une réclamation."""
    ok, err = validate_message_payload(name, email, subject, message_type, message)
    if not ok:
        return False, err, None

    with db_session(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO messages (
                user_id, name, email, subject, message, message_type, status, admin_response
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Nouveau', '')
            """,
            (
                int(user_id) if user_id is not None else None,
                name.strip(),
                email.strip().lower(),
                subject.strip(),
                message.strip(),
                message_type,
            ),
        )
        return True, "Votre message a bien été enregistré.", int(cursor.lastrowid)


def get_messages(
    message_type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Liste les messages filtrés pour l'administration ou l'utilisateur."""
    sql = "SELECT * FROM messages WHERE 1=1"
    params: List[Any] = []
    if message_type and message_type != "ALL":
        sql += " AND message_type = ?"
        params.append(message_type)
    if status and status != "ALL":
        sql += " AND status = ?"
        params.append(status)
    if user_id is not None:
        sql += " AND user_id = ?"
        params.append(int(user_id))
    sql += " ORDER BY created_at DESC, id DESC"

    with db_session(db_path) as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def get_merchant_messages(
    business_name: str,
    owner_user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Retourne les messages envoyés par le commerçant ou mentionnant son commerce."""
    like_name = f"%{business_name.strip()}%" if business_name else "%"
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE user_id = ?
               OR lower(subject) LIKE lower(?)
               OR lower(message) LIKE lower(?)
            ORDER BY created_at DESC, id DESC
            """,
            (int(owner_user_id), like_name, like_name),
        ).fetchall()
        return [dict(r) for r in rows]


def update_message_status(
    message_id: int,
    status: str,
    admin_response: str = "",
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Met à jour le statut et la réponse interne d'un message (Administration)."""
    ok, err = validate_message_status(status)
    if not ok:
        return False, err

    with db_session(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE messages
            SET status = ?, admin_response = ?
            WHERE id = ?
            """,
            (status, (admin_response or "").strip(), int(message_id)),
        )
        if cursor.rowcount == 0:
            return False, "Message introuvable."
    return True, "Statut et réponse mis à jour."
