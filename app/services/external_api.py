import asyncio
import logging

import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "IT-Jump-Weather-Bot/1.0"}


class ExternalAPIError(Exception):
    """Ошибка при обращении к внешнему API."""


class CityNotFound(ExternalAPIError):
    """Город не найден в геокодере."""


async def _get_json(url: str, params: dict | None = None, retries: int = 2) -> dict:
    timeout = aiohttp.ClientTimeout(total=settings.api_timeout)
    last_exc: Exception | None = None

    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession(
                timeout=timeout, headers=HEADERS
            ) as http:
                async with http.get(url, params=params) as resp:
                    if resp.status >= 400:
                        raise ExternalAPIError(f"HTTP {resp.status} от {url}")
                    return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            last_exc = exc
            logger.warning("API attempt %s failed: %s", attempt + 1, exc)
            if attempt < retries:
                await asyncio.sleep(0.5 * (2 ** attempt))
        except ExternalAPIError:
            raise

    raise ExternalAPIError(f"network: {last_exc}")


async def geocode_city(city: str) -> tuple[float, float]:
    data = await _get_json(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
    )
    if not data:
        raise CityNotFound(city)
    return float(data[0]["lat"]), float(data[0]["lon"])


async def fetch_weather(lat: float, lon: float) -> dict:
    return await _get_json(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
            "forecast_days": 3,
        },
    )
