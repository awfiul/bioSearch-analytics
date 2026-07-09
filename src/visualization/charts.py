"""Plotly chart builders for BLAST result analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


EVALUE_THRESHOLDS = [1, 1e-1, 1e-3, 1e-5, 1e-10, 1e-20, 1e-50]


def plot_evalue_distribution(df: pd.DataFrame) -> go.Figure:
    """Plot the distribution of -log10(E-value)."""
    values = _numeric_series(df, "evalue")
    values = values[values >= 0]
    if values.empty:
        return _empty_figure("Нет данных E-value для построения графика")

    transformed = -np.log10(values.clip(lower=1e-300))
    chart_df = pd.DataFrame({"-log10(E-value)": transformed})

    fig = px.histogram(
        chart_df,
        x="-log10(E-value)",
        nbins=30,
        title="Распределение E-value",
    )
    fig.update_layout(yaxis_title="Количество результатов")
    return fig


def plot_identity_distribution(df: pd.DataFrame) -> go.Figure:
    """Plot the distribution of identity percent."""
    values = _numeric_series(df, "identity_percent")
    if values.empty:
        return _empty_figure("Нет данных identity_percent для построения графика")

    chart_df = pd.DataFrame({"Identity, %": values})
    fig = px.histogram(
        chart_df,
        x="Identity, %",
        nbins=20,
        range_x=[0, 100],
        title="Распределение identity percent",
    )
    fig.update_layout(yaxis_title="Количество результатов")
    return fig


def plot_top_hits_by_bitscore(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Plot top hits ranked by bitscore."""
    if df.empty or "bitscore" not in df.columns:
        return _empty_figure("Нет данных bitscore для построения графика")

    chart_df = df.copy()
    chart_df["bitscore"] = pd.to_numeric(chart_df["bitscore"], errors="coerce")
    chart_df = chart_df.dropna(subset=["bitscore"]).sort_values(
        "bitscore",
        ascending=False,
    )
    chart_df = chart_df.head(top_n)
    if chart_df.empty:
        return _empty_figure("Нет числовых значений bitscore для построения графика")

    fig = px.bar(
        chart_df,
        x="bitscore",
        y="hit_id",
        orientation="h",
        title=f"Top {top_n} результатов по bitscore",
        labels={"bitscore": "Bit score", "hit_id": "Hit ID"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def plot_identity_vs_bitscore(df: pd.DataFrame) -> go.Figure:
    """Plot identity percent versus bitscore."""
    chart_df = _numeric_chart_df(df, ["identity_percent", "bitscore"])
    if chart_df.empty:
        return _empty_figure("Нет данных для графика identity vs bitscore")

    return px.scatter(
        chart_df,
        x="identity_percent",
        y="bitscore",
        hover_data=[column for column in ["query_id", "hit_id"] if column in chart_df],
        title="Identity percent vs bitscore",
        labels={"identity_percent": "Identity, %", "bitscore": "Bit score"},
    )


def plot_alignment_length_vs_bitscore(df: pd.DataFrame) -> go.Figure:
    """Plot alignment length versus bitscore."""
    chart_df = _numeric_chart_df(df, ["alignment_length", "bitscore"])
    if chart_df.empty:
        return _empty_figure("Нет данных для графика alignment length vs bitscore")

    return px.scatter(
        chart_df,
        x="alignment_length",
        y="bitscore",
        hover_data=[column for column in ["query_id", "hit_id"] if column in chart_df],
        title="Alignment length vs bitscore",
        labels={"alignment_length": "Alignment length", "bitscore": "Bit score"},
    )


def calculate_evalue_threshold_counts(
    df: pd.DataFrame,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    """Calculate remaining hit counts for several E-value thresholds."""
    thresholds = thresholds or EVALUE_THRESHOLDS
    values = _numeric_series(df, "evalue")

    return pd.DataFrame(
        {
            "threshold": thresholds,
            "count": [int((values <= threshold).sum()) for threshold in thresholds],
        }
    )


def plot_evalue_threshold_effect(df: pd.DataFrame) -> go.Figure:
    """Plot how E-value thresholds affect the number of remaining hits."""
    chart_df = calculate_evalue_threshold_counts(df)
    chart_df["threshold_label"] = chart_df["threshold"].map(_format_threshold)

    fig = px.line(
        chart_df,
        x="threshold_label",
        y="count",
        markers=True,
        title="Влияние порога E-value на количество результатов",
        labels={"threshold_label": "E-value threshold", "count": "Количество"},
    )
    return fig


def plot_before_after_filtering(total_count: int, filtered_count: int) -> go.Figure:
    """Plot the number of results before and after filtering."""
    chart_df = pd.DataFrame(
        {
            "stage": ["До фильтрации", "После фильтрации"],
            "count": [total_count, filtered_count],
        }
    )
    return px.bar(
        chart_df,
        x="stage",
        y="count",
        title="Количество результатов до и после фильтрации",
        labels={"stage": "Этап", "count": "Количество"},
    )


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns or df.empty:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce").dropna()


def _numeric_chart_df(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    chart_df = df.copy()
    for column in numeric_columns:
        if column not in chart_df.columns:
            return pd.DataFrame()
        chart_df[column] = pd.to_numeric(chart_df[column], errors="coerce")

    return chart_df.dropna(subset=numeric_columns)


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def _format_threshold(value: float) -> str:
    if value == 1:
        return "1"
    return f"{value:.0e}"
