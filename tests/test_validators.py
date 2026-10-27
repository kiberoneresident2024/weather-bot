from app.services.validators import (
    is_valid_city,
    is_valid_date,
    is_valid_email,
    is_valid_phone,
)


def test_city():
    assert is_valid_city("Москва")
    assert is_valid_city("Санкт-Петербург")
    assert is_valid_city("New York")
    assert not is_valid_city("")
    assert not is_valid_city("12345")
    assert not is_valid_city("a")


def test_email():
    assert is_valid_email("a@b.co")
    assert not is_valid_email("no-at-sign")
    assert not is_valid_email("")


def test_phone():
    assert is_valid_phone("+79991234567")
    assert is_valid_phone("8 (999) 123-45-67")
    assert not is_valid_phone("123")
    assert not is_valid_phone("")


def test_date():
    assert is_valid_date("01.01.2026")
    assert not is_valid_date("2026-01-01")
    assert not is_valid_date("32.13.2026")
