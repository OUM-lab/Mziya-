"""Configuration centrale de l'application Mziya."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "mziya.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
STYLE_PATH = BASE_DIR / "style.css"
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

APP_NAME = "Mziya"
APP_SLOGAN_FR = "Une carte, plusieurs commerces, plus d’avantages."
APP_CITY = "Agadir"
APP_COUNTRY = "Maroc"

POINTS_PER_MAD_BLOCK = 10  # 1 point par tranche de 10 MAD dépensés
DEFAULT_LANGUAGE = "fr"
SUPPORTED_LANGUAGES = ("fr", "en", "ar")
