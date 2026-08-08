import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from ..config import GROUP_CHAT_ID
from ..states import StudentForm
from ..keyboards import get_race_keyboard, RACE_MAP, get_approve_reject_keyboard
from ..utils import esc

router = Router()
logger = logging.getLogger(__name__)


@router.message(StateFilter(StudentForm.name))
async def student_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "<b>Раса</b>\nИ кто ты у нас по природе? Человек, эльф, недодемон? Пока ты будешь перечислять, я, пожалуй, пересчитаю свои рога. "
        "О, у меня их два. Прекрасных. Тёмно-синих. А у тебя? Ну давай, не томи, кто ты там по расовой принадлежности.",
        reply_markup=get_race_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.race)


@router.callback_query(StateFilter(StudentForm.race), F.data.startswith("race_"))
async def student_race(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_", 1)[1]
    if key not in RACE_MAP:
        await callback.answer("Выберите расу из предложенных", show_alert=True)
        return
    race_name = RACE_MAP[key]
    await state.update_data(race=race_name)
    await callback.message.delete()
    await callback.message.answer(f"Выбрана раса: {esc(race_name)}")
    await callback.message.answer(
        "<b>Возраст</b>\nНе подскажешь возраст? Мой я давно не считаю, потому что цифры не способны вместить моё величие. "
        "А вот твой — назови. Сверься с регламентом. Если тебе под сотню, а ты прёшься на первый курс, я даже не разозлюсь — мне просто станет ещё скучнее, чем было.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.age)
    await callback.answer()


@router.message(StateFilter(StudentForm.age))
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
        "<b>Пол / Рост / Вес</b>\nПол, рост, вес. Три скучных слова. Если у тебя есть что-то интересное в пропорциях — я, может, и подниму бровь. Но вряд ли.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.gender_height_weight)


@router.message(StateFilter(StudentForm.gender_height_weight))
async def student_gender_height_weight(message: types.Message, state: FSMContext):
    await state.update_data(gender_height_weight=message.text)
    await message.answer(
        "<b>Характер</b>\nОпиши свой характер. Мне, честно говоря, глубоко безразлично, что ты там о себе думаешь, но правила есть правила. "
        "Четыре строки. «Добрый и отзывчивый» — и я зевну так, что ты испугаешься. Лучше уж пиши, что ты скрытый маньяк. Хоть поржу.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.character)


@router.message(StateFilter(StudentForm.character))
async def student_character(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 4:
        await message.answer(f"⚠️ Характер должен содержать минимум 4 строки. Сейчас {len(lines)}. Напишите подробнее:")
        return
    await state.update_data(character=message.text)
    await message.answer(
        "<b>Способности</b>\nНа что ты способен? Не надейся меня впечатлить — я видел магов, которые создавали миры. Я сам создавал миры. "
        "Но давай, расскажи, как ты умеешь зажигать свечку пальцем. Только всесилие, бессмертие и прочее — ЗАПРЕЩЕНО. Это моё. "
        "Я и так слишком щедр, позволяя тебе дышать одним воздухом со мной.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.abilities)


@router.message(StateFilter(StudentForm.abilities))
async def student_abilities(message: types.Message, state: FSMContext):
    await state.update_data(abilities=message.text)
    await message.answer(
        "<b>Слабости и страхи</b>\nЧего ты боишься? Меня, надеюсь, уже боишься. Если нет — ничего, это приходит со временем. "
        "Слабости способностей тоже пиши. Мне это пригодится, чтобы… ну, просто чтобы было. Я коллекционирую чужие уязвимости. Такое вот хобби у бессмертного красавца.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.weaknesses)


@router.message(StateFilter(StudentForm.weaknesses))
async def student_weaknesses(message: types.Message, state: FSMContext):
    await state.update_data(weaknesses=message.text)
    await message.answer(
        "<b>Факты</b>\nРазвлеки меня. Любимая еда, хобби, шрамы. Только не вздумай писать «люблю закаты и прогулки» — я тут же потеряю к тебе остатки интереса. "
        "А их и так немного. Я пока подумаю, не добавить ли ещё один мир. Или леденцов. Я люблю леденцы.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.facts)


@router.message(StateFilter(StudentForm.facts))
async def student_facts(message: types.Message, state: FSMContext):
    await state.update_data(facts=message.text)
    await message.answer(
        "<b>Внешность</b>\nОпиши, как выглядишь. Если есть картинка — две строки. Я сравню со своим отражением. Спойлер: ты проиграешь. "
        "Мои рога, кстати, светятся в темноте. Бесполезно, но красиво. А ты? Ладно, пиши уже, не заставляй меня ждать. Ждать я не люблю, хотя ты того не стоишь.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.appearance)


@router.message(StateFilter(StudentForm.appearance))
async def student_appearance(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 2:
        await message.answer("⚠️ Внешность должна содержать минимум 2 строки. Опишите подробнее.")
        return
    await state.update_data(appearance=message.text)
    await message.answer(
        "<b>Биография</b>\nОт восьми строк. Откуда ты, кто родители, как ты вообще дожил до этого момента. Мне это нужно не для того, чтобы проникнуться твоей драмой — упаси боже, — "
        "а чтобы понять, сколько ты протянешь в моей Академии. Если биография скучная — приукрась. Я разрешаю. Я сегодня щедрый. Зеркало сказало, что я неотразим, и я ему верю.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.biography)


@router.message(StateFilter(StudentForm.biography))
async def student_biography(message: types.Message, state: FSMContext):
    lines = message.text.splitlines() if message.text else []
    if len(lines) < 8:
        await message.answer(f"⚠️ Биография должна содержать минимум 8 строк. Сейчас {len(lines)}. Напишите подробнее:")
        return
    await state.update_data(biography=message.text)
    await message.answer(
        "<b>Курс</b>\nНа какой курс собрался? Сверься с регламентом, я не буду повторять дважды. Если перепутаешь — останешься на первом курсе навсегда. "
        "Мне-то что, я всё равно буду тут, вечный и прекрасный, а вот ты состаришься за партой. Забавно? Возможно.",
        parse_mode="HTML"
    )
    await state.set_state(StudentForm.course)


@router.message(StateFilter(StudentForm.course))
async def student_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    data = await state.get_data()
    await state.clear()

    required_keys = ['name', 'race', 'age', 'gender_height_weight', 'character',
                     'abilities', 'weaknesses', 'facts', 'appearance', 'biography', 'course']
    missing = [k for k in required_keys if k not in data]
    if missing:
        await message.answer(f"⚠️ Ошибка: не хватает данных: {', '.join(missing)}. Заполните анкету заново.")
        return

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

    keyboard = get_approve_reject_keyboard(message.from_user.id)

    try:
        await message.bot.send_message(GROUP_CHAT_ID, text, reply_markup=keyboard, parse_mode="HTML")
        logger.info(f"Анкета ученика от {message.from_user.id} отправлена в группу {GROUP_CHAT_ID}")
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
