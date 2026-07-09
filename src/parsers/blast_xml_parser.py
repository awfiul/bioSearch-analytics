"""BLAST XML parser."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import BinaryIO

from Bio.Blast import NCBIXML
import pandas as pd

from src.parsers.schema import ensure_unified_schema


NUMERIC_COLUMNS = [
    "evalue",
    "bitscore",
    "score",
    "identity",
    "identity_percent",
    "alignment_length",
    "query_start",
    "query_end",
    "hit_start",
    "hit_end",
    "gaps",
    "coverage",
]


class BlastXmlParseError(ValueError):
    """Raised when BLAST XML content cannot be parsed."""


def parse_blast_xml(file: str | Path | bytes | BinaryIO) -> pd.DataFrame:
    """Parse BLAST XML into the unified DataFrame schema."""
    try:
        records = list(NCBIXML.parse(_prepare_handle(file)))
    except Exception as error:
        raise BlastXmlParseError(f"Не удалось прочитать BLAST XML: {error}") from error

    rows = []
    for record in records:
        query_id = _first_not_empty(
            getattr(record, "query_id", None),
            getattr(record, "query", None),
        )
        query_length = getattr(record, "query_letters", None)

        for alignment in getattr(record, "alignments", []):
            for hsp in getattr(alignment, "hsps", []):
                alignment_length = getattr(hsp, "align_length", None)
                identity = getattr(hsp, "identities", None)
                identity_percent = _calculate_identity_percent(identity, alignment_length)
                coverage = _calculate_coverage(alignment_length, query_length)

                rows.append(
                    {
                        "query_id": query_id,
                        "hit_id": getattr(alignment, "hit_id", None),
                        "hit_description": getattr(alignment, "hit_def", None),
                        "evalue": getattr(hsp, "expect", None),
                        "bitscore": getattr(hsp, "bits", None),
                        "score": getattr(hsp, "score", None),
                        "identity": identity,
                        "identity_percent": identity_percent,
                        "alignment_length": alignment_length,
                        "query_start": getattr(hsp, "query_start", None),
                        "query_end": getattr(hsp, "query_end", None),
                        "hit_start": getattr(hsp, "sbjct_start", None),
                        "hit_end": getattr(hsp, "sbjct_end", None),
                        "gaps": getattr(hsp, "gaps", None),
                        "coverage": coverage,
                        "source_format": "blast_xml",
                    }
                )

    return _build_dataframe(rows)


def _prepare_handle(file: str | Path | bytes | BinaryIO):
    if isinstance(file, bytes):
        return StringIO(file.decode("utf-8", errors="replace"))

    if isinstance(file, (str, Path)):
        return StringIO(Path(file).read_text(encoding="utf-8"))

    if hasattr(file, "seek"):
        file.seek(0)

    if hasattr(file, "getvalue"):
        content = file.getvalue()
        if isinstance(content, bytes):
            return StringIO(content.decode("utf-8", errors="replace"))
        return StringIO(str(content))

    return file


def _build_dataframe(rows: list[dict]) -> pd.DataFrame:
    columns = [
        "query_id",
        "hit_id",
        "hit_description",
        "evalue",
        "bitscore",
        "score",
        "identity",
        "identity_percent",
        "alignment_length",
        "query_start",
        "query_end",
        "hit_start",
        "hit_end",
        "gaps",
        "coverage",
        "source_format",
    ]
    df = pd.DataFrame(rows, columns=columns)
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return ensure_unified_schema(df)


def _calculate_identity_percent(identity: int | None, alignment_length: int | None) -> float | None:
    if identity is None or not alignment_length:
        return None
    return identity / alignment_length * 100


def _calculate_coverage(alignment_length: int | None, query_length: int | None) -> float | None:
    if alignment_length is None or not query_length:
        return None
    return alignment_length / query_length * 100


def _first_not_empty(*values):
    for value in values:
        if value:
            return value
    return None
