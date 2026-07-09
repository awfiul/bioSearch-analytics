"""Filtering helpers for unified BLAST result tables."""

from __future__ import annotations

import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    max_evalue: float | None = None,
    min_identity: float | None = None,
    min_bitscore: float | None = None,
    min_alignment_length: int | None = None,
    search_text: str | None = None,
    top_n: int | None = None,
) -> pd.DataFrame:
    """Apply user-selected filters to the unified DataFrame."""
    filtered_df = df.copy()

    if max_evalue is not None:
        filtered_df = _filter_numeric(filtered_df, "evalue", max_evalue, "le")

    if min_identity is not None:
        filtered_df = _filter_numeric(filtered_df, "identity_percent", min_identity, "ge")

    if min_bitscore is not None:
        filtered_df = _filter_numeric(filtered_df, "bitscore", min_bitscore, "ge")

    if min_alignment_length is not None:
        filtered_df = _filter_numeric(
            filtered_df,
            "alignment_length",
            min_alignment_length,
            "ge",
        )

    normalized_search = (search_text or "").strip()
    if normalized_search:
        filtered_df = _filter_by_text(filtered_df, normalized_search)

    if top_n is not None and top_n > 0:
        filtered_df = _top_n(filtered_df, top_n)

    return filtered_df.reset_index(drop=True)


def _filter_numeric(
    df: pd.DataFrame,
    column: str,
    threshold: float,
    operator: str,
) -> pd.DataFrame:
    if column not in df.columns:
        return df

    values = pd.to_numeric(df[column], errors="coerce")
    if operator == "le":
        return df[values <= threshold]
    if operator == "ge":
        return df[values >= threshold]

    raise ValueError(f"Unsupported filter operator: {operator}")


def _filter_by_text(df: pd.DataFrame, search_text: str) -> pd.DataFrame:
    searchable_columns = [
        column
        for column in ["query_id", "hit_id", "hit_description"]
        if column in df.columns
    ]
    if not searchable_columns:
        return df

    mask = pd.Series(False, index=df.index)
    for column in searchable_columns:
        mask = mask | df[column].fillna("").astype(str).str.contains(
            search_text,
            case=False,
            regex=False,
        )

    return df[mask]


def _top_n(df: pd.DataFrame, top_n: int) -> pd.DataFrame:
    if "bitscore" not in df.columns:
        return df.head(top_n)

    sorted_df = df.assign(
        _bitscore_sort=pd.to_numeric(df["bitscore"], errors="coerce")
    ).sort_values(
        by="_bitscore_sort",
        ascending=False,
        na_position="last",
    )
    return sorted_df.drop(columns=["_bitscore_sort"]).head(top_n)
