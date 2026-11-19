"""Fonctions de formatage pour l'affichage dans Mziya."""

from datetime import datetime


def format_mad(amount: float) -> str:
    """Formate un montant en dirhams marocains (MAD)."""
    try:
        val = float(amount)
    except (TypeError, ValueError):
        val = 0.0
    return f"{val:,.2f} MAD".replace(",", " ")


def format_points(points: int) -> str:
    """Formate un nombre de points."""
    try:
        val = int(points)
    except (TypeError, ValueError):
        val = 0
    return f"{val} pts"


def format_datetime(dt_str: str) -> str:
    """Formate une date SQLite en format lisible JJ/MM/AAAA HH:MM."""
    if not dt_str:
        return "—"
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(str(dt_str)[:19], fmt)
            if fmt == "%Y-%m-%d":
                return dt.strftime("%d/%m/%Y")
            return dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            continue
    return str(dt_str)


def format_client_qr_id(user_id: int) -> str:
    """Construit l'identifiant QR non sensible du client."""
    return f"MZIYA-CLIENT-{int(user_id):04d}"
