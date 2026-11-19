"""Statistiques et graphiques Pandas / Plotly alimentés par SQLite."""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd
import plotly.express as px

from database.database import db_session


def get_admin_kpis(db_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Calcule les indicateurs globaux réels depuis SQLite."""
    with db_session(db_path) as conn:
        clients = conn.execute(
            "SELECT COUNT(*) AS cnt FROM users WHERE role = 'client'"
        ).fetchone()["cnt"]
        merchants = conn.execute(
            "SELECT COUNT(*) AS cnt FROM merchants"
        ).fetchone()["cnt"]
        transactions = conn.execute(
            "SELECT COUNT(*) AS cnt FROM transactions"
        ).fetchone()["cnt"]
        points_dist = conn.execute(
            "SELECT COALESCE(SUM(points), 0) AS total FROM transactions WHERE transaction_type = 'earn'"
        ).fetchone()["total"]
        redemptions = conn.execute(
            "SELECT COUNT(*) AS cnt FROM redemptions"
        ).fetchone()["cnt"]
    return {
        "clients": int(clients),
        "merchants": int(merchants),
        "transactions": int(transactions),
        "points_distributed": int(points_dist),
        "redemptions": int(redemptions),
    }


def get_merchant_kpis(
    merchant_id: int, db_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Calcule les indicateurs réels d'un commerce depuis SQLite."""
    with db_session(db_path) as conn:
        clients = conn.execute(
            "SELECT COUNT(DISTINCT client_id) AS cnt FROM transactions WHERE merchant_id = ?",
            (int(merchant_id),),
        ).fetchone()["cnt"]
        transactions = conn.execute(
            "SELECT COUNT(*) AS cnt FROM transactions WHERE merchant_id = ?",
            (int(merchant_id),),
        ).fetchone()["cnt"]
        points_dist = conn.execute(
            """
            SELECT COALESCE(SUM(points), 0) AS total
            FROM transactions
            WHERE merchant_id = ? AND transaction_type = 'earn'
            """,
            (int(merchant_id),),
        ).fetchone()["total"]
        redemptions = conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM redemptions rd
            JOIN rewards r ON r.id = rd.reward_id
            WHERE r.merchant_id = ?
            """,
            (int(merchant_id),),
        ).fetchone()["cnt"]
        active_promos = conn.execute(
            "SELECT COUNT(*) AS cnt FROM promotions WHERE merchant_id = ? AND is_active = 1",
            (int(merchant_id),),
        ).fetchone()["cnt"]
    return {
        "clients": int(clients),
        "transactions": int(transactions),
        "points_distributed": int(points_dist),
        "redemptions": int(redemptions),
        "active_promotions": int(active_promos),
    }


def build_users_by_role_chart(db_path: Optional[Union[str, Path]] = None):
    """Graphique de répartition des utilisateurs par rôle."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            "SELECT role, COUNT(*) AS count FROM users GROUP BY role"
        ).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return None
    fig = px.pie(
        df,
        names="role",
        values="count",
        title="Répartition des utilisateurs par rôle",
        color_discrete_sequence=["#0f2942", "#0ea5a4", "#f97316"],
        hole=0.45,
    )
    fig.update_layout(margin=dict(t=45, b=15, l=15, r=15))
    return fig


def build_active_neighborhoods_chart(db_path: Optional[Union[str, Path]] = None):
    """Graphique des quartiers d'Agadir les plus actifs en transactions."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT m.neighborhood AS neighborhood, COUNT(t.id) AS transactions
            FROM transactions t
            JOIN merchants m ON m.id = t.merchant_id
            GROUP BY m.neighborhood
            ORDER BY transactions DESC
            """
        ).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return None
    fig = px.bar(
        df,
        x="neighborhood",
        y="transactions",
        title="Quartiers d'Agadir les plus actifs",
        labels={"neighborhood": "Quartier", "transactions": "Transactions simulées"},
        color_discrete_sequence=["#0ea5a4"],
    )
    fig.update_layout(margin=dict(t=45, b=20, l=15, r=15))
    return fig


def build_top_merchants_chart(db_path: Optional[Union[str, Path]] = None):
    """Graphique des commerces les plus actifs d'Agadir."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT m.business_name AS commerce,
                   COUNT(t.id) AS transactions,
                   COALESCE(SUM(CASE WHEN t.transaction_type = 'earn' THEN t.points ELSE 0 END), 0) AS points
            FROM merchants m
            LEFT JOIN transactions t ON t.merchant_id = m.id
            GROUP BY m.id, m.business_name
            ORDER BY transactions DESC
            """
        ).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return None
    fig = px.bar(
        df,
        x="commerce",
        y="transactions",
        title="Commerces les plus actifs",
        labels={"commerce": "Commerce", "transactions": "Transactions"},
        color_discrete_sequence=["#0f2942"],
    )
    fig.update_layout(margin=dict(t=45, b=20, l=15, r=15))
    return fig


def build_transactions_evolution_chart(
    merchant_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
):
    """Évolution des transactions simulées dans le temps (global ou par commerce)."""
    sql = """
        SELECT substr(created_at, 1, 10) AS date,
               COUNT(*) AS transactions,
               COALESCE(SUM(points), 0) AS points
        FROM transactions
    """
    params = ()
    if merchant_id is not None:
        sql += " WHERE merchant_id = ?"
        params = (int(merchant_id),)
    sql += " GROUP BY substr(created_at, 1, 10) ORDER BY date ASC"

    with db_session(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return None
    fig = px.line(
        df,
        x="date",
        y="transactions",
        markers=True,
        title="Évolution des transactions simulées",
        labels={"date": "Date", "transactions": "Nombre de transactions"},
        color_discrete_sequence=["#f97316"],
    )
    fig.update_layout(margin=dict(t=45, b=20, l=15, r=15))
    return fig
