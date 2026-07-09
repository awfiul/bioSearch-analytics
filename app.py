"""Streamlit entry point for BLAST results analytics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import streamlit as st

from src.analysis.filtering import apply_filters
from src.analysis.research import (
    calculate_correlations,
    calculate_filtering_efficiency,
    calculate_threshold_effect,
    generate_research_conclusions,
)
from src.analysis.statistics import calculate_summary, format_metric_value
from src.export.csv_exporter import dataframe_to_csv_bytes
from src.export.excel_exporter import dataframe_to_excel_bytes
from src.export.html_report import generate_html_report
from src.parsers.blast_tabular_parser import BlastTabularParseError, parse_blast_tabular
from src.parsers.blast_xml_parser import BlastXmlParseError, parse_blast_xml
from src.parsers.format_detector import UnsupportedFormatError, detect_format
from src.utils.table_display import (
    COLUMN_LABELS,
    get_default_display_columns,
    prepare_display_table,
)
from src.visualization.charts import (
    plot_alignment_length_vs_bitscore,
    plot_before_after_filtering,
    plot_evalue_distribution,
    plot_evalue_threshold_effect,
    plot_identity_distribution,
    plot_identity_vs_bitscore,
    plot_top_hits_by_bitscore,
)


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

    render_results(df, "Данные успешно прочитаны.")


def render_parsed_xml_data(uploaded_file: BinaryIO) -> None:
    """Parse BLAST XML content and render a preview table."""
    try:
        df = parse_blast_xml(uploaded_file)
    except BlastXmlParseError as error:
        st.error(str(error))
        st.caption("Статус обработки: ошибка парсинга XML-файла")
        return

    render_results(df, "XML успешно прочитан.")


def render_results(df, success_message: str) -> None:
    """Render filters, summary, and results table for parsed BLAST data."""
    filters = render_filter_controls()
    filtered_df = apply_filters(df, **filters)
    selected_columns = render_table_controls(filtered_df)
    display_df = prepare_display_table(filtered_df, selected_columns)

    st.subheader("Таблица результатов")
    st.success(
        f"{success_message} Строк до фильтрации: {len(df)}. "
        f"После фильтрации: {len(filtered_df)}."
    )
    render_summary(filtered_df, total_rows=len(df))
    if filtered_df.empty:
        st.warning("После применения фильтров не осталось строк.")
    render_charts(df, filtered_df)
    render_research_analysis(df)
    render_export_controls(
        original_df=df,
        filtered_df=filtered_df,
        filters=filters,
        filename=st.session_state.get("uploaded_filename"),
    )
    st.dataframe(display_df, use_container_width=True)


def render_charts(original_df, filtered_df) -> None:
    """Render Plotly charts for the filtered BLAST results."""
    st.subheader("Визуализации")

    distribution_tab, top_tab, scatter_tab, thresholds_tab = st.tabs(
        ["Распределения", "Top hits", "Scatter plots", "Пороги"]
    )

    with distribution_tab:
        col_evalue, col_identity = st.columns(2)
        col_evalue.plotly_chart(
            plot_evalue_distribution(filtered_df),
            use_container_width=True,
        )
        col_identity.plotly_chart(
            plot_identity_distribution(filtered_df),
            use_container_width=True,
        )

    with top_tab:
        st.plotly_chart(
            plot_top_hits_by_bitscore(filtered_df),
            use_container_width=True,
        )

    with scatter_tab:
        col_identity_score, col_length_score = st.columns(2)
        col_identity_score.plotly_chart(
            plot_identity_vs_bitscore(filtered_df),
            use_container_width=True,
        )
        col_length_score.plotly_chart(
            plot_alignment_length_vs_bitscore(filtered_df),
            use_container_width=True,
        )

    with thresholds_tab:
        col_thresholds, col_filtering = st.columns(2)
        col_thresholds.plotly_chart(
            plot_evalue_threshold_effect(original_df),
            use_container_width=True,
        )
        col_filtering.plotly_chart(
            plot_before_after_filtering(len(original_df), len(filtered_df)),
            use_container_width=True,
        )


def render_research_analysis(df) -> None:
    """Render the research-analysis section."""
    st.subheader("Исследовательский анализ")

    threshold_effect = calculate_threshold_effect(df)
    correlations = calculate_correlations(df)
    filtering_efficiency = calculate_filtering_efficiency(df)
    conclusions = generate_research_conclusions(df)

    correlation_cols = st.columns(2)
    correlation_cols[0].metric(
        "Корреляция bitscore / identity",
        format_metric_value(correlations["bitscore_identity_correlation"]),
    )
    correlation_cols[1].metric(
        "Корреляция length / bitscore",
        format_metric_value(correlations["alignment_length_bitscore_correlation"]),
    )

    efficiency_cols = st.columns(3)
    efficiency_cols[0].metric(
        "После исслед. фильтра",
        format_metric_value(filtering_efficiency["filtered_count"]),
    )
    efficiency_cols[1].metric(
        "Удалено строк",
        format_metric_value(filtering_efficiency["removed_count"]),
    )
    efficiency_cols[2].metric(
        "Удалено, %",
        format_metric_value(filtering_efficiency["removed_percent"], "%"),
    )

    with st.expander("Таблица влияния E-value threshold"):
        st.dataframe(
            threshold_effect.rename(
                columns={"threshold": "E-value threshold", "count": "Count"}
            ),
            use_container_width=True,
        )

    st.write("Краткие выводы:")
    for conclusion in conclusions:
        st.markdown(f"- {conclusion}")


def render_export_controls(original_df, filtered_df, filters: dict, filename: str | None) -> None:
    """Render download buttons for filtered data and HTML report."""
    st.subheader("Экспорт")

    summary = calculate_summary(filtered_df)
    conclusions = generate_research_conclusions(original_df)
    html_report = generate_html_report(
        original_df=original_df,
        filtered_df=filtered_df,
        filters=filters,
        summary=summary,
        conclusions=conclusions,
        filename=filename,
    )

    csv_col, excel_col, html_col = st.columns(3)
    csv_col.download_button(
        "Скачать CSV",
        data=dataframe_to_csv_bytes(filtered_df),
        file_name="filtered_blast_results.csv",
        mime="text/csv",
    )
    excel_col.download_button(
        "Скачать Excel",
        data=dataframe_to_excel_bytes(filtered_df),
        file_name="filtered_blast_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    html_col.download_button(
        "Скачать HTML-отчет",
        data=html_report.encode("utf-8"),
        file_name="blast_analysis_report.html",
        mime="text/html",
    )


def render_filter_controls() -> dict:
    """Render sidebar filters and return values for apply_filters."""
    with st.sidebar:
        st.header("Фильтры")

        evalue_options = {
            "Без фильтра": None,
            "1": 1.0,
            "1e-1": 1e-1,
            "1e-3": 1e-3,
            "1e-5": 1e-5,
            "1e-10": 1e-10,
            "1e-20": 1e-20,
            "1e-50": 1e-50,
        }
        selected_evalue = st.selectbox(
            "E-value <= ",
            options=list(evalue_options.keys()),
        )
        min_identity = st.slider("Identity >= %", 0, 100, 0, 1)
        min_bitscore = st.number_input("Bitscore >=", min_value=0.0, value=0.0)
        min_alignment_length = st.number_input(
            "Alignment length >=",
            min_value=0,
            value=0,
            step=1,
        )
        top_n_options = {
            "Все результаты": None,
            "Top 10": 10,
            "Top 20": 20,
            "Top 50": 50,
            "Top 100": 100,
        }
        selected_top_n = st.selectbox("Top N по bitscore", list(top_n_options.keys()))
        search_text = st.text_input("Поиск по query, hit или описанию")

    return {
        "max_evalue": evalue_options[selected_evalue],
        "min_identity": min_identity if min_identity > 0 else None,
        "min_bitscore": min_bitscore if min_bitscore > 0 else None,
        "min_alignment_length": (
            min_alignment_length if min_alignment_length > 0 else None
        ),
        "search_text": search_text,
        "top_n": top_n_options[selected_top_n],
    }


def render_table_controls(df) -> list[str]:
    """Render sidebar controls for table column visibility."""
    available_columns = list(df.columns)
    default_columns = get_default_display_columns(available_columns)
    label_to_column = {
        COLUMN_LABELS.get(column, column): column for column in available_columns
    }
    default_labels = [
        COLUMN_LABELS.get(column, column) for column in default_columns
    ]

    with st.sidebar:
        st.header("Таблица")
        selected_labels = st.multiselect(
            "Отображаемые колонки",
            options=list(label_to_column.keys()),
            default=default_labels,
        )

    return [label_to_column[label] for label in selected_labels]


def render_summary(df, total_rows: int | None = None) -> None:
    """Render summary statistics for parsed BLAST hits."""
    summary = calculate_summary(df)

    st.subheader("Сводная статистика")

    first_row = st.columns(4)
    first_row[0].metric("Всего совпадений", format_metric_value(summary["total_hits"]))
    first_row[1].metric("Уникальных query", format_metric_value(summary["unique_queries"]))
    first_row[2].metric("Уникальных hit", format_metric_value(summary["unique_hits"]))
    first_row[3].metric("Лучший E-value", format_metric_value(summary["min_evalue"]))

    second_row = st.columns(3)
    second_row[0].metric(
        "Максимальный bitscore",
        format_metric_value(summary["max_bitscore"]),
    )
    second_row[1].metric(
        "Средний identity",
        format_metric_value(summary["mean_identity_percent"], "%"),
    )
    second_row[2].metric(
        "Средняя длина",
        format_metric_value(summary["mean_alignment_length"]),
    )

    if total_rows is not None:
        st.caption(
            f"После фильтрации: {len(df)} из {total_rows} "
            f"({format_metric_value(_calculate_percent(len(df), total_rows), '%')})."
        )


def _calculate_percent(value: int, total: int) -> float | None:
    if total <= 0:
        return None
    return value / total * 100


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

    st.session_state["uploaded_filename"] = uploaded_file.name

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
