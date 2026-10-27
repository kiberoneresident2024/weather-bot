import asyncio
import logging
from logging.handlers import RotatingFileHandler

from vkbottle.bot import Bot

from app.bot.handlers import register_handlers
from app.config import DATA_DIR, settings
from app.db.session import init_db

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        DATA_DIR / "bot.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=[stream, file_handler])


async def run_bot_with_retry(bot: Bot) -> None:
    delay = 5
    max_delay = 60
    while True:
        try:
            logger.info("Запуск Long Poll...")
            await bot.run_polling()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("Long Poll упал: %s. Перезапуск через %s с.", exc, delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)
        else:
            break


async def main() -> None:
    if not settings.vk_token:
        raise RuntimeError(
            "VK_TOKEN не задан. Скопируйте .env.example в .env и заполните."
        )

    logger.info("Инициализация БД...")
    await init_db()

    bot = Bot(token=settings.vk_token)
    register_handlers(bot)

    await run_bot_with_retry(bot)


if __name__ == "__main__":
    setup_logging()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановлено пользователем")
