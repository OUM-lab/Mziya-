"""Fixtures pytest communes utilisant une base SQLite temporaire."""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.database import init_db


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    """Crée une base SQLite temporaire isolée pour chaque test."""
    db_file = tmp_path / "test_mziya.db"
    init_db(db_file)
    return db_file
