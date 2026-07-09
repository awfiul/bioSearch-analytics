import pandas as pd

from src.parsers.schema import UNIFIED_COLUMNS, ensure_unified_schema


def test_ensure_unified_schema_adds_missing_columns_and_orders_them() -> None:
    df = pd.DataFrame(
        {
            "hit_id": ["hit_1"],
            "query_id": ["query_1"],
            "evalue": ["1e-5"],
            "bitscore": ["42"],
        }
    )

    result = ensure_unified_schema(df)

    assert list(result.columns) == UNIFIED_COLUMNS
    assert result.loc[0, "query_id"] == "query_1"
    assert result.loc[0, "hit_id"] == "hit_1"
    assert result.loc[0, "evalue"] == 1e-5
    assert result.loc[0, "bitscore"] == 42
    assert pd.isna(result.loc[0, "coverage"])
