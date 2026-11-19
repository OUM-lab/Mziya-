"""Gestion de la connexion SQLite et initialisation du schéma pour Mziya."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Union

from config import DATABASE_PATH, SCHEMA_PATH


def resolve_db_path(db_path: Optional[Union[str, Path]] = None) -> str:
    """Retourne le chemin vers la base SQLite sous forme de chaîne."""
    if db_path is None:
        return str(DATABASE_PATH)
    return str(db_path)


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """Ouvre une connexion SQLite configurée avec RowFactory et clés étrangères."""
    conn = sqlite3.connect(resolve_db_path(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_session(
    db_path: Optional[Union[str, Path]] = None,
) -> Iterator[sqlite3.Connection]:
    """Context manager gérant commit, rollback et fermeture de connexion."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[Union[str, Path]] = None) -> None:
    """Crée les tables et index SQLite à partir de schema.sql."""
    schema_sql = Path(SCHEMA_PATH).read_text(encoding="utf-8")
    with db_session(db_path) as conn:
        conn.executescript(schema_sql)
