import pandas as pd

from src.analysis.statistics import calculate_summary, format_metric_value


def test_calculate_summary_returns_core_metrics() -> None:
    df = pd.DataFrame(
        {
            "query_id": ["query_1", "query_1", "query_2"],
            "hit_id": ["hit_1", "hit_2", "hit_2"],
            "evalue": [1e-5, 1e-10, 0.1],
            "bitscore": [50, 120, 80],
            "identity_percent": [70.0, 90.0, 80.0],
            "alignment_length": [100, 200, 150],
        }
    )

    summary = calculate_summary(df)

    assert summary == {
        "total_hits": 3,
        "unique_queries": 2,
        "unique_hits": 2,
        "min_evalue": 1e-10,
        "max_bitscore": 120.0,
        "mean_identity_percent": 80.0,
        "mean_alignment_length": 150.0,
    }


def test_calculate_summary_handles_empty_dataframe() -> None:
    summary = calculate_summary(pd.DataFrame())

    assert summary == {
        "total_hits": 0,
        "unique_queries": 0,
        "unique_hits": 0,
        "min_evalue": None,
        "max_bitscore": None,
        "mean_identity_percent": None,
        "mean_alignment_length": None,
    }


def test_calculate_summary_ignores_non_numeric_values() -> None:
    df = pd.DataFrame(
        {
            "query_id": ["query_1"],
            "hit_id": ["hit_1"],
            "evalue": ["bad"],
            "bitscore": ["42"],
            "identity_percent": ["bad"],
            "alignment_length": ["100"],
        }
    )

    summary = calculate_summary(df)

    assert summary["min_evalue"] is None
    assert summary["max_bitscore"] == 42.0
    assert summary["mean_identity_percent"] is None
    assert summary["mean_alignment_length"] == 100.0


def test_format_metric_value_handles_missing_values() -> None:
    assert format_metric_value(None) == "N/A"


def test_format_metric_value_formats_small_numbers_scientifically() -> None:
    assert format_metric_value(1e-10) == "1.00e-10"


def test_format_metric_value_formats_percent_suffix() -> None:
    assert format_metric_value(87.456, "%") == "87.46%"
