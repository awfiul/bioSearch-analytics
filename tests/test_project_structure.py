from pathlib import Path


def test_expected_project_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]

    expected_paths = [
        root / "app.py",
        root / "requirements.txt",
        root / "src" / "parsers" / "format_detector.py",
        root / "src" / "analysis" / "statistics.py",
        root / "src" / "visualization" / "charts.py",
        root / "src" / "export" / "html_report.py",
        root / "data" / "examples" / "sample_blast.tsv",
        root / "data" / "examples" / "sample_blast.xml",
    ]

    missing = [path for path in expected_paths if not path.exists()]
    assert not missing
