import app


def test_app_module_exposes_main() -> None:
    assert callable(app.main)


def test_calculate_percent_handles_zero_total() -> None:
    assert app._calculate_percent(1, 0) is None


def test_calculate_percent_returns_percentage() -> None:
    assert app._calculate_percent(2, 4) == 50


def test_select_uploaded_file_prefers_sidebar_file() -> None:
    assert app.select_uploaded_file("sidebar", "main") == "sidebar"


def test_select_uploaded_file_uses_main_file_when_sidebar_empty() -> None:
    assert app.select_uploaded_file(None, "main") == "main"


def test_select_uploaded_file_returns_none_without_uploads() -> None:
    assert app.select_uploaded_file(None, None) is None
