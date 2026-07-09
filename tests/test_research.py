import pandas as pd
import pytest

from src.analysis.research import (
    calculate_correlations,
    calculate_filtering_efficiency,
    calculate_threshold_effect,
    generate_research_conclusions,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "evalue": [1e-50, 2e-10, 1e-3],
            "bitscore": [180, 95, 54],
            "identity_percent": [98.5, 76.2, 61.0],
            "alignment_length": [200, 160, 120],
        }
    )


def test_calculate_threshold_effect_counts_remaining_hits() -> None:
    result = calculate_threshold_effect(_sample_df(), [1, 1e-5, 1e-20])

    assert result["threshold"].tolist() == [1, 1e-5, 1e-20]
    assert result["count"].tolist() == [3, 2, 1]


def test_calculate_correlations_returns_values_for_enough_data() -> None:
    result = calculate_correlations(_sample_df())

    assert result["bitscore_identity_correlation"] > 0
    assert result["alignment_length_bitscore_correlation"] > 0


def test_calculate_correlations_returns_none_for_not_enough_data() -> None:
    result = calculate_correlations(_sample_df().head(1))

    assert result["bitscore_identity_correlation"] is None
    assert result["alignment_length_bitscore_correlation"] is None


def test_calculate_filtering_efficiency_uses_default_research_filter() -> None:
    result = calculate_filtering_efficiency(_sample_df())

    assert result["original_count"] == 3
    assert result["filtered_count"] == 2
    assert result["removed_count"] == 1
    assert result["removed_percent"] == pytest.approx(100 / 3)


def test_generate_research_conclusions_returns_text_blocks() -> None:
    conclusions = generate_research_conclusions(_sample_df())

    assert len(conclusions) == 4
    assert "E-value" in conclusions[0]
    assert "bitscore" in conclusions[1]
