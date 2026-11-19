"""Service de gestion des récompenses simulées, redemptions et cartes cadeaux simulées."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from database.database import db_session
from utils.constants import REWARD_TYPES
from utils.security import generate_unique_code
from utils.validators import (
    validate_positive_amount,
    validate_positive_int,
    validate_required,
)


def create_reward(
    merchant_id: int,
    title: str,
    description: str,
    points_required: int,
    discount_value: float,
    reward_type: str,
    stock: int,
    expiration_date: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Optional[int]]:
    """Ajoute une nouvelle récompense simulée pour un commerce."""
    ok, err = validate_required(title, "Titre de la récompense")
    if not ok:
        return False, err, None
    ok, err = validate_positive_int(points_required, "Points nécessaires")
    if not ok:
        return False, err, None
    if int(stock) < 0:
        return False, "Le stock ne peut pas être négatif.", None
    if float(discount_value) < 0:
        return False, "La valeur de réduction ne peut pas être négative.", None
    if reward_type not in REWARD_TYPES:
        reward_type = REWARD_TYPES[0]

    with db_session(db_path) as conn:
        merchant = conn.execute(
            "SELECT id, is_active FROM merchants WHERE id = ?",
            (int(merchant_id),),
        ).fetchone()
        if merchant is None:
            return False, "Commerce introuvable.", None

        cursor = conn.execute(
            """
            INSERT INTO rewards (
                merchant_id, title, description, points_required,
                discount_value, reward_type, stock, expiration_date, is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                int(merchant_id),
                title.strip(),
                (description or "").strip(),
                int(points_required),
                float(discount_value),
                reward_type,
                int(stock),
                str(expiration_date)[:10],
            ),
        )
        return True, "Récompense simulée ajoutée avec succès.", int(cursor.lastrowid)


def update_reward(
    reward_id: int,
    merchant_id: int,
    title: str,
    description: str,
    points_required: int,
    discount_value: float,
    reward_type: str,
    stock: int,
    expiration_date: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Met à jour une récompense appartenant au commerce."""
    ok, err = validate_required(title, "Titre de la récompense")
    if not ok:
        return False, err
    ok, err = validate_positive_int(points_required, "Points nécessaires")
    if not ok:
        return False, err
    if int(stock) < 0:
        return False, "Le stock ne peut pas être négatif."

    with db_session(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE rewards
            SET title = ?, description = ?, points_required = ?,
                discount_value = ?, reward_type = ?, stock = ?, expiration_date = ?
            WHERE id = ? AND merchant_id = ?
            """,
            (
                title.strip(),
                (description or "").strip(),
                int(points_required),
                float(discount_value),
                reward_type if reward_type in REWARD_TYPES else REWARD_TYPES[0],
                int(stock),
                str(expiration_date)[:10],
                int(reward_id),
                int(merchant_id),
            ),
        )
        if cursor.rowcount == 0:
            return False, "Récompense introuvable pour ce commerce."
    return True, "Récompense mise à jour avec succès."


def toggle_reward_status(
    reward_id: int,
    is_active: bool,
    merchant_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Active ou désactive une récompense."""
    flag = 1 if is_active else 0
    with db_session(db_path) as conn:
        if merchant_id is not None:
            cursor = conn.execute(
                "UPDATE rewards SET is_active = ? WHERE id = ? AND merchant_id = ?",
                (flag, int(reward_id), int(merchant_id)),
            )
        else:
            cursor = conn.execute(
                "UPDATE rewards SET is_active = ? WHERE id = ?",
                (flag, int(reward_id)),
            )
        if cursor.rowcount == 0:
            return False, "Récompense introuvable."
    return True, "Statut de la récompense mis à jour."


def get_rewards(
    merchant_id: Optional[int] = None,
    neighborhood: Optional[str] = None,
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Récupère les récompenses filtrées par commerce et/ou quartier d'Agadir."""
    sql = """
        SELECT r.*, m.business_name, m.neighborhood, m.business_type
        FROM rewards r
        JOIN merchants m ON m.id = r.merchant_id
        WHERE 1=1
    """
    params: List[Any] = []
    if active_only:
        sql += " AND r.is_active = 1 AND m.is_active = 1"
    if merchant_id is not None:
        sql += " AND r.merchant_id = ?"
        params.append(int(merchant_id))
    if neighborhood and neighborhood != "ALL":
        sql += " AND m.neighborhood = ?"
        params.append(neighborhood)
    sql += " ORDER BY r.points_required ASC, r.id DESC"

    with db_session(db_path) as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def redeem_reward(
    client_id: int,
    reward_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Utilise une récompense simulée en déduisant les points sans jamais permettre un solde négatif."""
    with db_session(db_path) as conn:
        client = conn.execute(
            """
            SELECT id, full_name, points_balance, is_active
            FROM users
            WHERE id = ? AND role = 'client'
            """,
            (int(client_id),),
        ).fetchone()
        if client is None or int(client["is_active"]) != 1:
            return False, "Client introuvable ou inactif.", {}

        reward = conn.execute(
            """
            SELECT r.*, m.business_name, m.is_active AS merchant_active
            FROM rewards r
            JOIN merchants m ON m.id = r.merchant_id
            WHERE r.id = ?
            """,
            (int(reward_id),),
        ).fetchone()
        if reward is None or int(reward["is_active"]) != 1 or int(reward["merchant_active"]) != 1:
            return False, "Cette récompense n'est plus disponible.", {}

        if int(reward["stock"]) <= 0:
            return False, "Stock épuisé pour cette récompense.", {}

        points_required = int(reward["points_required"])
        current_balance = int(client["points_balance"])
        if current_balance < points_required:
            return (
                False,
                f"Solde insuffisant ({current_balance} pts disponibles, {points_required} pts requis).",
                {},
            )

        new_balance = current_balance - points_required
        if new_balance < 0:
            return False, "Opération refusée : solde négatif interdit.", {}

        redemption_code = generate_unique_code("MZIYA-REW", 8)

        conn.execute(
            "UPDATE users SET points_balance = ? WHERE id = ?",
            (new_balance, int(client_id)),
        )
        conn.execute(
            "UPDATE rewards SET stock = stock - 1 WHERE id = ? AND stock > 0",
            (int(reward_id),),
        )

        red_cursor = conn.execute(
            """
            INSERT INTO redemptions (
                client_id, reward_id, points_used, redemption_code, status, is_simulation
            )
            VALUES (?, ?, ?, ?, 'simulated_issued', 1)
            """,
            (int(client_id), int(reward_id), points_required, redemption_code),
        )
        redemption_id = int(red_cursor.lastrowid)

        conn.execute(
            """
            INSERT INTO transactions (
                client_id, merchant_id, transaction_type, purchase_amount,
                points, description, status, is_simulation
            )
            VALUES (?, ?, 'redeem', 0, ?, ?, 'completed', 1)
            """,
            (
                int(client_id),
                int(reward["merchant_id"]),
                points_required,
                f"Utilisation récompense simulée : {reward['title']} ({redemption_code})",
            ),
        )

        conn.execute(
            """
            INSERT INTO notifications (user_id, title, message, notification_type, is_read)
            VALUES (?, ?, ?, 'reward', 0)
            """,
            (
                int(client_id),
                f"Récompense simulée obtenue : {reward['title']}",
                f"Code simulé : {redemption_code} chez {reward['business_name']}. Nouveau solde : {new_balance} pts.",
            ),
        )

    return (
        True,
        f"Récompense simulée obtenue ! Code : {redemption_code}",
        {
            "redemption_id": redemption_id,
            "redemption_code": redemption_code,
            "points_used": points_required,
            "new_balance": new_balance,
            "is_simulation": True,
        },
    )


def get_client_redemptions(
    client_id: int, db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Retourne les récompenses simulées obtenues par un client."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT rd.*, r.title AS reward_title, r.reward_type, m.business_name, m.neighborhood
            FROM redemptions rd
            JOIN rewards r ON r.id = rd.reward_id
            JOIN merchants m ON m.id = r.merchant_id
            WHERE rd.client_id = ?
            ORDER BY rd.redeemed_at DESC, rd.id DESC
            """,
            (int(client_id),),
        ).fetchall()
        return [dict(r) for r in rows]


def create_simulated_gift_card(
    merchant_id: int,
    amount: float,
    expiration_date: str,
    client_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Crée une carte cadeau simulée sans valeur monétaire réelle."""
    ok, err = validate_positive_amount(amount, "Montant de la carte cadeau")
    if not ok:
        return False, err, {}

    clean_amount = round(float(amount), 2)
    gift_code = generate_unique_code("MZIYA-GIFT", 8)

    with db_session(db_path) as conn:
        merchant = conn.execute(
            "SELECT id, business_name, is_active FROM merchants WHERE id = ?",
            (int(merchant_id),),
        ).fetchone()
        if merchant is None or int(merchant["is_active"]) != 1:
            return False, "Commerce introuvable ou inactif.", {}

        cursor = conn.execute(
            """
            INSERT INTO gift_cards (
                client_id, merchant_id, amount, gift_code, status, expiration_date, is_simulation
            )
            VALUES (?, ?, ?, ?, 'active', ?, 1)
            """,
            (
                int(client_id) if client_id is not None else None,
                int(merchant_id),
                clean_amount,
                gift_code,
                str(expiration_date)[:10],
            ),
        )
        card_id = int(cursor.lastrowid)

    return (
        True,
        f"Carte cadeau simulée créée ({gift_code}). Sans valeur monétaire réelle.",
        {
            "id": card_id,
            "gift_code": gift_code,
            "amount": clean_amount,
            "status": "active",
            "is_simulation": True,
        },
    )


def get_gift_cards(
    client_id: Optional[int] = None,
    merchant_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Liste les cartes cadeaux simulées."""
    sql = """
        SELECT g.*, m.business_name, m.neighborhood
        FROM gift_cards g
        JOIN merchants m ON m.id = g.merchant_id
        WHERE 1=1
    """
    params: List[Any] = []
    if client_id is not None:
        sql += " AND g.client_id = ?"
        params.append(int(client_id))
    if merchant_id is not None:
        sql += " AND g.merchant_id = ?"
        params.append(int(merchant_id))
    sql += " ORDER BY g.created_at DESC, g.id DESC"

    with db_session(db_path) as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def disable_gift_card(
    gift_card_id: int,
    client_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Désactive une carte cadeau simulée."""
    with db_session(db_path) as conn:
        if client_id is not None:
            cursor = conn.execute(
                "UPDATE gift_cards SET status = 'disabled' WHERE id = ? AND client_id = ?",
                (int(gift_card_id), int(client_id)),
            )
        else:
            cursor = conn.execute(
                "UPDATE gift_cards SET status = 'disabled' WHERE id = ?",
                (int(gift_card_id),),
            )
        if cursor.rowcount == 0:
            return False, "Carte cadeau introuvable."
    return True, "Carte cadeau simulée désactivée."
