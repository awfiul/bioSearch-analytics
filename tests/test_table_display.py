import pandas as pd

from src.utils.table_display import (
    COLUMN_LABELS,
    get_default_display_columns,
    prepare_display_table,
)


def test_get_default_display_columns_keeps_only_available_columns() -> None:
    available_columns = ["query_id", "hit_id", "evalue", "unexpected"]

    assert get_default_display_columns(available_columns) == [
        "query_id",
        "hit_id",
        "evalue",
    ]


def test_prepare_display_table_selects_and_renames_columns() -> None:
    df = pd.DataFrame(
        {
            "query_id": ["query_1"],
            "hit_id": ["hit_1"],
            "evalue": [1e-5],
            "bitscore": [42],
        }
    )

    result = prepare_display_table(df, ["hit_id", "bitscore"])

    assert list(result.columns) == [
        COLUMN_LABELS["hit_id"],
        COLUMN_LABELS["bitscore"],
    ]
    assert result.iloc[0].tolist() == ["hit_1", 42]


def test_prepare_display_table_falls_back_when_selection_is_invalid() -> None:
    df = pd.DataFrame(
        {
            "query_id": ["query_1"],
            "hit_id": ["hit_1"],
            "evalue": [1e-5],
        }
    )

    result = prepare_display_table(df, ["missing"])

    assert list(result.columns) == ["Query ID", "Hit ID", "E-value"]
