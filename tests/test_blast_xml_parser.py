from pathlib import Path

import pandas as pd
import pytest

from src.parsers.blast_xml_parser import (
    BlastXmlParseError,
    parse_blast_xml,
)
from src.parsers.blast_tabular_parser import UNIFIED_COLUMNS


def test_parse_blast_xml_returns_unified_columns() -> None:
    xml_path = Path("data/examples/sample_blast.xml")

    df = parse_blast_xml(xml_path)

    assert list(df.columns) == UNIFIED_COLUMNS
    assert len(df) == 1
    assert df.loc[0, "query_id"] == "query_1"
    assert df.loc[0, "hit_id"] == "hit_alpha"
    assert df.loc[0, "hit_description"] == "hypothetical protein alpha"
    assert df.loc[0, "evalue"] == pytest.approx(1e-50)
    assert df.loc[0, "bitscore"] == 180.0
    assert df.loc[0, "score"] == 450
    assert df.loc[0, "identity_percent"] == pytest.approx(85 / 90 * 100)
    assert df.loc[0, "alignment_length"] == 90
    assert df.loc[0, "query_start"] == 1
    assert df.loc[0, "query_end"] == 90
    assert df.loc[0, "hit_start"] == 5
    assert df.loc[0, "hit_end"] == 94
    assert df.loc[0, "gaps"] == 1
    assert df.loc[0, "coverage"] == 90.0
    assert df.loc[0, "source_format"] == "blast_xml"


def test_parse_blast_xml_accepts_bytes() -> None:
    content = Path("data/examples/sample_blast.xml").read_bytes()

    df = parse_blast_xml(content)

    assert len(df) == 1
    assert df.loc[0, "hit_id"] == "hit_alpha"


def test_parse_blast_xml_returns_empty_dataframe_for_no_hits() -> None:
    content = Path("data/examples/sample_blast.xml").read_text(encoding="utf-8")
    content = content.replace(
        """        <Hit>
          <Hit_num>1</Hit_num>
          <Hit_id>hit_alpha</Hit_id>
          <Hit_def>hypothetical protein alpha</Hit_def>
          <Hit_accession>ABC123</Hit_accession>
          <Hit_len>120</Hit_len>
          <Hit_hsps>
            <Hsp>
              <Hsp_num>1</Hsp_num>
              <Hsp_bit-score>180.0</Hsp_bit-score>
              <Hsp_score>450</Hsp_score>
              <Hsp_evalue>1e-50</Hsp_evalue>
              <Hsp_query-from>1</Hsp_query-from>
              <Hsp_query-to>90</Hsp_query-to>
              <Hsp_hit-from>5</Hsp_hit-from>
              <Hsp_hit-to>94</Hsp_hit-to>
              <Hsp_query-frame>0</Hsp_query-frame>
              <Hsp_hit-frame>0</Hsp_hit-frame>
              <Hsp_identity>85</Hsp_identity>
              <Hsp_positive>88</Hsp_positive>
              <Hsp_gaps>1</Hsp_gaps>
              <Hsp_align-len>90</Hsp_align-len>
              <Hsp_qseq>MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAG</Hsp_qseq>
              <Hsp_hseq>MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAG</Hsp_hseq>
              <Hsp_midline>MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAG</Hsp_midline>
            </Hsp>
          </Hit_hsps>
        </Hit>""",
        "",
    )

    df = parse_blast_xml(content.encode())

    assert list(df.columns) == UNIFIED_COLUMNS
    assert df.empty


def test_parse_blast_xml_rejects_invalid_xml() -> None:
    with pytest.raises(BlastXmlParseError):
        parse_blast_xml(b"not xml")


def test_parse_blast_xml_empty_values_are_nan() -> None:
    df = parse_blast_xml(Path("data/examples/sample_blast.xml"))

    assert not pd.isna(df.loc[0, "coverage"])
