from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text


def reply_main_menu() -> str:
    kb = Keyboard(one_time=False, inline=False)
    kb.add(Text("Погода"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("Мой город"), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("История"), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text("Помощь"), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()


def reply_weather_result() -> str:
    kb = Keyboard(one_time=False, inline=False)
    kb.add(Text("Погода"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("История"), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("Мой город"), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text("Помощь"), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()


def inline_cities(recent_cities: list[str] | None = None) -> str:
    kb = Keyboard(one_time=False, inline=True)
    
    if recent_cities:
        for i, city in enumerate(recent_cities):
            kb.add(Callback(f"🕒 {city}", {"cmd": "city", "name": city}))
            if (i + 1) % 2 == 0:
                kb.row()
        if len(recent_cities) % 2 != 0:
            kb.row()
            
    kb.add(Callback("Москва", {"cmd": "city", "name": "Москва"}))
    kb.add(Callback("Санкт-Петербург", {"cmd": "city", "name": "Санкт-Петербург"}))
    kb.row()
    kb.add(Callback("Новосибирск", {"cmd": "city", "name": "Новосибирск"}))
    kb.add(Callback("Екатеринбург", {"cmd": "city", "name": "Екатеринбург"}))
    return kb.get_json()


def inline_after_result() -> str:
    kb = Keyboard(one_time=False, inline=True)
    # ИСПРАВЛЕНО: цвет передается в метод .add()
    kb.add(Callback("Другой город", {"cmd": "ask_city"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Callback("Меню", {"cmd": "menu"}), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()