from sqlalchemy.ext.asyncio import AsyncSession

from app.db import repository
from app.domain import texts
from app.services import external_api


async def fetch_weather_for_city(
    session: AsyncSession, vk_id: int, city: str
) -> tuple[str, bool]:
    """Получает погоду по названию города и сохраняет запрос в БД.

    Возвращает (текст_ответа, успех).
    """
    try:
        lat, lon = await external_api.geocode_city(city)
    except external_api.CityNotFound:
        return texts.TXT_CITY_NOT_FOUND, False
    except external_api.ExternalAPIError:
        return texts.TXT_API_ERROR, False

    try:
        data = await external_api.fetch_weather(lat, lon)
    except external_api.ExternalAPIError:
        return texts.TXT_API_ERROR, False

    await repository.set_user_city(session, vk_id, city)
    text = format_weather(city, data)
    await repository.add_history(session, vk_id, city, text)
    return text, True


def format_weather(city: str, data: dict) -> str:
    current = data.get("current", {})
    daily = data.get("daily", {})
    temp = current.get("temperature_2m")
    feels = current.get("apparent_temperature")
    wind = current.get("wind_speed_10m")

    lines = [f"🌤 Погода — {city}", ""]
    if temp is not None:
        lines.append(f"Сейчас: {temp} °C")
    if feels is not None:
        lines.append(f"Ощущается как: {feels} °C")
    if wind is not None:
        lines.append(f"Ветер: {wind} км/ч")

    lines.append("")
    lines.append("📅 Прогноз на 3 дня:")
    dates = daily.get("time", [])[:3]
    tmax = daily.get("temperature_2m_max", [])[:3]
    tmin = daily.get("temperature_2m_min", [])[:3]
    if not dates:
        lines.append("• данные недоступны")
    for d, hi, lo in zip(dates, tmax, tmin):
        lines.append(f"• {d}: {lo}…{hi} °C")

    return "\n".join(lines)