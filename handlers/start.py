from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states import Choice, StudentForm, StaffForm, STUDENT_PREV, STAFF_PREV, STUDENT_QUESTIONS, STAFF_QUESTIONS
from keyboards import get_main_menu_keyboard, get_race_keyboard_with_back, get_back_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    intro = (
        "А, это ты. Ну давай, заходи, раз уж пришёл. Только учти: я сейчас в процессе важного ничегонеделания, так что говори быстро.\n"
        "Хочешь анкету создать? Похвально. Даже не знаю, что более жалко — твоя уверенность, что ты достоин здесь учиться, или тот факт, что я действительно потрачу на тебя время.\n"
        "Впрочем, у меня сегодня хорошее настроение — я полюбовался на себя в зеркало, а это всегда поднимает дух.\n"
        "Так что давай, смертный, ученик ты или персонал?"
    )
    await message.answer(intro, reply_markup=get_main_menu_keyboard())
    await state.set_state(Choice.waiting)

@router.callback_query(StateFilter(Choice.waiting), F.data.startswith("choice_"))
async def process_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == "choice_student":
        await callback.message.answer(
            "<b>Для ученика</b>\n\n"
            "Назовись. Только без титулов, умоляю. «Лорд Тьмы», «Повелительница Звёзд» — я этого не вынесу. "
            "У меня у самого их десяток, и я не разбрасываюсь. Просто имя. Мне, в общем-то, всё равно, но формальности требуют.",
            parse_mode="HTML"
        )
        await state.set_state(StudentForm.name)
    elif callback.data == "choice_staff":
        await callback.message.answer(
            "<b>Для персонала</b>\n\n"
            "Решил устроиться ко мне на работу? Смело. Или глупо. Я пока не определился. Знаешь, что я люблю больше, чем хаос? Только себя. "
            "Так что, если ты не готов мириться с моим величием, капризами и тем, что я временами вообще забываю о существовании персонала, — лучше уйди сейчас. Я даже не замечу.\n\n"
            "<b>Должность</b>\n"
            "Кем хочешь быть? Преподавателем? Целителем? Смотрителем леса? Выбирай, мне без разницы. Только учти: если облажаешься, я разочаруюсь. "
            "А когда я разочаровываюсь, я начинаю искать развлечений. Обычно за чужой счёт. Ну так что, не передумал? Нет? Ну смотри.",
            parse_mode="HTML"
        )
        await state.set_state(StaffForm.position)
    await callback.answer()

# =====================================================
# ОБРАБОТЧИК КНОПКИ "НАЗАД" (без отдельной функции)
# =====================================================
@router.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        await callback.answer("Нечего отменять")
        return

    # Проверяем, является ли состояние частью ученической анкеты
    if current_state in STUDENT_PREV:
        prev = STUDENT_PREV[current_state]
        question = STUDENT_QUESTIONS.get(prev, "Вернулись к предыдущему шагу.")
        await state.set_state(prev)
        await callback.message.delete()

        # Определяем клавиатуру для предыдущего состояния
        if prev == StudentForm.race:
            keyboard = get_race_keyboard_with_back()
        elif prev == StudentForm.name:
            keyboard = None  # на первом шаге кнопка "Назад" не нужна
        else:
            keyboard = get_back_keyboard()

        await callback.bot.send_message(
            callback.message.chat.id,
            question,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()

    # Проверяем, является ли состояние частью анкеты персонала
    elif current_state in STAFF_PREV:
        prev = STAFF_PREV[current_state]
        question = STAFF_QUESTIONS.get(prev, "Вернулись к предыдущему шагу.")
        await state.set_state(prev)
        await callback.message.delete()

        if prev == StaffForm.race:
            keyboard = get_race_keyboard_with_back()
        elif prev == StaffForm.position:
            keyboard = None  # первый шаг персонала
        else:
            keyboard = get_back_keyboard()

        await callback.bot.send_message(
            callback.message.chat.id,
            question,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()

    else:
        await callback.answer("Нельзя вернуться назад", show_alert=True)
