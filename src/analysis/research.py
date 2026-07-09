"""Research-analysis helpers for BLAST result interpretation."""

from __future__ import annotations

import pandas as pd

from src.analysis.filtering import apply_filters


EVALUE_THRESHOLDS = [1, 1e-1, 1e-3, 1e-5, 1e-10, 1e-20, 1e-50]
DEFAULT_RESEARCH_FILTERS = {
    "max_evalue": 1e-5,
    "min_identity": 70,
    "min_alignment_length": 50,
}


def calculate_threshold_effect(
    df: pd.DataFrame,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    """Count how many hits remain under each E-value threshold."""
    thresholds = thresholds or EVALUE_THRESHOLDS
    evalues = _numeric_series(df, "evalue")

    return pd.DataFrame(
        {
            "threshold": thresholds,
            "count": [int((evalues <= threshold).sum()) for threshold in thresholds],
        }
    )


def calculate_correlations(df: pd.DataFrame) -> dict:
    """Calculate research correlations for key BLAST metrics."""
    return {
        "bitscore_identity_correlation": _safe_correlation(
            df,
            "bitscore",
            "identity_percent",
        ),
        "alignment_length_bitscore_correlation": _safe_correlation(
            df,
            "alignment_length",
            "bitscore",
        ),
    }


def calculate_filtering_efficiency(
    df: pd.DataFrame,
    filters: dict | None = None,
) -> dict:
    """Estimate how strongly a default combined filter reduces the data."""
    filters = filters or DEFAULT_RESEARCH_FILTERS
    filtered_df = apply_filters(df, **filters)
    original_count = int(len(df))
    filtered_count = int(len(filtered_df))
    removed_count = original_count - filtered_count
    removed_percent = (
        removed_count / original_count * 100 if original_count > 0 else None
    )

    return {
        "original_count": original_count,
        "filtered_count": filtered_count,
        "removed_count": removed_count,
        "removed_percent": removed_percent,
        "filters": filters,
    }


def generate_research_conclusions(df: pd.DataFrame) -> list[str]:
    """Generate short text conclusions for the research block."""
    conclusions = []
    threshold_effect = calculate_threshold_effect(df)
    correlations = calculate_correlations(df)
    filtering_efficiency = calculate_filtering_efficiency(df)

    conclusions.append(_threshold_conclusion(threshold_effect))
    conclusions.append(
        _correlation_conclusion(
            correlations["bitscore_identity_correlation"],
            "bitscore и identity percent",
        )
    )
    conclusions.append(
        _correlation_conclusion(
            correlations["alignment_length_bitscore_correlation"],
            "alignment length и bitscore",
        )
    )
    conclusions.append(_filtering_conclusion(filtering_efficiency))

    return conclusions


def _threshold_conclusion(threshold_effect: pd.DataFrame) -> str:
    if threshold_effect.empty:
        return "Недостаточно данных для анализа влияния порога E-value."

    first = threshold_effect.iloc[0]
    strict = threshold_effect[threshold_effect["threshold"] == 1e-10]
    if strict.empty:
        return "Влияние порога E-value рассчитано для доступных порогов."

    strict_count = int(strict.iloc[0]["count"])
    return (
        "При уменьшении порога E-value с "
        f"{_format_threshold(float(first['threshold']))} до 1e-10 "
        f"количество результатов изменилось с {int(first['count'])} "
        f"до {strict_count}."
    )


def _correlation_conclusion(value: float | None, label: str) -> str:
    if value is None:
        return f"Недостаточно данных для расчета корреляции между {label}."

    strength = "слабая"
    abs_value = abs(value)
    if abs_value >= 0.7:
        strength = "сильная"
    elif abs_value >= 0.3:
        strength = "умеренная"

    direction = "положительная" if value >= 0 else "отрицательная"
    return (
        f"Корреляция между {label}: {value:.2f}. "
        f"Это {strength} {direction} связь."
    )


def _filtering_conclusion(efficiency: dict) -> str:
    removed_percent = efficiency["removed_percent"]
    if removed_percent is None:
        return "Недостаточно данных для оценки эффективности фильтрации."

    return (
        "Комбинированный фильтр E-value <= 1e-5, identity >= 70%, "
        "alignment length >= 50 оставляет "
        f"{efficiency['filtered_count']} из {efficiency['original_count']} "
        f"результатов и удаляет {removed_percent:.2f}% строк."
    )


def _safe_correlation(
    df: pd.DataFrame,
    first_column: str,
    second_column: str,
) -> float | None:
    if first_column not in df.columns or second_column not in df.columns:
        return None

    values = df[[first_column, second_column]].apply(pd.to_numeric, errors="coerce")
    values = values.dropna()
    if len(values) < 2:
        return None

    correlation = values[first_column].corr(values[second_column])
    if pd.isna(correlation):
        return None
    return float(correlation)


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns or df.empty:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce").dropna()


def _format_threshold(value: float) -> str:
    if value == 1:
        return "1"
    return f"{value:.0e}"
