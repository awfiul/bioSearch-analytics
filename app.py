"""Streamlit entry point for BLAST results analytics."""

from __future__ import annotations

import streamlit as st


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

    uploaded_file = st.file_uploader(
        "Загрузите BLAST XML или tabular файл",
        type=["xml", "tsv", "txt", "tab"],
    )

    if uploaded_file is None:
        st.info("Файл пока не загружен. Поддерживаемые форматы: XML, TSV, TXT, TAB.")
        return

    file_size_kb = uploaded_file.size / 1024
    st.success("Файл загружен.")
    st.write(f"Имя файла: `{uploaded_file.name}`")
    st.write(f"Размер: `{file_size_kb:.2f} KB`")
    st.warning("Парсинг и аналитика будут добавлены на следующих этапах.")


if __name__ == "__main__":
    main()
