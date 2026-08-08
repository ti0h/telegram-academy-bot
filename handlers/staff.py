import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import GROUP_CHAT_ID
from states import StaffForm
from keyboards import get_race_keyboard_with_back, RACE_MAP, get_approve_reject_keyboard, get_back_keyboard
from utils import esc, split_text

router = Router()
logger = logging.getLogger(__name__)

# Вспомогательная функция для удаления предыдущего сообщения
async def cleanup_and_send(message: types.Message, state: FSMContext, text: str, reply_markup=None, parse_mode="HTML"):
    data = await state.get_data()
    last_id = data.get('last_bot_message_id')
    if last_id:
        try:
            await message.bot.delete_message(message.chat.id, last_id)
        except Exception:
            pass
    sent = await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
    await state.update_data(last_bot_message_id=sent.message_id)
    return sent

# ---------- Шаг 1: Ввод должности (текст) ----------
@router.message(StateFilter(StaffForm.position))
async def staff_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Имя / Фамилия</b>\nПредставься. Только быстро. Если имя дурацкое, я всё равно забуду его через пять минут и буду звать тебя «эй, ты». "
        "Я так делаю со всеми, это не личное. Просто вы все для меня на одно лицо.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.name)

# ---------- Шаг 2: Имя ----------
@router.message(StateFilter(StaffForm.name))
async def staff_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Возраст</b>\nСколько тебе лет? Мне не важно, но анкета требует. Я в это время полирую рога. Они у меня, знаешь ли, требуют ухода. "
        "Не то что твоя биография. Кстати, возраст. Жду.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.age)

# ---------- Шаг 3: Возраст ----------
@router.message(StateFilter(StaffForm.age))
async def staff_age(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await cleanup_and_send(
            message,
            state,
            "⚠️ Возраст должен быть числом. Попробуйте снова.",
            reply_markup=get_back_keyboard()
        )
        return
    age = int(message.text)
    if age < 1:
        await cleanup_and_send(
            message,
            state,
            "⚠️ Возраст должен быть положительным числом. Введите корректно.",
            reply_markup=get_back_keyboard()
        )
        return
    await state.update_data(age=age)
    await cleanup_and_send(
        message,
        state,
        "<b>Раса</b>\nИ кто ты у нас по природе? Человек, эльф, недодемон? Пока ты будешь перечислять, я, пожалуй, пересчитаю свои рога. "
        "О, у меня их два. Прекрасных. Тёмно-синих. А у тебя? Ну давай, не томи, кто ты там по расовой принадлежности.",
        reply_markup=get_race_keyboard_with_back()
    )
    await state.set_state(StaffForm.race)

# ---------- Шаг 4: Раса (callback) ----------
@router.callback_query(StateFilter(StaffForm.race), F.data.startswith("race_"))
async def staff_race(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_", 1)[1]
    if key not in RACE_MAP:
        await callback.answer("Выберите расу из предложенных", show_alert=True)
        return
    race_name = RACE_MAP[key]
    await state.update_data(race=race_name)
    await callback.message.delete()

    data_state = await state.get_data()
    last_id = data_state.get('last_bot_message_id')
    if last_id:
        try:
            await callback.bot.delete_message(callback.message.chat.id, last_id)
        except Exception:
            pass

    sent = await callback.message.answer(f"Выбрана раса: {esc(race_name)}")
    await state.update_data(last_bot_message_id=sent.message_id)

    sent2 = await callback.message.answer(
        "<b>Пол / Рост / Вес</b>\nКто ты? пол, рост, вес. Кратко. Пока ты пишешь, я прикидываю, достаточно ли хорош сегодня мой профиль. "
        "Кажется, да. Особенно правый рог. Левый тоже ничего. Ладно, я отвлёкся. Ты всё ещё тут? Пиши давай.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(last_bot_message_id=sent2.message_id)
    await state.set_state(StaffForm.gender_height_weight)
    await callback.answer()

# ---------- Шаг 5: Пол/Рост/Вес ----------
@router.message(StateFilter(StaffForm.gender_height_weight))
async def staff_gender_height_weight(message: types.Message, state: FSMContext):
    await state.update_data(gender_height_weight=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Характер</b>\nРасскажи, с кем мне предстоит делить воздух. Я надеюсь, ты не зануда. Я ненавижу зануд. Если ты садист — отлично, но помни: главный садист здесь я. "
        "И я ревнив. Не посягай на моё место, и мы поладим. Наверное. Не уверен. Мне вообще всё равно.\n\n<b>Минимум 200 символов.</b>",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.character)

# ---------- Шаг 6: Характер ----------
@router.message(StateFilter(StaffForm.character))
async def staff_character(message: types.Message, state: FSMContext):
    text = message.text or ""
    if len(text) < 200:
        await cleanup_and_send(
            message,
            state,
            f"⚠️ Характер должен содержать минимум 200 символов. Сейчас {len(text)}. Напишите подробнее.",
            reply_markup=get_back_keyboard()
        )
        return
    await state.update_data(character=text)
    await cleanup_and_send(
        message,
        state,
        "<b>Способности, магия и магическое направление</b>\nЧто ты умеешь? Кроме как вызывать у меня лёгкую скуку. "
        "Всесилие, бессмертие, антимагия — моё. Даже не дыши в их сторону. Если твои способности — что-то вроде «хорошо готовлю зелья», то хотя бы готовь их с фантазией. "
        "Я люблю, когда красиво. Себя я люблю больше, но и красоту ценю.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.abilities)

# ---------- Шаг 7: Способности ----------
@router.message(StateFilter(StaffForm.abilities))
async def staff_abilities(message: types.Message, state: FSMContext):
    await state.update_data(abilities=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Слабости, страхи</b>\nВсё выкладывай. Я, как истинный коллекционер, бережно храню чужие уязвимости в своей голове. "
        "Если ты вампир и боишься солнечного света — не переживай, в моей Академии всегда сумрачно. Я тоже люблю сумрак. Он мне идёт.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.weaknesses)

# ---------- Шаг 8: Слабости ----------
@router.message(StateFilter(StaffForm.weaknesses))
async def staff_weaknesses(message: types.Message, state: FSMContext):
    await state.update_data(weaknesses=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Факты</b>\nПривычки, хобби, бывшие работы. У меня, например, есть хобби — создавать миры и забывать о них. Ещё я коллекционирую проклятия. "
        "А ты? Только не говори, что вышиваешь крестиком. Я же засмею. И буду смеяться долго. У меня смех красивый, но обидный.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.facts)

# ---------- Шаг 9: Факты ----------
@router.message(StateFilter(StaffForm.facts))
async def staff_facts(message: types.Message, state: FSMContext):
    await state.update_data(facts=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Внешность</b>\nКартинка или описание. Только не пытайся выглядеть лучше меня. Это бессмысленно. Я — произведение искусства, а ты — так, эскиз. "
        "Одежду тоже опиши. Если ты одет как пугало, я переодену тебя сам. Не из заботы — просто ты будешь портить мне вид.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.appearance)

# ---------- Шаг 10: Внешность ----------
@router.message(StateFilter(StaffForm.appearance))
async def staff_appearance(message: types.Message, state: FSMContext):
    await state.update_data(appearance=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Биография</b>\nГде учился, кого предавал, почему решил, что достоин служить мне. Чтобы стать преподавателем, сдавал экзамен. "
        "Я не принимаю экзамены, я выше этого. Но биографию прочту. Если она скучная — я добавлю в неё красок. В основном красных. Люблю красный.\n\n"
        "<b>Минимум 200 символов.</b>",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StaffForm.biography)

# ---------- Шаг 11: Биография (проверка длины) ----------
@router.message(StateFilter(StaffForm.biography))
async def staff_biography(message: types.Message, state: FSMContext):
    text = message.text or ""
    if len(text) < 200:
        await cleanup_and_send(
            message,
            state,
            f"⚠️ Биография должна содержать минимум 200 символов. Сейчас {len(text)}. Напишите подробнее.",
            reply_markup=get_back_keyboard()
        )
        return
    await state.update_data(biography=text)
    data = await state.get_data()
    last_id = data.get('last_bot_message_id')
    await state.clear()

    if last_id:
        try:
            await message.bot.delete_message(message.chat.id, last_id)
        except Exception:
            pass

    required_keys = ['position', 'name', 'age', 'race', 'gender_height_weight',
                     'character', 'abilities', 'weaknesses', 'facts', 'appearance', 'biography']
    missing = [k for k in required_keys if k not in data]
    if missing:
        await message.answer(f"⚠️ Ошибка: не хватает данных: {', '.join(missing)}. Заполните анкету заново.")
        return

    full_text = (
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

    keyboard = get_approve_reject_keyboard(message.from_user.id)
    parts = split_text(full_text)

    try:
        await message.bot.send_message(
            GROUP_CHAT_ID,
            parts[0],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        for part in parts[1:]:
            await message.bot.send_message(
                GROUP_CHAT_ID,
                part,
                parse_mode="HTML"
            )
        logger.info(f"Анкета персонала от {message.from_user.id} отправлена в группу (частей: {len(parts)})")
    except Exception as e:
        logger.error(f"Ошибка отправки анкеты персонала в группу: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при отправке анкеты администраторам. Пожалуйста, попробуйте позже.",
            parse_mode="HTML"
        )
        return

    await message.answer(
        "✅ Анкета отправлена на проверку.\n\n"
        "<b>Бронь — неделя. Анкету править — три дня.</b> Если не успеешь… да плевать, если честно. Найдёшь другую работу. Или не найдёшь. "
        "Я в любом случае останусь тут — великий, прекрасный и абсолютно довольный собой.",
        parse_mode="HTML"
    )
