from types import SimpleNamespace

from app import (
    UploadedFileInfo,
    format_file_size,
    get_uploaded_file_info,
    validate_uploaded_file,
)


def test_format_file_size_bytes() -> None:
    assert format_file_size(512) == "512 B"


def test_format_file_size_kilobytes() -> None:
    assert format_file_size(1536) == "1.50 KB"


def test_format_file_size_megabytes() -> None:
    assert format_file_size(2 * 1024 * 1024) == "2.00 MB"


def test_get_uploaded_file_info_normalizes_extension() -> None:
    uploaded_file = SimpleNamespace(name="blast_result.XML", size=2048)

    info = get_uploaded_file_info(uploaded_file)

    assert info.name == "blast_result.XML"
    assert info.size_bytes == 2048
    assert info.extension == ".xml"


def test_validate_uploaded_file_accepts_supported_non_empty_file() -> None:
    info = UploadedFileInfo(name="blast_result.tsv", size_bytes=100, extension=".tsv")

    assert validate_uploaded_file(info) is None


def test_validate_uploaded_file_rejects_empty_file() -> None:
    info = UploadedFileInfo(name="blast_result.tsv", size_bytes=0, extension=".tsv")

    assert validate_uploaded_file(info) == (
        "Файл пустой. Загрузите непустой BLAST XML или tabular файл."
    )


def test_validate_uploaded_file_rejects_unsupported_extension() -> None:
    info = UploadedFileInfo(name="blast_result.csv", size_bytes=100, extension=".csv")

    assert validate_uploaded_file(info) == (
        "Неподдерживаемое расширение файла. Разрешены: .tab, .tsv, .txt, .xml."
    )
