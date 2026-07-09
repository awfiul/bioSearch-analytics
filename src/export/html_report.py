"""HTML report generation."""

from __future__ import annotations

from datetime import datetime
from html import escape

import pandas as pd


def generate_html_report(
    original_df: pd.DataFrame,
    filtered_df: pd.DataFrame,
    filters: dict,
    summary: dict,
    conclusions: list[str] | None = None,
    filename: str | None = None,
    generated_at: datetime | None = None,
) -> str:
    """Generate a simple self-contained HTML report."""
    generated_at = generated_at or datetime.now()
    conclusions = conclusions or []
    top_hits = _top_hits(filtered_df)

    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="ru">',
            "<head>",
            '<meta charset="utf-8">',
            "<title>BLAST Results Report</title>",
            _styles(),
            "</head>",
            "<body>",
            "<h1>BLAST Results Report</h1>",
            f"<p><strong>Файл:</strong> {escape(filename or 'не указан')}</p>",
            f"<p><strong>Дата анализа:</strong> {generated_at:%Y-%m-%d %H:%M:%S}</p>",
            "<h2>Сводка</h2>",
            _summary_table(summary, len(original_df), len(filtered_df)),
            "<h2>Примененные фильтры</h2>",
            _filters_table(filters),
            "<h2>Top-10 результатов</h2>",
            top_hits.to_html(index=False, escape=True),
            "<h2>Краткие выводы</h2>",
            _conclusions_list(conclusions),
            "</body>",
            "</html>",
        ]
    )


def _top_hits(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    top_df = df.copy()
    if "bitscore" in top_df.columns:
        top_df["bitscore"] = pd.to_numeric(top_df["bitscore"], errors="coerce")
        top_df = top_df.sort_values("bitscore", ascending=False, na_position="last")

    columns = [
        column
        for column in [
            "query_id",
            "hit_id",
            "hit_description",
            "evalue",
            "bitscore",
            "identity_percent",
            "alignment_length",
            "coverage",
        ]
        if column in top_df.columns
    ]
    return top_df[columns].head(10)


def _summary_table(
    summary: dict,
    original_count: int,
    filtered_count: int,
) -> str:
    rows = {
        "Всего строк до фильтрации": original_count,
        "Строк после фильтрации": filtered_count,
        "Уникальных query": summary.get("unique_queries"),
        "Уникальных hit": summary.get("unique_hits"),
        "Лучший E-value": summary.get("min_evalue"),
        "Максимальный bitscore": summary.get("max_bitscore"),
        "Средний identity": summary.get("mean_identity_percent"),
        "Средняя длина": summary.get("mean_alignment_length"),
    }
    return _dict_table(rows)


def _filters_table(filters: dict) -> str:
    readable_filters = {
        key: ("не задан" if value in (None, "") else value)
        for key, value in filters.items()
    }
    return _dict_table(readable_filters)


def _dict_table(rows: dict) -> str:
    body = "\n".join(
        "<tr>"
        f"<th>{escape(str(key))}</th>"
        f"<td>{escape(str(value))}</td>"
        "</tr>"
        for key, value in rows.items()
    )
    return f"<table><tbody>{body}</tbody></table>"


def _conclusions_list(conclusions: list[str]) -> str:
    if not conclusions:
        return "<p>Выводы не сформированы.</p>"

    items = "\n".join(f"<li>{escape(conclusion)}</li>" for conclusion in conclusions)
    return f"<ul>{items}</ul>"


def _styles() -> str:
    return """
<style>
body { font-family: Arial, sans-serif; margin: 32px; color: #1f2933; }
table { border-collapse: collapse; width: 100%; margin: 12px 0 24px; }
th, td { border: 1px solid #d9e2ec; padding: 8px 10px; text-align: left; }
th { background: #f0f4f8; }
h1, h2 { color: #102a43; }
</style>
"""
