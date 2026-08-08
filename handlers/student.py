import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import GROUP_CHAT_ID
from states import StudentForm
from keyboards import get_race_keyboard_with_back, RACE_MAP, get_approve_reject_keyboard, get_back_keyboard
from utils import esc, split_text

router = Router()
logger = logging.getLogger(__name__)


# ---------- Вспомогательная функция: удаляет предыдущее сообщение бота и отправляет новое ----------
async def cleanup_and_send(
    message: types.Message,
    state: FSMContext,
    text: str,
    reply_markup=None,
    parse_mode: str = "HTML"
):
    """
    Удаляет предыдущее сообщение бота (если есть) и отправляет новое.
    Сохраняет ID нового сообщения в состоянии.
    """
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


# ---------- Шаг 1: Имя ----------
@router.message(StateFilter(StudentForm.name))
async def student_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Раса</b>\nИ кто ты у нас по природе? Человек, эльф, недодемон? Пока ты будешь перечислять, я, пожалуй, пересчитаю свои рога. "
        "О, у меня их два. Прекрасных. Тёмно-синих. А у тебя? Ну давай, не томи, кто ты там по расовой принадлежности.",
        reply_markup=get_race_keyboard_with_back()
    )
    await state.set_state(StudentForm.race)


# ---------- Шаг 2: Раса (callback) ----------
@router.callback_query(StateFilter(StudentForm.race), F.data.startswith("race_"))
async def student_race(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_", 1)[1]
    if key not in RACE_MAP:
        await callback.answer("Выберите расу из предложенных", show_alert=True)
        return

    race_name = RACE_MAP[key]
    await state.update_data(race=race_name)

    # Удаляем сообщение с кнопками выбора расы
    await callback.message.delete()

    # Удаляем предыдущее сообщение бота (вопрос о расе)
    data = await state.get_data()
    last_id = data.get('last_bot_message_id')
    if last_id:
        try:
            await callback.bot.delete_message(callback.message.chat.id, last_id)
        except Exception:
            pass

    # Отправляем новое сообщение с вопросом о возрасте
    sent = await callback.message.answer(
        "<b>Возраст</b>\n\nНе подскажешь возраст? Мой я давно не считаю, потому что цифры не способны вместить моё величие. "
        "А вот твой — назови. Сверься с регламентом. Если тебе под сотню, а ты прёшься на первый курс, я даже не разозлюсь — мне просто станет ещё скучнее, чем было.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(last_bot_message_id=sent.message_id)
    await state.set_state(StudentForm.age)
    await callback.answer()


# ---------- Шаг 3: Возраст ----------
@router.message(StateFilter(StudentForm.age))
async def student_age(message: types.Message, state: FSMContext):
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
        "<b>Пол / Рост / Вес</b>\n\nПол, рост, вес. Три скучных слова. Если у тебя есть что-то интересное в пропорциях — я, может, и подниму бровь. Но вряд ли.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.gender_height_weight)


# ---------- Шаг 4: Пол/Рост/Вес ----------
@router.message(StateFilter(StudentForm.gender_height_weight))
async def student_gender_height_weight(message: types.Message, state: FSMContext):
    await state.update_data(gender_height_weight=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Характер</b>\n\nОпиши свой характер. Мне, честно говоря, глубоко безразлично, что ты там о себе думаешь, но правила есть правила. "
        "Минимум 200 символов. «Добрый и отзывчивый» — и я зевну так, что ты испугаешься. Лучше уж пиши, что ты скрытый маньяк. Хоть поржу.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.character)


# ---------- Шаг 5: Характер (проверка длины) ----------
@router.message(StateFilter(StudentForm.character))
async def student_character(message: types.Message, state: FSMContext):
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
        "<b>Способности</b>\n\nНа что ты способен? Не надейся меня впечатлить — я видел магов, которые создавали миры. Я сам создавал миры. "
        "Но давай, расскажи, как ты умеешь зажигать свечку пальцем. Только всесилие, бессмертие и прочее — ЗАПРЕЩЕНО. Это моё. "
        "Я и так слишком щедр, позволяя тебе дышать одним воздухом со мной.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.abilities)


# ---------- Шаг 6: Способности ----------
@router.message(StateFilter(StudentForm.abilities))
async def student_abilities(message: types.Message, state: FSMContext):
    await state.update_data(abilities=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Слабости и страхи</b>\n\nЧего ты боишься? Меня, надеюсь, уже боишься. Если нет — ничего, это приходит со временем. "
        "Слабости способностей тоже пиши. Мне это пригодится, чтобы… ну, просто чтобы было. Я коллекционирую чужие уязвимости. Такое вот хобби у бессмертного красавца.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.weaknesses)


# ---------- Шаг 7: Слабости ----------
@router.message(StateFilter(StudentForm.weaknesses))
async def student_weaknesses(message: types.Message, state: FSMContext):
    await state.update_data(weaknesses=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Факты</b>\n\nРазвлеки меня. Любимая еда, хобби, шрамы. Только не вздумай писать «люблю закаты и прогулки» — я тут же потеряю к тебе остатки интереса. "
        "А их и так немного. Я пока подумаю, не добавить ли ещё один мир. Или леденцов. Я люблю леденцы.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.facts)


# ---------- Шаг 8: Факты ----------
@router.message(StateFilter(StudentForm.facts))
async def student_facts(message: types.Message, state: FSMContext):
    await state.update_data(facts=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Внешность</b>\n\nОпиши, как выглядишь. Если есть картинка — две строки. Я сравню со своим отражением. Спойлер: ты проиграешь. "
        "Мои рога, кстати, светятся в темноте. Бесполезно, но красиво. А ты? Ладно, пиши уже, не заставляй меня ждать. Ждать я не люблю, хотя ты того не стоишь.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.appearance)


# ---------- Шаг 9: Внешность ----------
@router.message(StateFilter(StudentForm.appearance))
async def student_appearance(message: types.Message, state: FSMContext):
    await state.update_data(appearance=message.text)
    await cleanup_and_send(
        message,
        state,
        "<b>Биография</b>\n\nОткуда ты, кто родители, как ты вообще дожил до этого момента. Мне это нужно не для того, чтобы проникнуться твоей драмой — упаси боже, — "
        "а чтобы понять, сколько ты протянешь в моей Академии. Если биография скучная — приукрась. Я разрешаю. Я сегодня щедрый. Зеркало сказало, что я неотразим, и я ему верю.\n\n"
        "<b>Минимум 200 символов.</b>",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.biography)


# ---------- Шаг 10: Биография (проверка длины) ----------
@router.message(StateFilter(StudentForm.biography))
async def student_biography(message: types.Message, state: FSMContext):
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
    await cleanup_and_send(
        message,
        state,
        "<b>Курс</b>\n\nНа какой курс собрался из семи? Сверься с регламентом, я не буду повторять дважды. Если перепутаешь — останешься на первом курсе навсегда. "
        "Мне-то что, я всё равно буду тут, вечный и прекрасный, а вот ты состаришься за партой. Забавно? Возможно.",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(StudentForm.course)


# ---------- Шаг 11: Курс (финал) ----------
@router.message(StateFilter(StudentForm.course))
async def student_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    data = await state.get_data()

    # Сохраняем ID последнего сообщения перед очисткой состояния
    last_id = data.get('last_bot_message_id')
    await state.clear()  # очищаем состояние

    # Удаляем последнее сообщение бота (вопрос курса)
    if last_id:
        try:
            await message.bot.delete_message(message.chat.id, last_id)
        except Exception:
            pass

    # Проверка наличия всех ключей
    required_keys = ['name', 'race', 'age', 'gender_height_weight', 'character',
                     'abilities', 'weaknesses', 'facts', 'appearance', 'biography', 'course']
    missing = [k for k in required_keys if k not in data]
    if missing:
        await message.answer(f"⚠️ Ошибка: не хватает данных: {', '.join(missing)}. Заполните анкету заново.")
        return

    # Формируем полный текст анкеты
    full_text = (
        "📄 <b>Новая анкета ученика</b>\n\n"
        f"<b>Имя и фамилия:</b> {esc(data['name'])}\n"
        f"<b>Раса:</b> {esc(data['race'])}\n"
        f"<b>Возраст:</b> {esc(data['age'])}\n"
        f"<b>Пол/Рост/Вес:</b> {esc(data['gender_height_weight'])}\n"
        f"<b>Характер:</b> {esc(data['character'])}\n"
        f"<b>Способности:</b> {esc(data['abilities'])}\n"
        f"<b>Слабости и страхи:</b> {esc(data['weaknesses'])}\n"
        f"<b>Факты:</b> {esc(data['facts'])}\n"
        f"<b>Внешность:</b> {esc(data['appearance'])}\n"
        f"<b>Биография:</b> {esc(data['biography'])}\n"
        f"<b>Курс:</b> {esc(data['course'])}\n"
    )

    keyboard = get_approve_reject_keyboard(message.from_user.id)
    parts = split_text(full_text)

    try:
        # Отправляем первую часть с клавиатурой
        await message.bot.send_message(
            GROUP_CHAT_ID,
            parts[0],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        # Остальные части без клавиатуры
        for part in parts[1:]:
            await message.bot.send_message(
                GROUP_CHAT_ID,
                part,
                parse_mode="HTML"
            )
        logger.info(f"Анкета ученика от {message.from_user.id} отправлена в группу (частей: {len(parts)})")
    except Exception as e:
        logger.error(f"Ошибка отправки анкеты ученика в группу: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при отправке анкеты администраторам. Пожалуйста, попробуйте позже.",
            parse_mode="HTML"
        )
        return

    await message.answer(
        "✅ Анкета отправлена на проверку.\n\n"
        "<b>На правки — три дня.</b> Не успеешь — твои проблемы. Мне не к спеху. Я могу ждать вечность. Но тебе-то, смертный, вечность не светит.",
        parse_mode="HTML"
    )
