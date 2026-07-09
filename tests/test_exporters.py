from datetime import datetime
from io import BytesIO

import pandas as pd

from src.analysis.statistics import calculate_summary
from src.export.csv_exporter import dataframe_to_csv_bytes
from src.export.excel_exporter import dataframe_to_excel_bytes
from src.export.html_report import generate_html_report


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "query_id": ["query_1"],
            "hit_id": ["hit_alpha"],
            "hit_description": ["hypothetical <protein>"],
            "evalue": [1e-50],
            "bitscore": [180],
            "identity_percent": [98.5],
            "alignment_length": [200],
        }
    )


def test_dataframe_to_csv_bytes_contains_header_and_data() -> None:
    csv_bytes = dataframe_to_csv_bytes(_sample_df())
    text = csv_bytes.decode("utf-8-sig")

    assert "query_id,hit_id" in text
    assert "query_1,hit_alpha" in text


def test_dataframe_to_excel_bytes_can_be_read_back() -> None:
    excel_bytes = dataframe_to_excel_bytes(_sample_df())

    result = pd.read_excel(BytesIO(excel_bytes))

    assert result.loc[0, "query_id"] == "query_1"
    assert result.loc[0, "hit_id"] == "hit_alpha"


def test_generate_html_report_contains_escaped_content() -> None:
    df = _sample_df()
    html = generate_html_report(
        original_df=df,
        filtered_df=df,
        filters={"max_evalue": 1e-5, "search_text": ""},
        summary=calculate_summary(df),
        conclusions=["Test conclusion"],
        filename="sample.tsv",
        generated_at=datetime(2026, 7, 9, 12, 0, 0),
    )

    assert "BLAST Results Report" in html
    assert "sample.tsv" in html
    assert "2026-07-09 12:00:00" in html
    assert "hypothetical &lt;protein&gt;" in html
    assert "Test conclusion" in html


def test_exporters_handle_empty_dataframe() -> None:
    df = pd.DataFrame()

    csv_bytes = dataframe_to_csv_bytes(df)
    excel_bytes = dataframe_to_excel_bytes(df)
    html = generate_html_report(
        original_df=df,
        filtered_df=df,
        filters={},
        summary={},
        conclusions=[],
        filename=None,
    )

    assert csv_bytes == b"\xef\xbb\xbf\r\n"
    assert pd.read_excel(BytesIO(excel_bytes)).empty
    assert "Выводы не сформированы" in html
