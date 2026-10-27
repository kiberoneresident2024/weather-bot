"""Smoke-проверка проекта. Запуск: python smoke_test.py"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


async def run_checks() -> int:
    errors: list[str] = []

    if not Path(".env").exists():
        errors.append("Нет файла .env (скопируйте .env.example → .env)")
    else:
        load_dotenv()
        if not os.getenv("VK_TOKEN"):
            errors.append("VK_TOKEN не задан в .env")

    try:
        from app.db.session import SessionLocal, init_db
        from app.db import repository

        await init_db()
    except Exception as exc:
        errors.append(f"БД не инициализирована: {exc}")
        _report(errors)
        return 1

    try:
        test_id = 999_999_999
        async with SessionLocal() as session:
            await repository.set_user_city(session, test_id, "Москва")
        async with SessionLocal() as session:
            city = await repository.get_user_city(session, test_id)
        if city != "Москва":
            errors.append("БД не сохраняет город между сессиями")
    except Exception as exc:
        errors.append(f"Тест БД: {exc}")

    try:
        from app.services.validators import (
            is_valid_city,
            is_valid_date,
            is_valid_email,
            is_valid_phone,
        )

        assert is_valid_city("Москва")
        assert is_valid_city("New York")
        assert not is_valid_city("12345")
        assert is_valid_email("a@b.co")
        assert not is_valid_email("no-at")
        assert is_valid_phone("+79991234567")
        assert is_valid_date("01.01.2026")
    except Exception as exc:
        errors.append(f"Валидаторы: {exc}")

    api_ok = False
    try:
        from app.services import external_api

        lat, lon = await asyncio.wait_for(
            external_api.geocode_city("Москва"), timeout=20
        )
        data = await asyncio.wait_for(
            external_api.fetch_weather(lat, lon), timeout=20
        )
        if "current" not in data:
            errors.append("Внешнее API вернуло неожиданный формат")
        api_ok = True
    except asyncio.TimeoutError:
        print("Внешнее API: таймаут (сеть недоступна)")
    except Exception as exc:
        print(f"Внешнее API недоступно: {exc}")

    if errors:
        _report(errors)
        return 1

    print("Все проверки пройдены" + ("" if api_ok else " (без проверки внешнего API)"))
    return 0


def _report(errors: list[str]) -> None:
    print("Обнаружены проблемы:")
    for err in errors:
        print(f"  - {err}")


if __name__ == "__main__":
    sys.exit(asyncio.run(run_checks()))
