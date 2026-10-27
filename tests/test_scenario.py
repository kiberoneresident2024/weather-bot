from app.domain.scenario import format_weather


def test_format_weather_full():
    data = {
        "current": {
            "temperature_2m": 5,
            "apparent_temperature": 3,
            "wind_speed_10m": 10,
        },
        "daily": {
            "time": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "temperature_2m_max": [7, 6, 4],
            "temperature_2m_min": [1, 0, -2],
        },
    }
    text = format_weather("Москва", data)
    assert "Москва" in text
    assert "5" in text
    assert "2026-01-01" in text
    assert "прогноз" in text.lower()


def test_format_weather_empty():
    text = format_weather("Город", {})
    assert "Город" in text
    assert "данные недоступны" in text


def test_format_weather_partial():
    data = {"current": {"temperature_2m": 12}}
    text = format_weather("Сочи", data)
    assert "Сочи" in text
    assert "12" in text
