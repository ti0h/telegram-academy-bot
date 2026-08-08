import os
import asyncio
import logging
import signal
import time
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

# ---------- Загружаем секреты ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
PORT = int(os.getenv("PORT", 10000))  # Render задаёт PORT

# ВАЖНО: проверяем переменные ДО того как пытаемся превратить их в число.
# Раньше int(None) падал с непонятной ошибкой раньше, чем срабатывала эта проверка.
if not BOT_TOKEN or not GROUP_CHAT_ID_RAW:
    raise ValueError("BOT_TOKEN и GROUP_CHAT_ID должны быть заданы в .env")

GROUP_CHAT_ID = int(GROUP_CHAT_ID_RAW)

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ---------- RACE_MAP (все 13 рас) ----------
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


def esc(text) -> str:
    """
    Экранирует пользовательский текст перед вставкой в HTML-сообщение.
    Без этого символы вроде <, > или & могли бы сломать разметку
    и анкета вообще не отправилась бы админам.
    """
    return html.escape(str(text))


# ---------- СОСТОЯНИЯ ----------
class Choice(StatesGroup):
    waiting = State()


class StudentForm(StatesGroup):
    name = State()
    race = State()
    age = State()
    gender_height_weight = State()
    character = State()
    abilities = State()
    weaknesses = State()
    facts = State()
    appearance = State()
    biography = State()
    course = State()


class StaffForm(StatesGroup):
    position = State()
    name = State()
    age = State()
    race = State()
    gender_height_weight = State()
    character = State()
    abilities = State()
    weaknesses = State()
    facts = State()
    appearance = State()
    biography = State()


class RejectReason(StatesGroup):
    waiting_for_reason = State()


# ---------- /start ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    intro = (
        "А, это ты. Ну давай, заходи, раз уж пришёл. Только учти: я сейчас в процессе важного ничегонеделания, так что говори быстро.\n"
        "Хочешь анкету создать? Похвально. Даже не знаю, что более жалко — твоя уверенность, что ты достоин здесь учиться, или тот факт, что я действительно потрачу на тебя время.\n"
        "Впрочем, у меня сегодня хорошее настроение — я полюбовался на себя в зеркало, а это всегда поднимает дух.\n"
        "Так что давай, смертный, ученик ты или персонал?"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧑‍🎓 Ученик", callback_data="choice_student")],
        [InlineKeyboardButton(text="👨‍🏫 Персонал", callback_data="choice_staff")]
    ])
    await message.answer(intro, reply_markup=keyboard)
    await state.set_state(Choice.waiting)


# ---------- ВЫБОР ТИПА ----------
@dp.callback_query(StateFilter(Choice.waiting))
async def process_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "choice_student":
        await callback.message.delete()
        await bot.send_message(
            callback.message.chat.id,
            "<b>Для ученика</b>\n\n"
            "Назовись. Только без титулов, умоляю. «Лорд Тьмы», «Повелительница Звёзд» — я этого не вынесу. "
            "У меня у самого их десяток, и я не разбрасываюсь. Просто имя. Мне, в общем-то, всё равно, но формальности требуют."
        )
        await state.set_state(StudentForm.name)
        await callback.answer()
    elif callback.data == "choice_staff":
        await callback.message.delete()
        await bot.send_message(
            callback.message.chat.id,
            "<b>Для персонала</b>\n\n"
            "Решил устроиться ко мне на работу? Смело. Или глупо. Я пока не определился. Знаешь, что я люблю больше, чем хаос? Только себя. "
            "Так что, если ты не готов мириться с моим величием, капризами и тем, что я временами вообще забываю о существовании персонала, — лучше уйди сейчас. Я даже не замечу.\n\n"
            "<b>Должность</b>\n"
            "Кем хочешь быть? Преподавателем? Целителем? Смотрителем леса? Выбирай, мне без разницы. Только учти: если облажаешься, я разочаруюсь. "
            "А когда я разочаровываюсь, я начинаю искать развлечений. Обычно за чужой счёт. Ну так что, не передумал? Нет? Ну смотри."
        )
        await state.set_state(StaffForm.position)
        await callback.answer()


# ---------- АНКЕТА УЧЕНИКА ----------
@dp.message(StateFilter(StudentForm.name))
async def student_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "<b>Раса</b>\nИ кто ты у нас по природе? Человек, эльф, недодемон? Пока ты будешь перечислять, я, пожалуй, пересчитаю свои рога. "
        "О, у меня их два. Прекрасных. Тёмно-синих. А у тебя? Ну давай, не томи, кто ты там по расовой принадлежности.",
        reply_markup=get_race_keyboard()
    )
    await state.set_state(StudentForm.race)


@dp.callback_query(StateFilter(StudentForm.race))
async def student_race(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_", 1)[1]
    if key in RACE_MAP:
        race_name = RACE_MAP[key]
        await state.update_data(race=race_name)
        await callback.message.delete()
        await bot.send_message(callback.message.chat.id, f"Выбрана раса: {esc(race_name)}")
        await bot.send_message(
            callback.message.chat.id,
            "<b>Возраст</b>\nНе подскажешь возраст? Мой я давно не считаю, потому что цифры не способны вместить моё величие. "
            "А вот твой — назови. Сверься с регламентом. Если тебе под сотню, а ты прёшься на первый курс, я даже не разозлюсь — мне просто станет ещё скучнее, чем было."
        )
        await state.set_state(StudentForm.age)
        await callback.answer()
    else:
        await callback.answer("Выберите расу из предложенных", show_alert=True)


@dp.message(StateFilter(StudentForm.age))
async def student_age(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Возраст должен быть числом. Попробуйте снова.")
        return
    age = int(message.text)
    if age < 1 or age > 120:
        await message.answer("⚠️ Возраст должен быть от 1 до 120. Введите корректно.")
        return
    await state.update_data(age=age)
    await message.answer(
        "<b>Пол / Рост / Вес</b>\nПол, рост, вес. Три скучных слова. Если у тебя есть что-то интересное в пропорциях — я, может, и подниму бровь. Но вряд ли."
    )
    await state.set_state(StudentForm.gender_height_weight)


@dp.message(StateFilter(StudentForm.gender_height_weight))
async def student_gender_height_weight(message: types.Message, state: FSMContext):
    await state.update_data(gender_height_weight=message.text)
    await message.answer(
        "<b>Характер</b>\nОпиши свой характер. Мне, честно говоря, глубоко безразлично, что ты там о себе думаешь, но правила есть правила. "
        "Четыре строки. «Добрый и отзывчивый» — и я зевну так, что ты испугаешься. Лучше уж пиши, что ты скрытый маньяк. Хоть поржу."
    )
    await state.set_state(StudentForm.character)


@dp.message(StateFilter(StudentForm.character))
async def student_character(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 4:
        await message.answer(f"⚠️ Характер должен содержать минимум 4 строки. Сейчас {len(lines)}. Напишите подробнее:")
        return
    await state.update_data(character=message.text)
    await message.answer(
        "<b>Способности</b>\nНа что ты способен? Не надейся меня впечатлить — я видел магов, которые создавали миры. Я сам создавал миры. "
        "Но давай, расскажи, как ты умеешь зажигать свечку пальцем. Только всесилие, бессмертие и прочее — ЗАПРЕЩЕНО. Это моё. "
        "Я и так слишком щедр, позволяя тебе дышать одним воздухом со мной."
    )
    await state.set_state(StudentForm.abilities)


@dp.message(StateFilter(StudentForm.abilities))
async def student_abilities(message: types.Message, state: FSMContext):
    await state.update_data(abilities=message.text)
    await message.answer(
        "<b>Слабости и страхи</b>\nЧего ты боишься? Меня, надеюсь, уже боишься. Если нет — ничего, это приходит со временем. "
        "Слабости способностей тоже пиши. Мне это пригодится, чтобы… ну, просто чтобы было. Я коллекционирую чужие уязвимости. Такое вот хобби у бессмертного красавца."
    )
    await state.set_state(StudentForm.weaknesses)


@dp.message(StateFilter(StudentForm.weaknesses))
async def student_weaknesses(message: types.Message, state: FSMContext):
    await state.update_data(weaknesses=message.text)
    await message.answer(
        "<b>Факты</b>\nРазвлеки меня. Любимая еда, хобби, шрамы. Только не вздумай писать «люблю закаты и прогулки» — я тут же потеряю к тебе остатки интереса. "
        "А их и так немного. Я пока подумаю, не добавить ли ещё один мир. Или леденцов. Я люблю леденцы."
    )
    await state.set_state(StudentForm.facts)


@dp.message(StateFilter(StudentForm.facts))
async def student_facts(message: types.Message, state: FSMContext):
    await state.update_data(facts=message.text)
    await message.answer(
        "<b>Внешность</b>\nОпиши, как выглядишь. Если есть картинка — две строки. Я сравню со своим отражением. Спойлер: ты проиграешь. "
        "Мои рога, кстати, светятся в темноте. Бесполезно, но красиво. А ты? Ладно, пиши уже, не заставляй меня ждать. Ждать я не люблю, хотя ты того не стоишь."
    )
    await state.set_state(StudentForm.appearance)


@dp.message(StateFilter(StudentForm.appearance))
async def student_appearance(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 2:
        await message.answer("⚠️ Внешность должна содержать минимум 2 строки. Опишите подробнее.")
        return
    await state.update_data(appearance=message.text)
    await message.answer(
        "<b>Биография</b>\nОт восьми строк. Откуда ты, кто родители, как ты вообще дожил до этого момента. Мне это нужно не для того, чтобы проникнуться твоей драмой — упаси боже, — "
        "а чтобы понять, сколько ты протянешь в моей Академии. Если биография скучная — приукрась. Я разрешаю. Я сегодня щедрый. Зеркало сказало, что я неотразим, и я ему верю."
    )
    await state.set_state(StudentForm.biography)


@dp.message(StateFilter(StudentForm.biography))
async def student_biography(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 8:
        await message.answer(f"⚠️ Биография должна содержать минимум 8 строк. Сейчас {len(lines)}. Напишите подробнее:")
        return
    await state.update_data(biography=message.text)
    await message.answer(
        "<b>Курс</b>\nНа какой курс собрался? Сверься с регламентом, я не буду повторять дважды. Если перепутаешь — останешься на первом курсе навсегда. "
        "Мне-то что, я всё равно буду тут, вечный и прекрасный, а вот ты состаришься за партой. Забавно? Возможно."
    )
    await state.set_state(StudentForm.course)


@dp.message(StateFilter(StudentForm.course))
async def student_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    data = await state.get_data()
    await state.clear()

    text = (
        "📄 <b>Новая анкета ученика</b>\n\n"
        f"<b>Имя и фамилия:</b> {esc(data['name'])}\n"
        f"<b>Раса:</b> {esc(data['race'])}\n"
        f"<b>Возраст:</b> {esc(data['age'])}\n"
        f"<b>Пол/Рост/Вес:</b> {esc(data['gender_height_weight'])}\n"
        f"<b>Характер:</b>\n{esc(data['character'])}\n"
        f"<b>Способности:</b>\n{esc(data['abilities'])}\n"
        f"<b>Слабости и страхи:</b>\n{esc(data['weaknesses'])}\n"
        f"<b>Факты:</b>\n{esc(data['facts'])}\n"
        f"<b>Внешность:</b>\n{esc(data['appearance'])}\n"
        f"<b>Биография:</b>\n{esc(data['biography'])}\n"
        f"<b>Курс:</b> {esc(data['course'])}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{message.from_user.id}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}")]
    ])

    await bot.send_message(GROUP_CHAT_ID, text, reply_markup=keyboard)
    await message.answer(
        "✅ Анкета отправлена на проверку.\n\n"
        "<b>На правки — три дня.</b> Не успеешь — твои проблемы. Мне не к спеху. Я могу ждать вечность. Но тебе-то, смертный, вечность не светит."
    )


# ---------- АНКЕТА ПЕРСОНАЛА ----------
@dp.message(StateFilter(StaffForm.position))
async def staff_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer(
        "<b>Имя / Фамилия</b>\nПредставься. Только быстро. Если имя дурацкое, я всё равно забуду его через пять минут и буду звать тебя «эй, ты». "
        "Я так делаю со всеми, это не личное. Просто вы все для меня на одно лицо."
    )
    await state.set_state(StaffForm.name)


@dp.message(StateFilter(StaffForm.name))
async def staff_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "<b>Возраст</b>\nСколько тебе лет? Мне не важно, но анкета требует. Я в это время полирую рога. Они у меня, знаешь ли, требуют ухода. "
        "Не то что твоя биография. Кстати, возраст. Жду."
    )
    await state.set_state(StaffForm.age)


@dp.message(StateFilter(StaffForm.age))
async def staff_age(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Возраст должен быть числом. Попробуйте снова.")
        return
    age = int(message.text)
    if age < 1 or age > 120:
        await message.answer("⚠️ Возраст от 1 до 120. Введите корректно.")
        return
    await state.update_data(age=age)
    await message.answer(
        "<b>Раса</b>\nИ кто ты у нас по природе? Человек, эльф, недодемон? Пока ты будешь перечислять, я, пожалуй, пересчитаю свои рога. "
        "О, у меня их два. Прекрасных. Тёмно-синих. А у тебя? Ну давай, не томи, кто ты там по расовой принадлежности.",
        reply_markup=get_race_keyboard()
    )
    await state.set_state(StaffForm.race)


@dp.callback_query(StateFilter(StaffForm.race))
async def staff_race(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_", 1)[1]
    if key in RACE_MAP:
        race_name = RACE_MAP[key]
        await state.update_data(race=race_name)
        await callback.message.delete()
        await bot.send_message(callback.message.chat.id, f"Выбрана раса: {esc(race_name)}")
        await bot.send_message(
            callback.message.chat.id,
            "<b>Пол / Рост / Вес</b>\nКто ты? пол, рост, вес. Кратко. Пока ты пишешь, я прикидываю, достаточно ли хорош сегодня мой профиль. "
            "Кажется, да. Особенно правый рог. Левый тоже ничего. Ладно, я отвлёкся. Ты всё ещё тут? Пиши давай."
        )
        await state.set_state(StaffForm.gender_height_weight)
        await callback.answer()
    else:
        await callback.answer("Выберите расу из предложенных", show_alert=True)


@dp.message(StateFilter(StaffForm.gender_height_weight))
async def staff_gender_height_weight(message: types.Message, state: FSMContext):
    await state.update_data(gender_height_weight=message.text)
    await message.answer(
        "<b>Характер</b>\nРасскажи, с кем мне предстоит делить воздух. Я надеюсь, ты не зануда. Я ненавижу зануд. Если ты садист — отлично, но помни: главный садист здесь я. "
        "И я ревнив. Не посягай на моё место, и мы поладим. Наверное. Не уверен. Мне вообще всё равно."
    )
    await state.set_state(StaffForm.character)


@dp.message(StateFilter(StaffForm.character))
async def staff_character(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 4:
        await message.answer(f"⚠️ Характер должен быть минимум 4 строки. Сейчас {len(lines)}. Напишите подробнее:")
        return
    await state.update_data(character=message.text)
    await message.answer(
        "<b>Способности, магия и магическое направление</b>\nЧто ты умеешь? Кроме как вызывать у меня лёгкую скуку. "
        "Всесилие, бессмертие, антимагия — моё. Даже не дыши в их сторону. Если твои способности — что-то вроде «хорошо готовлю зелья», то хотя бы готовь их с фантазией. "
        "Я люблю, когда красиво. Себя я люблю больше, но и красоту ценю."
    )
    await state.set_state(StaffForm.abilities)


@dp.message(StateFilter(StaffForm.abilities))
async def staff_abilities(message: types.Message, state: FSMContext):
    await state.update_data(abilities=message.text)
    await message.answer(
        "<b>Слабости, страхи</b>\nВсё выкладывай. Я, как истинный коллекционер, бережно храню чужие уязвимости в своей голове. "
        "Если ты вампир и боишься солнечного света — не переживай, в моей Академии всегда сумрачно. Я тоже люблю сумрак. Он мне идёт."
    )
    await state.set_state(StaffForm.weaknesses)


@dp.message(StateFilter(StaffForm.weaknesses))
async def staff_weaknesses(message: types.Message, state: FSMContext):
    await state.update_data(weaknesses=message.text)
    await message.answer(
        "<b>Факты</b>\nПривычки, хобби, бывшие работы. У меня, например, есть хобби — создавать миры и забывать о них. Ещё я коллекционирую проклятия. "
        "А ты? Только не говори, что вышиваешь крестиком. Я же засмею. И буду смеяться долго. У меня смех красивый, но обидный."
    )
    await state.set_state(StaffForm.facts)


@dp.message(StateFilter(StaffForm.facts))
async def staff_facts(message: types.Message, state: FSMContext):
    await state.update_data(facts=message.text)
    await message.answer(
        "<b>Внешность</b>\nКартинка или описание. Только не пытайся выглядеть лучше меня. Это бессмысленно. Я — произведение искусства, а ты — так, эскиз. "
        "Одежду тоже опиши. Если ты одет как пугало, я переодену тебя сам. Не из заботы — просто ты будешь портить мне вид."
    )
    await state.set_state(StaffForm.appearance)


@dp.message(StateFilter(StaffForm.appearance))
async def staff_appearance(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 2:
        await message.answer("⚠️ Внешность должна быть минимум 2 строки. Опишите подробнее.")
        return
    await state.update_data(appearance=message.text)
    await message.answer(
        "<b>Биография</b>\nГде учился, кого предавал, почему решил, что достоин служить мне. Чтобы стать преподавателем, сдавал экзамен. "
        "Я не принимаю экзамены, я выше этого. Но биографию прочту. Если она скучная — я добавлю в неё красок. В основном красных. Люблю красный."
    )
    await state.set_state(StaffForm.biography)


@dp.message(StateFilter(StaffForm.biography))
async def staff_biography(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 8:
        await message.answer(f"⚠️ Биография должна быть минимум 8 строк. Сейчас {len(lines)}. Напишите подробнее:")
        return
    await state.update_data(biography=message.text)
    data = await state.get_data()
    await state.clear()

    text = (
        "📄 <b>Новая анкета персонала</b>\n\n"
        f"<b>Должность:</b> {esc(data['position'])}\n"
        f"<b>Имя/Фамилия:</b> {esc(data['name'])}\n"
        f"<b>Возраст:</b> {esc(data['age'])}\n"
        f"<b>Раса:</b> {esc(data['race'])}\n"
        f"<b>Пол/Рост/Вес:</b> {esc(data['gender_height_weight'])}\n"
        f"<b>Характер:</b>\n{esc(data['character'])}\n"
        f"<b>Способности, магия и магическое направление:</b>\n{esc(data['abilities'])}\n"
        f"<b>Слабости, страхи:</b>\n{esc(data['weaknesses'])}\n"
        f"<b>Факты:</b>\n{esc(data['facts'])}\n"
        f"<b>Внешность:</b>\n{esc(data['appearance'])}\n"
        f"<b>Биография:</b>\n{esc(data['biography'])}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{message.from_user.id}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}")]
    ])

    await bot.send_message(GROUP_CHAT_ID, text, reply_markup=keyboard)
    await message.answer(
        "✅ Анкета отправлена на проверку.\n\n"
        "<b>Бронь — неделя. Анкету править — три дня.</b> Если не успеешь… да плевать, если честно. Найдёшь другую работу. Или не найдёшь. "
        "Я в любом случае останусь тут — великий, прекрасный и абсолютно довольный собой."
    )


# ---------- ОБРАБОТЧИК КНОПОК (ОДОБРИТЬ / ОТКЛОНИТЬ) ----------
@dp.callback_query()
async def handle_group_action(callback: types.CallbackQuery, state: FSMContext):
    # Обрабатываем только ожидаемый формат "approve_123" / "reject_123",
    # чтобы случайный callback_data не уронил обработчик.
    parts = callback.data.split("_", 1)
    if len(parts) != 2 or parts[0] not in ("approve", "reject") or not parts[1].isdigit():
        await callback.answer()
        return

    action, user_id_str = parts
    user_id = int(user_id_str)

    try:
        member = await bot.get_chat_member(GROUP_CHAT_ID, callback.from_user.id)
    except Exception as e:
        logging.warning("Не удалось проверить права пользователя %s: %s", callback.from_user.id, e)
        await callback.answer("⚠️ Не удалось проверить ваши права.", show_alert=True)
        return

    if member.status not in ("administrator", "creator"):
        await callback.answer("⛔ Только администраторы группы могут принимать решения.", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)

    admin = callback.from_user
    admin_mention = f"@{admin.username}" if admin.username else f"<a href='tg://user?id={admin.id}'>{esc(admin.first_name)}</a>"

    if action == "approve":
        new_text = callback.message.text + f"\n\n✅ <b>Одобрено</b> администратором {admin_mention}"
        await bot.edit_message_text(new_text, chat_id=GROUP_CHAT_ID, message_id=callback.message.message_id)
        try:
            await bot.send_message(user_id, "🎉 Ваша анкета <b>одобрена</b>! Добро пожаловать.")
        except Exception as e:
            logging.warning("Не удалось уведомить пользователя %s: %s", user_id, e)
        await callback.answer("Анкета принята", show_alert=False)

    elif action == "reject":
        await state.update_data(
            user_id=user_id,
            original_message_id=callback.message.message_id,
            original_text=callback.message.text,
            admin_mention=admin_mention,
            admin_id=admin.id
        )
        request_msg = await bot.send_message(
            GROUP_CHAT_ID,
            f"👤 {admin_mention}, напишите <b>причину отклонения</b> в ответ на это сообщение."
        )
        await state.update_data(request_message_id=request_msg.message_id)
        await state.set_state(RejectReason.waiting_for_reason)
        await callback.answer("Напишите причину в группе, ответив на запрос.", show_alert=False)


# ---------- ОБРАБОТЧИК ПРИЧИНЫ ОТКЛОНЕНИЯ ----------
@dp.message(StateFilter(RejectReason.waiting_for_reason))
async def process_reject_reason(message: types.Message, state: FSMContext):
    if message.chat.id != GROUP_CHAT_ID:
        return

    data = await state.get_data()
    if not data:
        await message.answer("⚠️ Данные утеряны. Нажмите кнопку отклонения заново.")
        await state.clear()
        return

    request_msg_id = data.get('request_message_id')
    if not message.reply_to_message or message.reply_to_message.message_id != request_msg_id:
        await message.answer("❌ Пожалуйста, ответьте на сообщение с запросом причины (это нужно для связки).")
        return

    if message.from_user.id != data.get('admin_id'):
        await message.answer("⛔ Вы не тот администратор, который инициировал отклонение.")
        return

    reason = (message.text or "").strip()
    if not reason:
        await message.answer("⚠️ Причина не может быть пустой. Напишите текст.")
        return

    user_id = data['user_id']
    original_text = data['original_text']
    original_msg_id = data['original_message_id']
    admin_mention = data['admin_mention']

    new_text = original_text + f"\n\n❌ <b>Отклонено</b> администратором {admin_mention}\n<b>Причина:</b> {esc(reason)}"
    try:
        await bot.edit_message_text(new_text, chat_id=GROUP_CHAT_ID, message_id=original_msg_id)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка редактирования: {esc(e)}")
        return

    try:
        await bot.send_message(user_id, f"❌ Ваша анкета <b>отклонена</b>.\nПричина: {esc(reason)}")
    except Exception as e:
        logging.warning("Не удалось уведомить пользователя %s: %s", user_id, e)

    try:
        await bot.delete_message(GROUP_CHAT_ID, request_msg_id)
    except Exception:
        pass

    await state.clear()
    await message.answer("✅ Причина принята, анкета отклонена.")


# ---------- ЗАПУСК ВЕБ-СЕРВЕРА И БОТА ----------
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
    await site.start()
    logging.info("🌐 Web server started on port %s", PORT)


async def main():
    # Устанавливаем HTML как parse_mode по умолчанию для всех сообщений бота,
    # чтобы не указывать его каждый раз вручную.
    bot.parse_mode = "HTML"
    await start_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
