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
        sent = await callback.message.answer(
            "<b>Для ученика</b>\n\n"
            "Назовись. Только без титулов, умоляю. «Лорд Тьмы», «Повелительница Звёзд» — я этого не вынесу. "
            "У меня у самого их десяток, и я не разбрасываюсь. Просто имя. Мне, в общем-то, всё равно, но формальности требуют.",
            parse_mode="HTML"
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        await state.set_state(StudentForm.name)
    elif callback.data == "choice_staff":
        # Теперь просим ввести должность вручную
        sent = await callback.message.answer(
            "<b>Для персонала</b>\n\n"
            "Напиши свою должность (например, «Учитель магии» или «Директор»).\n"
            "Список с доступными должностями есть в регламенте академии, выбирать только оттуда, если вы хотите дополнительную роль обратитесь к администрации.",
            parse_mode="HTML"
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        await state.set_state(StaffForm.position)   # теперь это текстовое состояние
    await callback.answer()

# Обработчик кнопки "Назад" (без изменений, но нужно адаптировать для StaffForm.position)
@router.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        await callback.answer("Нечего отменять")
        return

    await callback.message.delete()

    if current_state in STUDENT_PREV:
        prev = STUDENT_PREV[current_state]
        question = STUDENT_QUESTIONS.get(prev, "Вернулись к предыдущему шагу.")
        await state.set_state(prev)
        if prev == StudentForm.race:
            keyboard = get_race_keyboard_with_back()
        elif prev == StudentForm.name:
            keyboard = None
        else:
            keyboard = get_back_keyboard()

        data = await state.get_data()
        last_id = data.get('last_bot_message_id')
        if last_id:
            try:
                await callback.bot.delete_message(callback.message.chat.id, last_id)
            except Exception:
                pass

        sent = await callback.bot.send_message(
            callback.message.chat.id,
            question,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        await callback.answer()

    elif current_state in STAFF_PREV:
        prev = STAFF_PREV[current_state]
        question = STAFF_QUESTIONS.get(prev, "Вернулись к предыдущему шагу.")
        await state.set_state(prev)
        if prev == StaffForm.race:
            keyboard = get_race_keyboard_with_back()
        elif prev == StaffForm.position:
            keyboard = None   # первый шаг – без кнопки назад
        else:
            keyboard = get_back_keyboard()

        data = await state.get_data()
        last_id = data.get('last_bot_message_id')
        if last_id:
            try:
                await callback.bot.delete_message(callback.message.chat.id, last_id)
            except Exception:
                pass

        sent = await callback.bot.send_message(
            callback.message.chat.id,
            question,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        await callback.answer()

    else:
        await callback.answer("Нельзя вернуться назад", show_alert=True)
