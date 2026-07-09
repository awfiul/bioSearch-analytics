"""Summary statistics for unified BLAST result tables."""

from __future__ import annotations

import math

import pandas as pd


def calculate_summary(df: pd.DataFrame) -> dict:
    """Calculate summary metrics for BLAST hits."""
    return {
        "total_hits": int(len(df)),
        "unique_queries": _nunique(df, "query_id"),
        "unique_hits": _nunique(df, "hit_id"),
        "min_evalue": _safe_min(df, "evalue"),
        "max_bitscore": _safe_max(df, "bitscore"),
        "mean_identity_percent": _safe_mean(df, "identity_percent"),
        "mean_alignment_length": _safe_mean(df, "alignment_length"),
    }


def calculate_correlations(df: pd.DataFrame) -> dict:
    """Calculate correlations used by the research section."""
    from src.analysis.research import calculate_correlations as _calculate_correlations

    return _calculate_correlations(df)


def calculate_threshold_effect(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate E-value threshold effect used by the research section."""
    from src.analysis.research import (
        calculate_threshold_effect as _calculate_threshold_effect,
    )

    return _calculate_threshold_effect(df)


def format_metric_value(value: int | float | None, suffix: str = "") -> str:
    """Format summary values for Streamlit metric cards."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"

    if isinstance(value, int):
        return f"{value}{suffix}"

    if value == 0:
        return f"0{suffix}"

    abs_value = abs(value)
    if abs_value < 0.001 or abs_value >= 1_000_000:
        return f"{value:.2e}{suffix}"

    return f"{value:.2f}{suffix}"


def _nunique(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns or df.empty:
        return 0
    return int(df[column].dropna().nunique())


def _safe_min(df: pd.DataFrame, column: str) -> float | None:
    series = _numeric_series(df, column)
    if series.empty:
        return None
    return float(series.min())


def _safe_max(df: pd.DataFrame, column: str) -> float | None:
    series = _numeric_series(df, column)
    if series.empty:
        return None
    return float(series.max())


def _safe_mean(df: pd.DataFrame, column: str) -> float | None:
    series = _numeric_series(df, column)
    if series.empty:
        return None
    return float(series.mean())


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns or df.empty:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce").dropna()
