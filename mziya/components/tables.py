"""Affichage structuré des tableaux Pandas dans Streamlit."""

from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from translations import get_text


def render_transactions_table(
    rows: List[Dict[str, Any]], language: str = "fr", include_client: bool = False
) -> None:
    """Affiche un tableau lisible des transactions simulées."""
    if not rows:
        st.info(get_text("no_results", language))
        return
    df = pd.DataFrame(rows)
    cols = [
        c
        for c in [
            "id",
            "client_name" if include_client else None,
            "business_name" if "business_name" in df.columns else None,
            "neighborhood" if "neighborhood" in df.columns else None,
            "transaction_type",
            "purchase_amount",
            "points",
            "description",
            "is_simulation",
            "created_at",
        ]
        if c and c in df.columns
    ]
    display_df = df[cols].copy()
    if "is_simulation" in display_df.columns:
        display_df["is_simulation"] = display_df["is_simulation"].map(
            lambda x: "Simulation" if int(x) == 1 else "Réel"
        )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_generic_table(
    rows: List[Dict[str, Any]], columns: List[str], language: str = "fr"
) -> None:
    """Affiche un tableau Pandas filtré sur les colonnes souhaitées."""
    if not rows:
        st.info(get_text("no_results", language))
        return
    df = pd.DataFrame(rows)
    available = [c for c in columns if c in df.columns]
    st.dataframe(df[available], use_container_width=True, hide_index=True)
