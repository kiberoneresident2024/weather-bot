import logging

from vkbottle import GroupEventType
from vkbottle.bot import Bot, Message, MessageEvent

from app.bot import keyboards
from app.bot.deps import get_session
from app.bot.states import BotStates
from app.db import repository
from app.domain import scenario, texts
from app.services.validators import is_valid_city

logger = logging.getLogger(__name__)

MENU_COMMANDS = [
    "/start", "start",
    "Начать", "начать",
    "Меню", "меню",
    "Назад", "назад",
]


async def _send_menu(bot: Bot, peer_id: int, text: str) -> None:
    await bot.state_dispenser.set(peer_id, BotStates.MENU)
    await bot.api.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=0,
        keyboard=keyboards.reply_main_menu(),
    )


async def _snackbar(event: MessageEvent, text: str) -> None:
    try:
        await event.show_snackbar(text)
    except Exception as exc:
        logger.debug("snackbar failed: %s", exc)


def register_handlers(bot: Bot) -> None:

    @bot.on.message(text=MENU_COMMANDS)
    async def start_handler(message: Message) -> None:
        await _send_menu(bot, message.peer_id, texts.TXT_WELCOME)

    @bot.on.message(text=["Погода", "Узнать погоду", "/weather"])
    async def ask_city_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.WAITING_CITY)
        async with get_session() as session:
            recent = await repository.get_recent_cities(session, message.from_id)
        await message.answer(texts.TXT_ASK_CITY, keyboard=keyboards.inline_cities(recent))

    @bot.on.message(text=["Мой город", "/my_city"])
    async def my_city_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        async with get_session() as session:
            city = await repository.get_user_city(session, message.from_id)
        text = f"📍 Ваш город: {city}" if city else texts.TXT_NO_CITY
        await message.answer(text, keyboard=keyboards.reply_main_menu())

    @bot.on.message(text=["История", "/history"])
    async def history_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        async with get_session() as session:
            items = await repository.get_recent_history(
                session, message.from_id, limit=5
            )
        if not items:
            await message.answer(
                texts.TXT_HISTORY_EMPTY, keyboard=keyboards.reply_main_menu()
            )
            return
        lines = [texts.TXT_HISTORY_HEADER, ""]
        for item in items:
            ts = item.created_at.strftime("%d.%m %H:%M")
            lines.append(f"• {ts} — {item.query}")
        await message.answer("\n".join(lines), keyboard=keyboards.reply_main_menu())

    @bot.on.message(text=["Помощь", "/help"])
    async def help_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(texts.TXT_HELP, keyboard=keyboards.reply_main_menu())

    @bot.on.message(state=BotStates.WAITING_CITY)
    async def city_input_handler(message: Message) -> None:
        city = (message.text or "").strip()
        if not is_valid_city(city):
            async with get_session() as session:
                recent = await repository.get_recent_cities(session, message.from_id)
            await message.answer(
                texts.TXT_INVALID_CITY, keyboard=keyboards.inline_cities(recent)
            )
            return

        await message.answer(texts.TXT_LOADING)
        async with get_session() as session:
            text, ok = await scenario.fetch_weather_for_city(
                session, message.from_id, city
            )

        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        keyboard = (
            keyboards.reply_weather_result() if ok else keyboards.reply_main_menu()
        )
        await message.answer(text, keyboard=keyboard)

    @bot.on.message()
    async def fallback_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(texts.TXT_FALLBACK, keyboard=keyboards.reply_main_menu())

    @bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
    async def callback_handler(event: MessageEvent) -> None:
        payload = event.payload or {}
        cmd = payload.get("cmd")
        peer_id = event.peer_id
        user_id = event.user_id

        if cmd == "city":
            city = payload.get("name", "")
            if not is_valid_city(city):
                await _snackbar(event, texts.TXT_INVALID_CITY)
                return
            
            # 1. Сразу убираем "крутилку", отвечая на событие
            await _snackbar(event, texts.TXT_LOADING)
            
            # 2. Делаем запрос к API
            async with get_session() as session:
                text, ok = await scenario.fetch_weather_for_city(
                    session, user_id, city
                )
                
            await bot.state_dispenser.set(peer_id, BotStates.MENU)
            keyboard = (
                keyboards.inline_after_result() if ok else keyboards.reply_main_menu()
            )
            await bot.api.messages.send(
                peer_id=peer_id, message=text, random_id=0, keyboard=keyboard
            )

        elif cmd == "ask_city":
            await _snackbar(event, texts.TXT_ASK_CITY)
            await bot.state_dispenser.set(peer_id, BotStates.WAITING_CITY)
            async with get_session() as session:
                recent = await repository.get_recent_cities(session, user_id)
            await bot.api.messages.send(
                peer_id=peer_id,
                message=texts.TXT_ASK_CITY,
                random_id=0,
                keyboard=keyboards.inline_cities(recent),
            )

        elif cmd == "menu":
            await _snackbar(event, texts.TXT_MAIN_MENU)
            await _send_menu(bot, peer_id, texts.TXT_WELCOME)