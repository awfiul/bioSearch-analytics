"""Streamlit entry point for BLAST results analytics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import streamlit as st

from src.parsers.blast_tabular_parser import BlastTabularParseError, parse_blast_tabular
from src.parsers.blast_xml_parser import BlastXmlParseError, parse_blast_xml
from src.parsers.format_detector import UnsupportedFormatError, detect_format


SUPPORTED_EXTENSIONS = {".xml", ".tsv", ".txt", ".tab"}


@dataclass(frozen=True)
class UploadedFileInfo:
    """Basic metadata shown before parsing starts."""

    name: str
    size_bytes: int
    extension: str


def format_file_size(size_bytes: int) -> str:
    """Return a compact human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"

    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{size_kb:.2f} KB"

    size_mb = size_kb / 1024
    return f"{size_mb:.2f} MB"


def get_file_extension(filename: str) -> str:
    """Return the lowercase suffix used for upload validation."""
    return Path(filename).suffix.lower()


def get_uploaded_file_info(uploaded_file: BinaryIO) -> UploadedFileInfo:
    """Extract metadata from a Streamlit uploaded file object."""
    name = getattr(uploaded_file, "name", "")
    size = int(getattr(uploaded_file, "size", 0) or 0)

    return UploadedFileInfo(
        name=name,
        size_bytes=size,
        extension=get_file_extension(name),
    )


def validate_uploaded_file(info: UploadedFileInfo) -> str | None:
    """Return an error message for invalid uploads, otherwise None."""
    if not info.name:
        return "Не удалось определить имя файла."

    if info.size_bytes <= 0:
        return "Файл пустой. Загрузите непустой BLAST XML или tabular файл."

    if info.extension not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        return f"Неподдерживаемое расширение файла. Разрешены: {allowed}."

    return None


def render_uploaded_file_status(uploaded_file: BinaryIO) -> bool:
    """Render upload metadata and return True when the file passes basic checks."""
    info = get_uploaded_file_info(uploaded_file)
    validation_error = validate_uploaded_file(info)

    st.subheader("Загруженный файл")

    col_name, col_size, col_ext = st.columns(3)
    col_name.metric("Имя файла", info.name or "не определено")
    col_size.metric("Размер", format_file_size(info.size_bytes))
    col_ext.metric("Расширение", info.extension or "нет")

    if validation_error:
        st.error(validation_error)
        st.caption("Статус обработки: ошибка загрузки")
        return False

    st.success("Файл загружен и прошел базовую проверку.")
    st.caption("Статус обработки: готов к определению формата")
    return True


def render_format_detection(uploaded_file: BinaryIO) -> str | None:
    """Render detected source format and return it when successful."""
    content = uploaded_file.getvalue()

    try:
        detection = detect_format(uploaded_file.name, content)
    except UnsupportedFormatError as error:
        st.error(str(error))
        st.caption("Статус обработки: формат не определен")
        return None

    st.subheader("Формат данных")
    st.write(f"Определенный формат: `{detection.source_format}`")
    st.caption(f"Причина: {detection.reason}")
    st.caption("Статус обработки: формат определен")
    return detection.source_format


def render_parsed_tabular_data(uploaded_file: BinaryIO) -> None:
    """Parse BLAST tabular content and render a preview table."""
    try:
        df = parse_blast_tabular(uploaded_file)
    except BlastTabularParseError as error:
        st.error(str(error))
        st.caption("Статус обработки: ошибка парсинга tabular-файла")
        return

    st.subheader("Таблица результатов")
    st.success(f"Данные успешно прочитаны. Строк: {len(df)}.")
    st.dataframe(df, use_container_width=True)


def render_parsed_xml_data(uploaded_file: BinaryIO) -> None:
    """Parse BLAST XML content and render a preview table."""
    try:
        df = parse_blast_xml(uploaded_file)
    except BlastXmlParseError as error:
        st.error(str(error))
        st.caption("Статус обработки: ошибка парсинга XML-файла")
        return

    st.subheader("Таблица результатов")
    st.success(f"XML успешно прочитан. Строк: {len(df)}.")
    st.dataframe(df, use_container_width=True)


def main() -> None:
    st.set_page_config(
        page_title="BLAST Results Analytics",
        page_icon="DNA",
        layout="wide",
    )

    st.title("BLAST Results Analytics")
    st.write(
        "Приложение для загрузки, обработки, фильтрации и визуализации "
        "результатов поиска биологических последовательностей."
    )

    with st.sidebar:
        st.header("Данные")
        uploaded_file = st.file_uploader(
            "Загрузите BLAST XML или tabular файл",
            type=["xml", "tsv", "txt", "tab"],
        )

    if uploaded_file is None:
        st.info("Файл пока не загружен. Поддерживаемые форматы: XML, TSV, TXT, TAB.")
        return

    is_valid_upload = render_uploaded_file_status(uploaded_file)
    if not is_valid_upload:
        return

    detected_format = render_format_detection(uploaded_file)
    if detected_format is None:
        return

    if detected_format == "blast_tabular":
        render_parsed_tabular_data(uploaded_file)
        return

    if detected_format == "blast_xml":
        render_parsed_xml_data(uploaded_file)
        return


if __name__ == "__main__":
    main()
