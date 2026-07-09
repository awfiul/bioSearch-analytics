import pytest

from src.parsers.format_detector import (
    UnsupportedFormatError,
    detect_format,
    looks_like_blast_tabular,
    looks_like_blast_xml,
)


def test_detect_format_recognizes_blast_xml_by_extension_and_content() -> None:
    result = detect_format("blast_result.xml", b"<?xml version='1.0'?><BlastOutput />")

    assert result.source_format == "blast_xml"


def test_detect_format_recognizes_tabular_header() -> None:
    content = (
        "qseqid\tsseqid\tpident\tlength\tmismatch\tgapopen\t"
        "qstart\tqend\tsstart\tsend\tevalue\tbitscore\n"
        "query_1\thit_1\t99.0\t100\t1\t0\t1\t100\t5\t104\t1e-20\t120\n"
    ).encode()

    result = detect_format("blast_result.tsv", content)

    assert result.source_format == "blast_tabular"


def test_detect_format_recognizes_tabular_without_header() -> None:
    content = b"query_1\thit_1\t99.0\t100\t1\t0\t1\t100\t5\t104\t1e-20\t120\n"

    result = detect_format("blast_result.txt", content)

    assert result.source_format == "blast_tabular"


def test_detect_format_rejects_unknown_content() -> None:
    with pytest.raises(UnsupportedFormatError):
        detect_format("notes.txt", b"not a blast file")


def test_detect_format_rejects_empty_content() -> None:
    with pytest.raises(UnsupportedFormatError):
        detect_format("empty.tsv", b"")


def test_looks_like_blast_xml_is_case_insensitive() -> None:
    assert looks_like_blast_xml("<blastoutput></blastoutput>")


def test_looks_like_blast_tabular_ignores_comments() -> None:
    content = (
        "# BLASTN 2.15.0+\n"
        "query_1\thit_1\t99.0\t100\t1\t0\t1\t100\t5\t104\t1e-20\t120\n"
    )

    assert looks_like_blast_tabular(content)
