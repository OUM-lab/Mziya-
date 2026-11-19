"""Fonctions de validation des entrées utilisateur et des règles d'Agadir."""

import re
from datetime import date, datetime
from typing import Optional, Tuple

from utils.constants import (
    AGADIR_NEIGHBORHOODS,
    ALLOWED_ROLES,
    MESSAGE_STATUSES,
    MESSAGE_TYPES,
)

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^(\+212|0)[5-7]\d{8}$")


def validate_required(value: Optional[str], field_label: str) -> Tuple[bool, str]:
    """Vérifie qu'un champ texte obligatoire n'est pas vide."""
    if value is None or not str(value).strip():
        return False, f"Le champ « {field_label} » est obligatoire."
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """Valide le format d'une adresse email."""
    cleaned = (email or "").strip()
    if not cleaned:
        return False, "L'adresse email est obligatoire."
    if not EMAIL_REGEX.match(cleaned):
        return False, "Format d'email invalide (ex. nom@exemple.ma)."
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Valide un numéro de téléphone marocain (+212XXXXXXXXX ou 0XXXXXXXXX)."""
    cleaned = re.sub(r"[\s\-.]", "", phone or "")
    if not cleaned:
        return False, "Le numéro de téléphone est obligatoire."
    if not PHONE_REGEX.match(cleaned):
        return (
            False,
            "Numéro de téléphone marocain invalide (ex. 0612345678 ou +212612345678).",
        )
    return True, ""


def normalize_phone(phone: str) -> str:
    """Nettoie un numéro de téléphone pour le stockage."""
    return re.sub(r"[\s\-.]", "", (phone or "").strip())


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Vérifie la robustesse minimale d'un mot de passe."""
    if not password or len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères."
    return True, ""


def validate_neighborhood(neighborhood: str) -> Tuple[bool, str]:
    """Vérifie que le quartier appartient exclusivement à Agadir."""
    if not neighborhood or neighborhood.strip() not in AGADIR_NEIGHBORHOODS:
        return (
            False,
            "Quartier invalide. Mziya est actuellement limitée aux quartiers d'Agadir.",
        )
    return True, ""


def validate_role(role: str) -> Tuple[bool, str]:
    """Vérifie que le rôle utilisateur est autorisé."""
    if role not in ALLOWED_ROLES:
        return False, "Rôle utilisateur invalide."
    return True, ""


def validate_positive_amount(amount: float, label: str = "Montant") -> Tuple[bool, str]:
    """Vérifie qu'un montant est strictement positif."""
    try:
        numeric = float(amount)
    except (TypeError, ValueError):
        return False, f"{label} invalide."
    if numeric <= 0:
        return False, f"{label} doit être strictement supérieur à 0."
    return True, ""


def validate_positive_int(value: int, label: str = "Valeur") -> Tuple[bool, str]:
    """Vérifie qu'un entier est strictement positif."""
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return False, f"{label} invalide."
    if numeric <= 0:
        return False, f"{label} doit être supérieur à 0."
    return True, ""


def validate_date_range(start_str: str, end_str: str) -> Tuple[bool, str]:
    """Vérifie que la date de fin est postérieure ou égale à la date de début."""
    try:
        start_d = date.fromisoformat(str(start_str)[:10])
        end_d = date.fromisoformat(str(end_str)[:10])
    except ValueError:
        return False, "Format de date invalide."
    if end_d < start_d:
        return False, "La date de fin doit être postérieure à la date de début."
    return True, ""


def validate_message_payload(
    name: str, email: str, subject: str, message_type: str, message: str
) -> Tuple[bool, str]:
    """Valide un message ou une réclamation avant enregistrement."""
    for val, label in (
        (name, "Nom"),
        (subject, "Sujet"),
        (message, "Message"),
    ):
        ok, err = validate_required(val, label)
        if not ok:
            return False, err
    ok, err = validate_email(email)
    if not ok:
        return False, err
    if message_type not in MESSAGE_TYPES:
        return False, "Type de message invalide."
    return True, ""


def validate_message_status(status: str) -> Tuple[bool, str]:
    """Vérifie que le statut d'un message est valide."""
    if status not in MESSAGE_STATUSES:
        return False, "Statut de message invalide."
    return True, ""


def parse_iso_date(value: Optional[str]) -> Optional[datetime]:
    """Convertit une date ISO en datetime si possible."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", ""))
    except ValueError:
        return None
