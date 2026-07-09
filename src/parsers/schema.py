"""Shared DataFrame schema for parsed BLAST results."""

from __future__ import annotations

import pandas as pd


UNIFIED_COLUMNS = [
    "query_id",
    "hit_id",
    "hit_description",
    "evalue",
    "bitscore",
    "score",
    "identity_percent",
    "alignment_length",
    "query_start",
    "query_end",
    "hit_start",
    "hit_end",
    "gaps",
    "coverage",
    "source_format",
]

NUMERIC_UNIFIED_COLUMNS = [
    "evalue",
    "bitscore",
    "score",
    "identity_percent",
    "alignment_length",
    "query_start",
    "query_end",
    "hit_start",
    "hit_end",
    "gaps",
    "coverage",
]


def ensure_unified_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with unified BLAST columns in stable order."""
    result = df.copy()

    for column in UNIFIED_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA

    for column in NUMERIC_UNIFIED_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    return result[UNIFIED_COLUMNS].reset_index(drop=True)
