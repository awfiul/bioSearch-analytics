"""File format detection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_FORMATS = {"blast_xml", "blast_tabular"}
TABULAR_EXTENSIONS = {".tsv", ".txt", ".tab"}
XML_EXTENSIONS = {".xml"}
STANDARD_TABULAR_COLUMNS = {
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
}


class UnsupportedFormatError(ValueError):
    """Raised when uploaded content is not recognized as a supported format."""


@dataclass(frozen=True)
class FormatDetectionResult:
    """Detected file format and a short explanation for the user."""

    source_format: str
    reason: str


def detect_format(filename: str, content: bytes) -> FormatDetectionResult:
    """Detect whether uploaded content is BLAST XML or BLAST tabular output."""
    extension = Path(filename).suffix.lower()
    text_sample = content[:8192].decode("utf-8", errors="ignore").lstrip()

    if not text_sample:
        raise UnsupportedFormatError("Файл пустой или не содержит читаемого текста.")

    if extension in XML_EXTENSIONS and looks_like_blast_xml(text_sample):
        return FormatDetectionResult(
            source_format="blast_xml",
            reason="расширение .xml и найдена BLAST XML-структура",
        )

    if extension in TABULAR_EXTENSIONS and looks_like_blast_tabular(text_sample):
        return FormatDetectionResult(
            source_format="blast_tabular",
            reason="табличное расширение и найдены BLAST tabular-поля",
        )

    if looks_like_blast_xml(text_sample):
        return FormatDetectionResult(
            source_format="blast_xml",
            reason="найдена BLAST XML-структура по содержимому",
        )

    if looks_like_blast_tabular(text_sample):
        return FormatDetectionResult(
            source_format="blast_tabular",
            reason="найдена tabular-структура по содержимому",
        )

    raise UnsupportedFormatError(
        "Не удалось определить формат. Поддерживаются BLAST XML и BLAST tabular."
    )


def looks_like_blast_xml(text: str) -> bool:
    """Return True when the sample contains BLAST XML markers."""
    lowered = text.lower()
    return "<blastoutput" in lowered or "<blastxml" in lowered


def looks_like_blast_tabular(text: str) -> bool:
    """Return True when the sample resembles BLAST outfmt 6 tabular data."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        return False

    first_line = lines[0]
    separator = "\t" if "\t" in first_line else None
    fields = first_line.split(separator)

    normalized_fields = {field.strip().lower() for field in fields}
    if STANDARD_TABULAR_COLUMNS.issubset(normalized_fields):
        return True

    return len(fields) >= 12 and _looks_like_numeric_tabular_row(fields)


def _looks_like_numeric_tabular_row(fields: list[str]) -> bool:
    if len(fields) < 12:
        return False

    numeric_indexes = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    return all(_is_number(fields[index]) for index in numeric_indexes)


def _is_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True
