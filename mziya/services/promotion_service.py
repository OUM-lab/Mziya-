"""Service de gestion des promotions locales (limitées à Agadir)."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from database.database import db_session
from utils.validators import (
    validate_date_range,
    validate_neighborhood,
    validate_required,
)


def create_promotion(
    merchant_id: int,
    title: str,
    description: str,
    discount_percentage: float,
    neighborhood: str,
    start_date: str,
    end_date: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Optional[int]]:
    """Crée une promotion locale rattachée à un quartier d'Agadir."""
    ok, err = validate_required(title, "Titre de la promotion")
    if not ok:
        return False, err, None

    ok, err = validate_neighborhood(neighborhood)
    if not ok:
        return False, err, None

    try:
        pct = float(discount_percentage)
    except (TypeError, ValueError):
        return False, "Pourcentage de réduction invalide.", None
    if pct <= 0 or pct > 100:
        return False, "Le pourcentage de réduction doit être compris entre 1 et 100.", None

    ok, err = validate_date_range(start_date, end_date)
    if not ok:
        return False, err, None

    with db_session(db_path) as conn:
        merchant = conn.execute(
            "SELECT id, is_active FROM merchants WHERE id = ?",
            (int(merchant_id),),
        ).fetchone()
        if merchant is None:
            return False, "Commerce introuvable.", None

        cursor = conn.execute(
            """
            INSERT INTO promotions (
                merchant_id, title, description, discount_percentage,
                neighborhood, start_date, end_date, is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                int(merchant_id),
                title.strip(),
                (description or "").strip(),
                round(pct, 2),
                neighborhood.strip(),
                str(start_date)[:10],
                str(end_date)[:10],
            ),
        )
        return True, "Promotion ajoutée avec succès.", int(cursor.lastrowid)


def update_promotion(
    promotion_id: int,
    merchant_id: int,
    title: str,
    description: str,
    discount_percentage: float,
    neighborhood: str,
    start_date: str,
    end_date: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Modifie une promotion existante du commerce."""
    ok, err = validate_required(title, "Titre de la promotion")
    if not ok:
        return False, err
    ok, err = validate_neighborhood(neighborhood)
    if not ok:
        return False, err
    try:
        pct = float(discount_percentage)
    except (TypeError, ValueError):
        return False, "Pourcentage de réduction invalide."
    if pct <= 0 or pct > 100:
        return False, "Le pourcentage doit être entre 1 et 100."
    ok, err = validate_date_range(start_date, end_date)
    if not ok:
        return False, err

    with db_session(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE promotions
            SET title = ?, description = ?, discount_percentage = ?,
                neighborhood = ?, start_date = ?, end_date = ?
            WHERE id = ? AND merchant_id = ?
            """,
            (
                title.strip(),
                (description or "").strip(),
                round(pct, 2),
                neighborhood.strip(),
                str(start_date)[:10],
                str(end_date)[:10],
                int(promotion_id),
                int(merchant_id),
            ),
        )
        if cursor.rowcount == 0:
            return False, "Promotion introuvable pour ce commerce."
    return True, "Promotion mise à jour avec succès."


def toggle_promotion_status(
    promotion_id: int,
    is_active: bool,
    merchant_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Active ou désactive une promotion."""
    flag = 1 if is_active else 0
    with db_session(db_path) as conn:
        if merchant_id is not None:
            cursor = conn.execute(
                "UPDATE promotions SET is_active = ? WHERE id = ? AND merchant_id = ?",
                (flag, int(promotion_id), int(merchant_id)),
            )
        else:
            cursor = conn.execute(
                "UPDATE promotions SET is_active = ? WHERE id = ?",
                (flag, int(promotion_id)),
            )
        if cursor.rowcount == 0:
            return False, "Promotion introuvable."
    return True, "Statut de la promotion mis à jour."


def get_promotions(
    neighborhood: Optional[str] = None,
    merchant_id: Optional[int] = None,
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Récupère les promotions d'Agadir avec filtres par quartier et commerce."""
    sql = """
        SELECT p.*, m.business_name, m.business_type
        FROM promotions p
        JOIN merchants m ON m.id = p.merchant_id
        WHERE 1=1
    """
    params: List[Any] = []
    if active_only:
        sql += " AND p.is_active = 1 AND m.is_active = 1"
    if neighborhood and neighborhood != "ALL":
        sql += " AND p.neighborhood = ?"
        params.append(neighborhood)
    if merchant_id is not None:
        sql += " AND p.merchant_id = ?"
        params.append(int(merchant_id))
    sql += " ORDER BY p.created_at DESC, p.id DESC"

    with db_session(db_path) as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]
