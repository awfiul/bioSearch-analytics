from io import BytesIO

import pandas as pd
import pytest

from src.parsers.blast_tabular_parser import (
    BlastTabularParseError,
    UNIFIED_COLUMNS,
    parse_blast_tabular,
)


def test_parse_blast_tabular_with_header_returns_unified_columns() -> None:
    content = (
        "qseqid\tsseqid\tpident\tlength\tmismatch\tgapopen\t"
        "qstart\tqend\tsstart\tsend\tevalue\tbitscore\n"
        "query_1\thit_1\t99.0\t100\t1\t0\t1\t100\t5\t104\t1e-20\t120\n"
    ).encode()

    df = parse_blast_tabular(content)

    assert list(df.columns) == UNIFIED_COLUMNS
    assert len(df) == 1
    assert df.loc[0, "query_id"] == "query_1"
    assert df.loc[0, "hit_id"] == "hit_1"
    assert df.loc[0, "identity_percent"] == 99.0
    assert df.loc[0, "alignment_length"] == 100
    assert df.loc[0, "evalue"] == pytest.approx(1e-20)
    assert df.loc[0, "bitscore"] == 120
    assert df.loc[0, "source_format"] == "blast_tabular"


def test_parse_blast_tabular_without_header_uses_standard_column_order() -> None:
    content = b"query_1\thit_1\t88.5\t90\t10\t1\t2\t91\t7\t96\t2e-5\t80\n"

    df = parse_blast_tabular(content)

    assert len(df) == 1
    assert df.loc[0, "query_id"] == "query_1"
    assert df.loc[0, "hit_id"] == "hit_1"
    assert df.loc[0, "query_start"] == 2
    assert df.loc[0, "hit_end"] == 96
    assert df.loc[0, "gaps"] == 1


def test_parse_blast_tabular_ignores_comment_lines() -> None:
    content = (
        "# BLASTN 2.15.0+\n"
        "qseqid\tsseqid\tpident\tlength\tmismatch\tgapopen\t"
        "qstart\tqend\tsstart\tsend\tevalue\tbitscore\n"
        "query_1\thit_1\t99.0\t100\t1\t0\t1\t100\t5\t104\t1e-20\t120\n"
    ).encode()

    df = parse_blast_tabular(BytesIO(content))

    assert len(df) == 1
    assert df.loc[0, "bitscore"] == 120


def test_parse_blast_tabular_rejects_empty_content() -> None:
    with pytest.raises(BlastTabularParseError):
        parse_blast_tabular(b"qseqid\tsseqid\n")


def test_parse_blast_tabular_numeric_errors_become_nan() -> None:
    content = (
        "qseqid\tsseqid\tpident\tlength\tmismatch\tgapopen\t"
        "qstart\tqend\tsstart\tsend\tevalue\tbitscore\n"
        "query_1\thit_1\tbad\t100\t1\t0\t1\t100\t5\t104\tbad\t120\n"
    ).encode()

    df = parse_blast_tabular(content)

    assert pd.isna(df.loc[0, "identity_percent"])
    assert pd.isna(df.loc[0, "evalue"])
