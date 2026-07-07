"""BLAST tabular parser."""

from __future__ import annotations

from io import BytesIO, StringIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd


STANDARD_BLAST_COLUMNS = [
    "qseqid",
    "sseqid",
    "pident",
    "length",
    "mismatch",
    "gapopen",
    "qstart",
    "qend",
    "sstart",
    "send",
    "evalue",
    "bitscore",
]

UNIFIED_COLUMNS = [
    "query_id",
    "hit_id",
    "hit_description",
    "evalue",
    "bitscore",
    "score",
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

NUMERIC_COLUMNS = [
    "evalue",
    "bitscore",
    "score",
    "identity_percent",
    "alignment_length",
    "query_start",
    "query_end",
    "hit_start",
    "hit_end",
    "gaps",
    "coverage",
]


class BlastTabularParseError(ValueError):
    """Raised when BLAST tabular content cannot be parsed."""


def parse_blast_tabular(file: str | Path | bytes | BinaryIO) -> pd.DataFrame:
    """Parse BLAST tabular output into the unified DataFrame schema."""
    raw_df = _read_tabular(file)
    if raw_df.empty:
        raise BlastTabularParseError("BLAST tabular файл не содержит строк с результатами.")

    normalized_df = _normalize_raw_columns(raw_df)
    unified_df = pd.DataFrame(
        {
            "query_id": normalized_df["qseqid"],
            "hit_id": normalized_df["sseqid"],
            "hit_description": pd.NA,
            "evalue": normalized_df["evalue"],
            "bitscore": normalized_df["bitscore"],
            "score": pd.NA,
            "identity_percent": normalized_df["pident"],
            "alignment_length": normalized_df["length"],
            "query_start": normalized_df["qstart"],
            "query_end": normalized_df["qend"],
            "hit_start": normalized_df["sstart"],
            "hit_end": normalized_df["send"],
            "gaps": normalized_df["gapopen"],
            "coverage": pd.NA,
            "source_format": "blast_tabular",
        }
    )

    return _coerce_numeric_columns(unified_df)


def _read_tabular(file: str | Path | bytes | BinaryIO) -> pd.DataFrame:
    source = _prepare_source(file)
    return pd.read_csv(
        source,
        sep="\t",
        comment="#",
        header=None,
        dtype=str,
        keep_default_na=False,
    )


def _prepare_source(file: str | Path | bytes | BinaryIO):
    if isinstance(file, bytes):
        return BytesIO(file)

    if isinstance(file, (str, Path)):
        return file

    if hasattr(file, "seek"):
        file.seek(0)

    if hasattr(file, "getvalue"):
        content = file.getvalue()
        if isinstance(content, bytes):
            return BytesIO(content)
        return StringIO(str(content))

    return file


def _normalize_raw_columns(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df.empty:
        raise BlastTabularParseError("BLAST tabular файл не содержит строк с результатами.")

    first_row = [str(value).strip().lower() for value in raw_df.iloc[0].tolist()]

    if set(STANDARD_BLAST_COLUMNS).issubset(first_row):
        normalized_df = raw_df.iloc[1:].copy()
        normalized_df.columns = first_row
        if normalized_df.empty:
            raise BlastTabularParseError(
                "BLAST tabular файл не содержит строк с результатами."
            )
        return normalized_df[STANDARD_BLAST_COLUMNS].reset_index(drop=True)

    if len(raw_df.columns) < len(STANDARD_BLAST_COLUMNS):
        raise BlastTabularParseError(
            "BLAST tabular файл должен содержать минимум 12 стандартных колонок."
        )

    normalized_df = raw_df.iloc[:, : len(STANDARD_BLAST_COLUMNS)].copy()
    normalized_df.columns = STANDARD_BLAST_COLUMNS
    return normalized_df.reset_index(drop=True)


def _coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in NUMERIC_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result[UNIFIED_COLUMNS].reset_index(drop=True)
