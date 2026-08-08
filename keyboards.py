from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

RACE_MAP = {
    "dark_elf": "Тёмный эльф",
    "mage": "Маг",
    "demon": "Демон",
    "mutant": "Мутант",
    "shifter": "Шифтер",
    "lis": "Лис",
    "wolfes": "Волки",
    "cats": "Коты",
    "juravli": "Журавли",
    "snakes": "Змеи",
    "sun_elf": "Светлые эльфы",
    "soul": "Дух",
    "seraphim": "Серафим"
}

def get_race_keyboard():
    """Клавиатура с выбором расы (без кнопки назад)."""
    buttons = []
    row = []
    for i, (key, name) in enumerate(RACE_MAP.items(), 1):
        row.append(InlineKeyboardButton(text=name, callback_data=f"race_{key}"))
        if i % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_race_keyboard_with_back():
    """Клавиатура с выбором расы + кнопка 'Назад'."""
    kb = get_race_keyboard()
    # добавляем строку с кнопкой назад
    kb.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return kb

def get_back_keyboard():
    """Клавиатура только с кнопкой 'Назад'."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧑‍🎓 Ученик", callback_data="choice_student")],
        [InlineKeyboardButton(text="👨‍🏫 Персонал", callback_data="choice_staff")]
    ])

def get_approve_reject_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ]
    ])
