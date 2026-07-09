"""Helpers for displaying BLAST result tables in the UI."""

from __future__ import annotations

import pandas as pd


DEFAULT_DISPLAY_COLUMNS = [
    "query_id",
    "hit_id",
    "hit_description",
    "evalue",
    "bitscore",
    "identity_percent",
    "alignment_length",
    "coverage",
    "query_start",
    "query_end",
    "hit_start",
    "hit_end",
]

COLUMN_LABELS = {
    "query_id": "Query ID",
    "hit_id": "Hit ID",
    "hit_description": "Hit description",
    "evalue": "E-value",
    "bitscore": "Bit score",
    "score": "Score",
    "identity_percent": "Identity, %",
    "alignment_length": "Alignment length",
    "query_start": "Query start",
    "query_end": "Query end",
    "hit_start": "Hit start",
    "hit_end": "Hit end",
    "gaps": "Gaps",
    "coverage": "Coverage, %",
    "source_format": "Source format",
}


def get_default_display_columns(available_columns: list[str]) -> list[str]:
    """Return default table columns that exist in a given DataFrame."""
    return [
        column for column in DEFAULT_DISPLAY_COLUMNS if column in available_columns
    ]


def prepare_display_table(
    df: pd.DataFrame,
    selected_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Return a UI-only table with selected columns and readable labels."""
    available_columns = list(df.columns)
    columns = selected_columns or get_default_display_columns(available_columns)
    safe_columns = [column for column in columns if column in available_columns]

    if not safe_columns:
        safe_columns = get_default_display_columns(available_columns)

    return df[safe_columns].rename(columns=COLUMN_LABELS)
