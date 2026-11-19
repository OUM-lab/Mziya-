"""Outils de sécurité : hachage de mots de passe et génération de codes uniques."""

import hashlib
import hmac
import os
import secrets

try:
    import bcrypt  # type: ignore

    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False


def hash_password(password: str) -> str:
    """Hache un mot de passe de manière sécurisée (bcrypt ou PBKDF2-SHA256)."""
    if not password or not isinstance(password, str):
        raise ValueError("Le mot de passe ne peut pas être vide.")
    if _HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    salt_bytes = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 200_000)
    return f"pbkdf2_sha256${salt_bytes.hex()}${dk.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie qu'un mot de passe correspond à son empreinte stockée."""
    if not password or not password_hash:
        return False
    try:
        if password_hash.startswith("$2"):
            if not _HAS_BCRYPT:
                return False
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        if password_hash.startswith("pbkdf2_sha256$"):
            _, salt_hex, hash_hex = password_hash.split("$", 2)
            salt_bytes = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(hash_hex)
            actual = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt_bytes, 200_000
            )
            return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
    return False


def generate_unique_code(prefix: str, length: int = 8) -> str:
    """Génère un code aléatoire lisible (pour récompenses ou cartes cadeaux simulées)."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    token = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}-{token}"
