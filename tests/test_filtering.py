import pandas as pd

from src.analysis.filtering import apply_filters


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "query_id": ["query_1", "query_1", "query_2"],
            "hit_id": ["hit_alpha", "hit_beta", "hit_gamma"],
            "hit_description": [
                "alpha kinase",
                "beta transferase",
                "gamma protein",
            ],
            "evalue": [1e-50, 2e-10, 1e-3],
            "bitscore": [180, 95, 54],
            "identity_percent": [98.5, 76.2, 61.0],
            "alignment_length": [200, 160, 120],
        }
    )


def test_apply_filters_by_max_evalue() -> None:
    result = apply_filters(_sample_df(), max_evalue=1e-20)

    assert result["hit_id"].tolist() == ["hit_alpha"]


def test_apply_filters_by_min_identity() -> None:
    result = apply_filters(_sample_df(), min_identity=70)

    assert result["hit_id"].tolist() == ["hit_alpha", "hit_beta"]


def test_apply_filters_by_min_bitscore() -> None:
    result = apply_filters(_sample_df(), min_bitscore=100)

    assert result["hit_id"].tolist() == ["hit_alpha"]


def test_apply_filters_by_min_alignment_length() -> None:
    result = apply_filters(_sample_df(), min_alignment_length=150)

    assert result["hit_id"].tolist() == ["hit_alpha", "hit_beta"]


def test_apply_filters_by_search_text_case_insensitive() -> None:
    result = apply_filters(_sample_df(), search_text="TRANSFERASE")

    assert result["hit_id"].tolist() == ["hit_beta"]


def test_apply_filters_top_n_orders_by_bitscore_desc() -> None:
    result = apply_filters(_sample_df(), top_n=2)

    assert result["hit_id"].tolist() == ["hit_alpha", "hit_beta"]


def test_apply_filters_combines_filters_before_top_n() -> None:
    result = apply_filters(
        _sample_df(),
        max_evalue=1e-2,
        min_identity=60,
        min_bitscore=50,
        min_alignment_length=100,
        search_text="hit",
        top_n=2,
    )

    assert result["hit_id"].tolist() == ["hit_alpha", "hit_beta"]


def test_apply_filters_handles_missing_columns_without_crashing() -> None:
    df = pd.DataFrame({"query_id": ["query_1"], "hit_id": ["hit_1"]})

    result = apply_filters(
        df,
        max_evalue=1e-5,
        min_identity=70,
        min_bitscore=100,
        min_alignment_length=50,
        search_text="hit_1",
        top_n=10,
    )

    assert result["hit_id"].tolist() == ["hit_1"]
