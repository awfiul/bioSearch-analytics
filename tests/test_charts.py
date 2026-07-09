import pandas as pd

from src.visualization.charts import (
    calculate_evalue_threshold_counts,
    plot_alignment_length_vs_bitscore,
    plot_before_after_filtering,
    plot_evalue_distribution,
    plot_evalue_threshold_effect,
    plot_identity_distribution,
    plot_identity_vs_bitscore,
    plot_top_hits_by_bitscore,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "query_id": ["query_1", "query_1", "query_2"],
            "hit_id": ["hit_alpha", "hit_beta", "hit_gamma"],
            "evalue": [1e-50, 2e-10, 1e-3],
            "bitscore": [180, 95, 54],
            "identity_percent": [98.5, 76.2, 61.0],
            "alignment_length": [200, 160, 120],
        }
    )


def test_calculate_evalue_threshold_counts() -> None:
    result = calculate_evalue_threshold_counts(_sample_df(), [1, 1e-5, 1e-20])

    assert result["count"].tolist() == [3, 2, 1]


def test_plot_evalue_distribution_returns_histogram() -> None:
    fig = plot_evalue_distribution(_sample_df())

    assert len(fig.data) == 1
    assert fig.data[0].type == "histogram"


def test_plot_identity_distribution_returns_histogram() -> None:
    fig = plot_identity_distribution(_sample_df())

    assert len(fig.data) == 1
    assert fig.data[0].type == "histogram"


def test_plot_top_hits_by_bitscore_returns_bar() -> None:
    fig = plot_top_hits_by_bitscore(_sample_df(), top_n=2)

    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"


def test_plot_identity_vs_bitscore_returns_scatter() -> None:
    fig = plot_identity_vs_bitscore(_sample_df())

    assert len(fig.data) == 1
    assert fig.data[0].type == "scatter"


def test_plot_alignment_length_vs_bitscore_returns_scatter() -> None:
    fig = plot_alignment_length_vs_bitscore(_sample_df())

    assert len(fig.data) == 1
    assert fig.data[0].type == "scatter"


def test_plot_evalue_threshold_effect_returns_line() -> None:
    fig = plot_evalue_threshold_effect(_sample_df())

    assert len(fig.data) == 1
    assert fig.data[0].type == "scatter"


def test_plot_before_after_filtering_returns_bar() -> None:
    fig = plot_before_after_filtering(total_count=10, filtered_count=4)

    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"


def test_empty_chart_has_annotation() -> None:
    fig = plot_evalue_distribution(pd.DataFrame())

    assert len(fig.data) == 0
    assert len(fig.layout.annotations) == 1
