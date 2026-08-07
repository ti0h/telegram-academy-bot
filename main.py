import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# ------------------ КОНФИГ ------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", 0))
if not BOT_TOKEN or not GROUP_CHAT_ID:
    raise ValueError("Переменные окружения BOT_TOKEN и GROUP_CHAT_ID обязательны")
# -------------------------------------------

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ---------- СОСТОЯНИЕ ДЛЯ ВЫБОРА ТИПА ----------
class Choice(StatesGroup):
    waiting = State()

# ---------- СОСТОЯНИЯ ДЛЯ АНКЕТЫ УЧЕНИКА ----------
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

# ---------- СОСТОЯНИЯ ДЛЯ АНКЕТЫ ПЕРСОНАЛА ----------
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

# ---------- СОСТОЯНИЕ ДЛЯ ПРИЧИНЫ ОТКЛОНЕНИЯ ----------
class RejectReason(StatesGroup):
    waiting_for_reason = State()

# ---------- /start ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    intro = (
        "А, это ты. Ну давай, заходи, раз уж пришёл. Только учти: я сейчас в процессе важного ничегонеделания, так что говори быстро.\n"
        "Хочешь анкету создать? Похвально. Даже не знаю, что более жалко - твоя уверенность, что ты достоин здесь учиться, или тот факт, что я действительно потрачу на тебя время.\n"
        "Впрочем, у меня сегодня хорошее настроение - я полюбовался на себя в зеркало, а это всегда поднимает дух.\n"
        "Так что давай, смертный, ученик ты или персонал?"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧑‍🎓 Ученик", callback_data="choice_student")],
        [InlineKeyboardButton(text="👨‍🏫 Персонал", callback_data="choice_staff")]
    ])
    await message.answer(intro, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(Choice.waiting)

# ---------- ОБРАБОТКА ВЫБОРА ТИПА ----------
@dp.callback_query(StateFilter(Choice.waiting))
async def process_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "choice_student":
        await callback.message.delete()
        await bot.send_message(
            callback.message.chat.id,
            "**Для ученика**\n\n"
            "Назовись. Только без титулов, умоляю. «Лорд Тьмы», «Повелительница Звёзд» - я этого не вынесу. "
            "У меня у самого их десяток, и я не разбрасываюсь. Просто имя. Мне, в общем-то, всё равно, но формальности требуют.",
            parse_mode="Markdown"
        )
        await state.set_state(StudentForm.name)
        await callback.answer()
    elif callback.data == "choice_staff":
        await callback.message.delete()
        await bot.send_message(
            callback.message.chat.id,
            "**Для персонала**\n\n"
            "Решил устроиться ко мне на работу? Смело. Или глупо. Я пока не определился. Знаешь, что я люблю больше, чем хаос? Только себя. "
            "Так что, если ты не готов мириться с моим величием, капризами и тем, что я временами вообще забываю о существовании персонала, - лучше уйди сейчас. Я даже не замечу.\n\n"
            "**Должность**\n"
            "Кем хочешь быть? Преподавателем? Целителем? Смотрителем леса? Выбирай, мне без разницы. Только учти: если облажаешься, я разочаруюсь. "
            "А когда я разочаровываюсь, я начинаю искать развлечений. Обычно за чужой счёт. Ну так что, не передумал? Нет? Ну смотри.",
            parse_mode="Markdown"
        )
        await state.set_state(StaffForm.position)
        await callback.answer()

# ---------- АНКЕТА УЧЕНИКА ----------
@dp.message(StateFilter(StudentForm.name))
async def student_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧝 Темный эльф", callback_data="race_dark_elf")],
        [InlineKeyboardButton(text="🧝 Эльф", callback_data="race_elf")],
        [InlineKeyboardButton(text="🧑 Человек", callback_data="race_human")],
        [InlineKeyboardButton(text="⛏ Гном", callback_data="race_dwarf")],
        [InlineKeyboardButton(text="👹 Орк", callback_data="race_orc")]
    ])
    await message.answer(
        "**Раса**\nИ кто ты у нас по природе? Человек, эльф, недодемон? Пока ты будешь перечислять, я, пожалуй, пересчитаю свои рога. "
        "О, у меня их два. Прекрасных. Тёмно-синих. А у тебя? Ну давай, не томи, кто ты там по расовой принадлежности.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.race)

@dp.callback_query(StateFilter(StudentForm.race))
async def student_race(callback: types.CallbackQuery, state: FSMContext):
    race_map = {
        "race_dark_elf": "Темный эльф",
        "race_elf": "Эльф",
        "race_human": "Человек",
        "race_dwarf": "Гном",
        "race_orc": "Орк"
    }
    race = race_map.get(callback.data)
    if race:
        await state.update_data(race=race)
        await callback.message.delete()
        await bot.send_message(callback.message.chat.id, f"Выбрана раса: {race}", parse_mode="Markdown")
        await bot.send_message(
            callback.message.chat.id,
            "**Возраст**\nНе подскажешь возраст? Мой я давно не считаю, потому что цифры не способны вместить моё величие. "
            "А вот твой - назови. Сверься с регламентом. Если тебе под сотню, а ты прёшься на первый курс, я даже не разозлюсь - мне просто станет ещё скучнее, чем было.",
            parse_mode="Markdown"
        )
        await state.set_state(StudentForm.age)
        await callback.answer()
    else:
        await callback.answer("Выберите расу из предложенных", show_alert=True)

@dp.message(StateFilter(StudentForm.age))
async def student_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Возраст должен быть числом. Попробуйте снова.", parse_mode="Markdown")
        return
    age = int(message.text)
    if age < 1 or age > 120:
        await message.answer("⚠️ Возраст должен быть от 1 до 120. Введите корректно.", parse_mode="Markdown")
        return
    await state.update_data(age=age)
    await message.answer(
        "**Пол / Рост / Вес**\nПол, рост, вес. Три скучных слова. Если у тебя есть что-то интересное в пропорциях - я, может, и подниму бровь. Но вряд ли.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.gender_height_weight)

@dp.message(StateFilter(StudentForm.gender_height_weight))
async def student_gender_height_weight(message: types.Message, state: FSMContext):
    await state.update_data(gender_height_weight=message.text)
    await message.answer(
        "**Характер**\nОпиши свой характер. Мне, честно говоря, глубоко безразлично, что ты там о себе думаешь, но правила есть правила. "
        "Четыре строки. «Добрый и отзывчивый» - и я зевну так, что ты испугаешься. Лучше уж пиши, что ты скрытый маньяк. Хоть поржу.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.character)

@dp.message(StateFilter(StudentForm.character))
async def student_character(message: types.Message, state: FSMContext):
    lines = message.text.splitlines()
    if len(lines) < 4:
        await message.answer(
            f"⚠️ Характер должен содержать минимум 4 строки. Сейчас {len(lines)}. Напишите подробнее:",
            parse_mode="Markdown"
        )
        return
    await state.update_data(character=message.text)
    await message.answer(
        "**Способности**\nНа что ты способен? Не надейся меня впечатлить - я видел магов, которые создавали миры. Я сам создавал миры. "
        "Но давай, расскажи, как ты умеешь зажигать свечку пальцем. Только всесилие, бессмертие и прочее - ЗАПРЕЩЕНО. Это моё. "
        "Я и так слишком щедр, позволяя тебе дышать одним воздухом со мной.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.abilities)

@dp.message(StateFilter(StudentForm.abilities))
async def student_abilities(message: types.Message, state: FSMContext):
    await state.update_data(abilities=message.text)
    await message.answer(
        "**Слабости и страхи**\nЧего ты боишься? Меня, надеюсь, уже боишься. Если нет - ничего, это приходит со временем. "
        "Слабости способностей тоже пиши. Мне это пригодится, чтобы… ну, просто чтобы было. Я коллекционирую чужие уязвимости. Такое вот хобби у бессмертного красавца.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.weaknesses)

@dp.message(StateFilter(StudentForm.weaknesses))
async def student_weaknesses(message: types.Message, state: FSMContext):
    await state.update_data(weaknesses=message.text)
    await message.answer(
        "**Факты**\nРазвлеки меня. Любимая еда, хобби, шрамы. Только не вздумай писать «люблю закаты и прогулки» - я тут же потеряю к тебе остатки интереса. "
        "А их и так немного. Я пока подумаю, не добавить ли ещё один мир. Или леденцов. Я люблю леденцы.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.facts)

@dp.message(StateFilter(StudentForm.facts))
async def student_facts(message: types.Message, state: FSMContext):
    await state.update_data(facts=message.text)
    await message.answer(
        "**Внешность**\nОпиши, как выглядишь. Если есть картинка - две строки. Я сравню со своим отражением. Спойлер: ты проиграешь. "
        "Мои рога, кстати, светятся в темноте. Бесполезно, но красиво. А ты? Ладно, пиши уже, не заставляй меня ждать. Ждать я не люблю, хотя ты того не стоишь.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.appearance)

@dp.message(StateFilter(StudentForm.appearance))
async def student_appearance(message: types.Message, state: FSMContext):
    lines = message.text.splitlines()
    if len(lines) < 2:
        await message.answer("⚠️ Внешность должна содержать минимум 2 строки. Опишите подробнее.", parse_mode="Markdown")
        return
    await state.update_data(appearance=message.text)
    await message.answer(
        "**Биография**\nОт восьми строк. Откуда ты, кто родители, как ты вообще дожил до этого момента. Мне это нужно не для того, чтобы проникнуться твоей драмой - упаси боже, - "
        "а чтобы понять, сколько ты протянешь в моей Академии. Если биография скучная - приукрась. Я разрешаю. Я сегодня щедрый. Зеркало сказало, что я неотразим, и я ему верю.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.biography)

@dp.message(StateFilter(StudentForm.biography))
async def student_biography(message: types.Message, state: FSMContext):
    lines = message.text.splitlines()
    if len(lines) < 8:
        await message.answer(
            f"⚠️ Биография должна содержать минимум 8 строк. Сейчас {len(lines)}. Напишите подробнее:",
            parse_mode="Markdown"
        )
        return
    await state.update_data(biography=message.text)
    await message.answer(
        "**Курс**\nНа какой курс собрался? Сверься с регламентом, я не буду повторять дважды. Если перепутаешь - останешься на первом курсе навсегда. "
        "Мне-то что, я всё равно буду тут, вечный и прекрасный, а вот ты состаришься за партой. Забавно? Возможно.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentForm.course)

@dp.message(StateFilter(StudentForm.course))
async def student_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    data = await state.get_data()
    await state.clear()

    text = (
        "📄 **Новая анкета ученика**\n\n"
        f"**Имя и фамилия:** {data['name']}\n"
        f"**Раса:** {data['race']}\n"
        f"**Возраст:** {data['age']}\n"
        f"**Пол/Рост/Вес:** {data['gender_height_weight']}\n"
        f"**Характер:**\n{data['character']}\n"
        f"**Способности:**\n{data['abilities']}\n"
        f"**Слабости и страхи:**\n{data['weaknesses']}\n"
        f"**Факты:**\n{data['facts']}\n"
        f"**Внешность:**\n{data['appearance']}\n"
        f"**Биография:**\n{data['biography']}\n"
        f"**Курс:** {data['course']}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{message.from_user.id}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}")]
    ])

    await bot.send_message(GROUP_CHAT_ID, text, parse_mode="Markdown", reply_markup=keyboard)
    await message.answer(
        "✅ Анкета отправлена на проверку.\n\n"
        "**На правки - три дня.** Не успеешь - твои проблемы. Мне не к спеху. Я могу ждать вечность. Но тебе-то, смертный, вечность не светит.",
        parse_mode="Markdown"
    )

# ---------- АНКЕТА ПЕРСОНАЛА ----------
@dp.message(StateFilter(StaffForm.position))
async def staff_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer(
        "**Имя / Фамилия**\nПредставься. Только быстро. Если имя дурацкое, я всё равно забуду его через пять минут и буду звать тебя «эй, ты». "
        "Я так делаю со всеми, это не личное. Просто вы все для меня на одно лицо.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.name)

@dp.message(StateFilter(StaffForm.name))
async def staff_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "**Возраст**\nСколько тебе лет? Мне не важно, но анкета требует. Я в это время полирую рога. Они у меня, знаешь ли, требуют ухода. "
        "Не то что твоя биография. Кстати, возраст. Жду.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.age)

@dp.message(StateFilter(StaffForm.age))
async def staff_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Возраст должен быть числом. Попробуйте снова.", parse_mode="Markdown")
        return
    age = int(message.text)
    if age < 1 or age > 120:
        await message.answer("⚠️ Возраст от 1 до 120. Введите корректно.", parse_mode="Markdown")
        return
    await state.update_data(age=age)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧝 Темный эльфsfdsfdsfdsf", callback_data="race_dark_elf")],
        [InlineKeyboardButton(text="🧝 Эльф", callback_data="race_elf")],
        [InlineKeyboardButton(text="🧑 Человек", callback_data="race_human")],
        [InlineKeyboardButton(text="⛏ Гном", callback_data="race_dwarf")],
        [InlineKeyboardButton(text="👹 Орк", callback_data="race_orc")]
        [InlineKeyboardButton(text="👹 Огр", callback_data="race_ogr")]
    ])
    await message.answer(
        "**Раса**\nИ кто ты у нас по природе? Человек, эльф, недодемон? Пока ты будешь перечислять, я, пожалуй, пересчитаю свои рога. "
        "О, у меня их два. Прекрасных. Тёмно-синих. А у тебя? Ну давай, не томи, кто ты там по расовой принадлежности.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.race)

@dp.callback_query(StateFilter(StaffForm.race))
async def staff_race(callback: types.CallbackQuery, state: FSMContext):
    race_map = {
        "race_dark_elf": "Темный эльф",
        "race_elf": "Эльф",
        "race_human": "Человек",
        "race_dwarf": "Гном",
        "race_orc": "Орк"
    }
    race = race_map.get(callback.data)
    if race:
        await state.update_data(race=race)
        await callback.message.delete()
        await bot.send_message(callback.message.chat.id, f"Выбрана раса: {race}", parse_mode="Markdown")
        await bot.send_message(
            callback.message.chat.id,
            "**Пол / Рост / Вес**\nКто ты? пол, рост, вес. Кратко. Пока ты пишешь, я прикидываю, достаточно ли хорош сегодня мой профиль. "
            "Кажется, да. Особенно правый рог. Левый тоже ничего. Ладно, я отвлёкся. Ты всё ещё тут? Пиши давай.",
            parse_mode="Markdown"
        )
        await state.set_state(StaffForm.gender_height_weight)
        await callback.answer()
    else:
        await callback.answer("Выберите расу из предложенных", show_alert=True)

@dp.message(StateFilter(StaffForm.gender_height_weight))
async def staff_gender_height_weight(message: types.Message, state: FSMContext):
    await state.update_data(gender_height_weight=message.text)
    await message.answer(
        "**Характер**\nРасскажи, с кем мне предстоит делить воздух. Я надеюсь, ты не зануда. Я ненавижу зануд. Если ты садист - отлично, но помни: главный садист здесь я. "
        "И я ревнив. Не посягай на моё место, и мы поладим. Наверное. Не уверен. Мне вообще всё равно.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.character)

@dp.message(StateFilter(StaffForm.character))
async def staff_character(message: types.Message, state: FSMContext):
    lines = message.text.splitlines()
    if len(lines) < 4:
        await message.answer(
            f"⚠️ Характер должен быть минимум 4 строки. Сейчас {len(lines)}. Напишите подробнее:",
            parse_mode="Markdown"
        )
        return
    await state.update_data(character=message.text)
    await message.answer(
        "**Способности, магия и магическое направление**\nЧто ты умеешь? Кроме как вызывать у меня лёгкую скуку. "
        "Всесилие, бессмертие, антимагия - моё. Даже не дыши в их сторону. Если твои способности - что-то вроде «хорошо готовлю зелья», то хотя бы готовь их с фантазией. "
        "Я люблю, когда красиво. Себя я люблю больше, но и красоту ценю.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.abilities)

@dp.message(StateFilter(StaffForm.abilities))
async def staff_abilities(message: types.Message, state: FSMContext):
    await state.update_data(abilities=message.text)
    await message.answer(
        "**Слабости, страхи**\nВсё выкладывай. Я, как истинный коллекционер, бережно храню чужие уязвимости в своей голове. "
        "Если ты вампир и боишься солнечного света - не переживай, в моей Академии всегда сумрачно. Я тоже люблю сумрак. Он мне идёт.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.weaknesses)

@dp.message(StateFilter(StaffForm.weaknesses))
async def staff_weaknesses(message: types.Message, state: FSMContext):
    await state.update_data(weaknesses=message.text)
    await message.answer(
        "**Факты**\nПривычки, хобби, бывшие работы. У меня, например, есть хобби - создавать миры и забывать о них. Ещё я коллекционирую проклятия. "
        "А ты? Только не говори, что вышиваешь крестиком. Я же засмею. И буду смеяться долго. У меня смех красивый, но обидный.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.facts)

@dp.message(StateFilter(StaffForm.facts))
async def staff_facts(message: types.Message, state: FSMContext):
    await state.update_data(facts=message.text)
    await message.answer(
        "**Внешность**\nКартинка или описание. Только не пытайся выглядеть лучше меня. Это бессмысленно. Я - произведение искусства, а ты - так, эскиз. "
        "Одежду тоже опиши. Если ты одет как пугало, я переодену тебя сам. Не из заботы - просто ты будешь портить мне вид.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.appearance)

@dp.message(StateFilter(StaffForm.appearance))
async def staff_appearance(message: types.Message, state: FSMContext):
    lines = message.text.splitlines()
    if len(lines) < 2:
        await message.answer("⚠️ Внешность должна быть минимум 2 строки. Опишите подробнее.", parse_mode="Markdown")
        return
    await state.update_data(appearance=message.text)
    await message.answer(
        "**Биография**\nГде учился, кого предавал, почему решил, что достоин служить мне. Чтобы стать преподавателем, сдавал экзамен. "
        "Я не принимаю экзамены, я выше этого. Но биографию прочту. Если она скучная - я добавить в неё красок. В основном красных. Люблю красный.",
        parse_mode="Markdown"
    )
    await state.set_state(StaffForm.biography)

@dp.message(StateFilter(StaffForm.biography))
async def staff_biography(message: types.Message, state: FSMContext):
    lines = message.text.splitlines()
    if len(lines) < 8:
        await message.answer(
            f"⚠️ Биография должна быть минимум 8 строк. Сейчас {len(lines)}. Напишите подробнее:",
            parse_mode="Markdown"
        )
        return
    await state.update_data(biography=message.text)
    data = await state.get_data()
    await state.clear()

    text = (
        "📄 **Новая анкета персонала**\n\n"
        f"**Должность:** {data['position']}\n"
        f"**Имя/Фамилия:** {data['name']}\n"
        f"**Возраст:** {data['age']}\n"
        f"**Раса:** {data['race']}\n"
        f"**Пол/Рост/Вес:** {data['gender_height_weight']}\n"
        f"**Характер:**\n{data['character']}\n"
        f"**Способности, магия и магическое направление:**\n{data['abilities']}\n"
        f"**Слабости, страхи:**\n{data['weaknesses']}\n"
        f"**Факты:**\n{data['facts']}\n"
        f"**Внешность:**\n{data['appearance']}\n"
        f"**Биография:**\n{data['biography']}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{message.from_user.id}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}")]
    ])

    await bot.send_message(GROUP_CHAT_ID, text, parse_mode="Markdown", reply_markup=keyboard)
    await message.answer(
        "✅ Анкета отправлена на проверку.\n\n"
        "**Бронь - неделя. Анкету править - три дня.** Если не успеешь… да плевать, если честно. Найдёшь другую работу. Или не найдёшь. Я в любом случае останусь тут - великий, прекрасный и абсолютно довольный собой.",
        parse_mode="Markdown"
    )

# ---------- ОБРАБОТЧИК КНОПОК (ОДОБРИТЬ / ОТКЛОНИТЬ) ----------
@dp.callback_query()
async def handle_group_action(callback: types.CallbackQuery, state: FSMContext):
    # Проверка прав администратора
    try:
        member = await bot.get_chat_member(GROUP_CHAT_ID, callback.from_user.id)
    except:
        await callback.answer("⚠️ Не удалось проверить ваши права.", show_alert=True)
        return

    if member.status not in ("administrator", "creator"):
        await callback.answer("⛔ Только администраторы группы могут принимать решения.", show_alert=True)
        return

    action, user_id_str = callback.data.split("_")
    user_id = int(user_id_str)

    # Убираем кнопки
    await callback.message.edit_reply_markup(reply_markup=None)

    admin = callback.from_user
    admin_mention = f"@{admin.username}" if admin.username else f"[{admin.first_name}](tg://user?id={admin.id})"

    if action == "approve":
        new_text = callback.message.text + f"\n\n✅ **Одобрено** администратором {admin_mention}"
        await bot.edit_message_text(new_text, chat_id=GROUP_CHAT_ID, message_id=callback.message.message_id, parse_mode="Markdown")
        await bot.send_message(user_id, "Анкета принята.\n\nНадо же, принята. Не скажу, что я в восторге - я вообще редко бываю в восторге от кого-то, кроме себя, - но твоя писанина меня хотя бы не усыпила. Это уже достижение. Так что заходи, располагайся и постарайся не умереть в первую же неделю. Мне будет… ну, не то чтобы жаль, скорее неловко перед статистикой. И да, не думай, что мы теперь друзья. Ты здесь гость, я здесь - вечность. Разницу улавливаешь? Вот и славно.\n\nhttps://t.me/+Iji2mDCmE24yMTNi", parse_mode="Markdown")
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
            f"👤 {admin_mention}, напишите **причину отклонения** в ответ на это сообщение.",
            parse_mode="Markdown"
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
        await message.answer("⚠️ Данные утеряны. Нажмите кнопку отклонения заново.", parse_mode="Markdown")
        await state.clear()
        return

    request_msg_id = data.get('request_message_id')
    if not message.reply_to_message or message.reply_to_message.message_id != request_msg_id:
        await message.answer("❌ Пожалуйста, ответьте на сообщение с запросом причины (это нужно для связки).", parse_mode="Markdown")
        return

    if message.from_user.id != data.get('admin_id'):
        await message.answer("⛔ Вы не тот администратор, который инициировал отклонение.", parse_mode="Markdown")
        return

    reason = message.text.strip()
    if not reason:
        await message.answer("⚠️ Причина не может быть пустой. Напишите текст.", parse_mode="Markdown")
        return

    user_id = data['user_id']
    original_text = data['original_text']
    original_msg_id = data['original_message_id']
    admin_mention = data['admin_mention']

    new_text = original_text + f"\n\n❌ **Отклонено** администратором {admin_mention}\n**Причина:** {reason}"
    try:
        await bot.edit_message_text(new_text, chat_id=GROUP_CHAT_ID, message_id=original_msg_id, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка редактирования: {e}", parse_mode="Markdown")
        return

    await bot.send_message(user_id, f"❌ Ваша анкета **отклонена**.\nПричина: {reason}\nНу надо же. Я почти впечатлён. Почти. Знаешь, получить отказ по такой причине - это надо было постараться. В плохом смысле. Мне за тебя даже чуть-чуть стыдно, а я, поверь, существо практически бесстыдное. Ступай, подумай над собой. Если одумаешься и переделаешь - так уж и быть, посмотрю ещё раз. Но учти: второго такого позора я не прощу. Не позорься.", parse_mode="Markdown")

    try:
        await bot.delete_message(GROUP_CHAT_ID, request_msg_id)
    except:
        pass

    await state.clear()
    await message.answer("✅ Причина принята, анкета отклонена.", parse_mode="Markdown")

# ---------- ЗАПУСК ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
