"""Service d'authentification, gestion des utilisateurs et contrôle d'accès."""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from database.database import db_session
from utils.constants import ALLOWED_ROLES, BUSINESS_TYPES
from utils.formatting import format_client_qr_id
from utils.security import hash_password, verify_password
from utils.validators import (
    normalize_phone,
    validate_email,
    validate_neighborhood,
    validate_password_strength,
    validate_phone,
    validate_required,
    validate_role,
)

__all__ = [
    "register_user",
    "authenticate_user",
    "hash_password",
    "verify_password",
    "logout_user",
    "require_login",
    "require_role",
    "get_user_by_id",
    "get_merchant_by_owner",
    "get_merchant_by_id",
    "get_all_merchants",
    "get_all_users",
    "set_user_active_status",
    "update_client_profile",
    "update_merchant_description",
]


def register_user(
    full_name: str,
    email: str,
    phone: str,
    password: str,
    role: str,
    neighborhood: str,
    language: str = "fr",
    business_name: str = "",
    business_type: str = "",
    address: str = "",
    description: str = "",
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Inscrit un nouvel utilisateur (client, commerçant ou admin) dans SQLite."""
    ok, err = validate_required(full_name, "Nom complet")
    if not ok:
        return False, err, None

    ok, err = validate_email(email)
    if not ok:
        return False, err, None

    ok, err = validate_phone(phone)
    if not ok:
        return False, err, None

    ok, err = validate_password_strength(password)
    if not ok:
        return False, err, None

    ok, err = validate_role(role)
    if not ok:
        return False, err, None

    ok, err = validate_neighborhood(neighborhood)
    if not ok:
        return False, err, None

    if role == "merchant":
        ok, err = validate_required(business_name, "Nom du commerce")
        if not ok:
            return False, err, None
        ok, err = validate_required(address, "Adresse du commerce")
        if not ok:
            return False, err, None
        if not business_type or business_type not in BUSINESS_TYPES:
            business_type = BUSINESS_TYPES[0]

    clean_email = email.strip().lower()
    clean_phone = normalize_phone(phone)
    clean_name = full_name.strip()
    clean_neighborhood = neighborhood.strip()
    clean_lang = language if language in ("fr", "en", "ar") else "fr"
    pw_hash = hash_password(password)

    try:
        with db_session(db_path) as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE lower(email) = ?",
                (clean_email,),
            ).fetchone()
            if existing is not None:
                return False, "Un compte existe déjà avec cette adresse email.", None

            cursor = conn.execute(
                """
                INSERT INTO users (
                    full_name, email, phone, password_hash, role,
                    language, neighborhood, points_balance, qr_code, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, 1)
                """,
                (
                    clean_name,
                    clean_email,
                    clean_phone,
                    pw_hash,
                    role,
                    clean_lang,
                    clean_neighborhood,
                ),
            )
            user_id = int(cursor.lastrowid)

            qr_code = format_client_qr_id(user_id) if role == "client" else None
            if qr_code:
                conn.execute(
                    "UPDATE users SET qr_code = ? WHERE id = ?",
                    (qr_code, user_id),
                )

            merchant_id = None
            if role == "merchant":
                m_cursor = conn.execute(
                    """
                    INSERT INTO merchants (
                        owner_user_id, business_name, business_type,
                        address, neighborhood, phone, description, is_active
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        user_id,
                        business_name.strip(),
                        business_type,
                        address.strip(),
                        clean_neighborhood,
                        clean_phone,
                        (description or "").strip(),
                    ),
                )
                merchant_id = int(m_cursor.lastrowid)

            user_row = conn.execute(
                """
                SELECT id, full_name, email, phone, role, language,
                       neighborhood, points_balance, qr_code, is_active, created_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
            user_dict = dict(user_row) if user_row else {"id": user_id}
            if merchant_id is not None:
                user_dict["merchant_id"] = merchant_id
            return True, "Compte créé avec succès.", user_dict
    except sqlite3.IntegrityError:
        return False, "Impossible de créer le compte (email déjà utilisé).", None


def authenticate_user(
    email: str,
    password: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authentifie un utilisateur actif par email et mot de passe."""
    if not email or not password:
        return False, "Veuillez saisir votre email et votre mot de passe.", None

    clean_email = email.strip().lower()
    with db_session(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, full_name, email, phone, password_hash, role, language,
                   neighborhood, points_balance, qr_code, is_active, created_at
            FROM users
            WHERE lower(email) = ?
            """,
            (clean_email,),
        ).fetchone()

        if row is None:
            return False, "Email ou mot de passe incorrect.", None

        if int(row["is_active"]) != 1:
            return False, "Ce compte a été désactivé. Contactez l'administration.", None

        if not verify_password(password, row["password_hash"]):
            return False, "Email ou mot de passe incorrect.", None

        user_dict = {
            "id": row["id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "phone": row["phone"],
            "role": row["role"],
            "language": row["language"],
            "neighborhood": row["neighborhood"],
            "points_balance": row["points_balance"],
            "qr_code": row["qr_code"],
            "is_active": row["is_active"],
            "created_at": row["created_at"],
        }
        if row["role"] == "merchant":
            merchant = conn.execute(
                "SELECT id, business_name FROM merchants WHERE owner_user_id = ?",
                (row["id"],),
            ).fetchone()
            if merchant:
                user_dict["merchant_id"] = merchant["id"]
                user_dict["business_name"] = merchant["business_name"]

        return True, "Connexion réussie.", user_dict


def logout_user() -> None:
    """Déconnecte l'utilisateur courant dans la session Streamlit."""
    import streamlit as st

    for key in ("user", "authenticated", "current_page"):
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["current_page"] = "home"


def require_login(session_state: Optional[Dict[str, Any]] = None) -> bool:
    """Vérifie qu'un utilisateur actif est connecté."""
    if session_state is None:
        import streamlit as st

        state = st.session_state
    else:
        state = session_state
    user = state.get("user")
    return bool(user and int(user.get("is_active", 0)) == 1)


def require_role(
    *allowed_roles: str,
    session_state: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie que l'utilisateur connecté possède l'un des rôles autorisés."""
    if session_state is None:
        import streamlit as st

        state = st.session_state
    else:
        state = session_state
    if not require_login(state):
        return False
    user = state.get("user", {})
    role = user.get("role")
    return role in ALLOWED_ROLES and role in allowed_roles


def get_user_by_id(
    user_id: int, db_path: Optional[Union[str, Path]] = None
) -> Optional[Dict[str, Any]]:
    """Retourne un utilisateur sans son hash de mot de passe."""
    with db_session(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, full_name, email, phone, role, language,
                   neighborhood, points_balance, qr_code, is_active, created_at
            FROM users
            WHERE id = ?
            """,
            (int(user_id),),
        ).fetchone()
        return dict(row) if row else None


def get_merchant_by_owner(
    owner_user_id: int, db_path: Optional[Union[str, Path]] = None
) -> Optional[Dict[str, Any]]:
    """Retourne le commerce rattaché à un compte commerçant."""
    with db_session(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM merchants WHERE owner_user_id = ?",
            (int(owner_user_id),),
        ).fetchone()
        return dict(row) if row else None


def get_merchant_by_id(
    merchant_id: int, db_path: Optional[Union[str, Path]] = None
) -> Optional[Dict[str, Any]]:
    """Retourne un commerce par son identifiant."""
    with db_session(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM merchants WHERE id = ?",
            (int(merchant_id),),
        ).fetchone()
        return dict(row) if row else None


def get_all_merchants(
    active_only: bool = False,
    neighborhood: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Liste les commerces inscrits à Agadir."""
    query = """
        SELECT m.*, u.full_name AS owner_name, u.email AS owner_email, u.is_active AS user_active
        FROM merchants m
        JOIN users u ON u.id = m.owner_user_id
        WHERE 1=1
    """
    params: List[Any] = []
    if active_only:
        query += " AND m.is_active = 1 AND u.is_active = 1"
    if neighborhood and neighborhood != "ALL":
        query += " AND m.neighborhood = ?"
        params.append(neighborhood)
    query += " ORDER BY m.business_name ASC"

    with db_session(db_path) as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def get_all_users(
    role: Optional[str] = None, db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Liste les utilisateurs pour l'administration."""
    query = """
        SELECT id, full_name, email, phone, role, language,
               neighborhood, points_balance, qr_code, is_active, created_at
        FROM users
        WHERE 1=1
    """
    params: List[Any] = []
    if role and role in ALLOWED_ROLES:
        query += " AND role = ?"
        params.append(role)
    query += " ORDER BY id DESC"

    with db_session(db_path) as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def set_user_active_status(
    user_id: int, is_active: bool, db_path: Optional[Union[str, Path]] = None
) -> Tuple[bool, str]:
    """Active ou désactive un utilisateur (et son commerce s'il est commerçant)."""
    flag = 1 if is_active else 0
    with db_session(db_path) as conn:
        row = conn.execute(
            "SELECT id, role FROM users WHERE id = ?",
            (int(user_id),),
        ).fetchone()
        if row is None:
            return False, "Utilisateur introuvable."
        conn.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (flag, int(user_id)),
        )
        if row["role"] == "merchant":
            conn.execute(
                "UPDATE merchants SET is_active = ? WHERE owner_user_id = ?",
                (flag, int(user_id)),
            )
    msg = "Compte réactivé avec succès." if is_active else "Compte désactivé avec succès."
    return True, msg


def update_client_profile(
    user_id: int,
    full_name: str,
    phone: str,
    neighborhood: str,
    language: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Met à jour les informations autorisées du profil client."""
    ok, err = validate_required(full_name, "Nom complet")
    if not ok:
        return False, err
    ok, err = validate_phone(phone)
    if not ok:
        return False, err
    ok, err = validate_neighborhood(neighborhood)
    if not ok:
        return False, err

    clean_lang = language if language in ("fr", "en", "ar") else "fr"
    with db_session(db_path) as conn:
        conn.execute(
            """
            UPDATE users
            SET full_name = ?, phone = ?, neighborhood = ?, language = ?
            WHERE id = ? AND role = 'client'
            """,
            (
                full_name.strip(),
                normalize_phone(phone),
                neighborhood.strip(),
                clean_lang,
                int(user_id),
            ),
        )
    return True, "Profil mis à jour avec succès."


def update_merchant_description(
    merchant_id: int,
    description: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """Permet au commerçant de mettre à jour la description et les coordonnées de son commerce."""
    with db_session(db_path) as conn:
        if phone is not None and phone.strip():
            ok, err = validate_phone(phone)
            if not ok:
                return False, err
            clean_phone = normalize_phone(phone)
        else:
            row = conn.execute(
                "SELECT phone FROM merchants WHERE id = ?", (int(merchant_id),)
            ).fetchone()
            clean_phone = row["phone"] if row else ""

        if address is not None:
            ok, err = validate_required(address, "Adresse")
            if not ok:
                return False, err
            clean_address = address.strip()
        else:
            row = conn.execute(
                "SELECT address FROM merchants WHERE id = ?", (int(merchant_id),)
            ).fetchone()
            clean_address = row["address"] if row else ""

        conn.execute(
            """
            UPDATE merchants
            SET description = ?, phone = ?, address = ?
            WHERE id = ?
            """,
            ((description or "").strip(), clean_phone, clean_address, int(merchant_id)),
        )
    return True, "Informations du commerce mises à jour."
