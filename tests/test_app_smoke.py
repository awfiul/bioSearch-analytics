import app


def test_app_module_exposes_main() -> None:
    assert callable(app.main)


def test_calculate_percent_handles_zero_total() -> None:
    assert app._calculate_percent(1, 0) is None


def test_calculate_percent_returns_percentage() -> None:
    assert app._calculate_percent(2, 4) == 50
