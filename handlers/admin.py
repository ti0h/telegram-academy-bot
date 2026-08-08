import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import GROUP_CHAT_ID
from states import RejectReason
from utils import esc

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith(("approve_", "reject_")))
async def handle_approve_reject(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 1)
    if len(parts) != 2 or not parts[1].isdigit():
        await callback.answer()
        return

    action, user_id_str = parts
    user_id = int(user_id_str)

    try:
        member = await callback.bot.get_chat_member(GROUP_CHAT_ID, callback.from_user.id)
    except Exception as e:
        logger.warning("Не удалось проверить права %s: %s", callback.from_user.id, e)
        await callback.answer("⚠️ Не удалось проверить ваши права.", show_alert=True)
        return

    if member.status not in ("administrator", "creator"):
        await callback.answer("⛔ Только администраторы группы могут принимать решения.", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)

    admin = callback.from_user
    admin_mention = f"@{admin.username}" if admin.username else f"<a href='tg://user?id={admin.id}'>{esc(admin.first_name)}</a>"

    if action == "approve":
        try:
            await callback.bot.send_message(
                GROUP_CHAT_ID,
                f"✅ <b>Анкета одобрена</b> администратором {admin_mention}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения об одобрении: {e}")
            await callback.answer("⚠️ Ошибка отправки сообщения", show_alert=True)
            return

        try:
            await callback.bot.send_message(
                user_id,
                "<i>— Что ж... неожиданно достойная работа. Поздравляю. Теперь ты официально стал частью Академии Пафент. Надеюсь, твоё пребывание здесь окажется долгим. Хотя... это уже зависит исключительно от тебя.</i>\n\n https://t.me/+Iji2mDCmE24yMTNi",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning("Не удалось уведомить пользователя %s: %s", user_id, e)

        await callback.answer("Анкета принята", show_alert=False)

    elif action == "reject":
        await state.update_data(
            user_id=user_id,
            original_message_id=callback.message.message_id,
            admin_mention=admin_mention,
            admin_id=admin.id
        )
        try:
            request_msg = await callback.bot.send_message(
                GROUP_CHAT_ID,
                f"👤 {admin_mention}, напишите <b>причину отклонения</b> в ответ на это сообщение.",
                parse_mode="HTML"
            )
            await state.update_data(request_message_id=request_msg.message_id)
            await state.set_state(RejectReason.waiting_for_reason)
            await callback.answer("Напишите причину в группе, ответив на запрос.", show_alert=False)
        except Exception as e:
            logger.error(f"Ошибка при запросе причины отклонения: {e}")
            await callback.answer("⚠️ Ошибка при запросе причины", show_alert=True)

@router.message(StateFilter(RejectReason.waiting_for_reason))
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
    admin_mention = data['admin_mention']

    try:
        await message.bot.send_message(
            GROUP_CHAT_ID,
            f"❌ <b>Анкета отклонена</b> администратором {admin_mention}\n<b>Причина:</b> {esc(reason)}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения об отклонении: {e}")
        await message.answer(f"⚠️ Ошибка отправки: {esc(e)}")
        return

    try:
        await message.bot.send_message(
            user_id,
            f"— Хм... Нет. Пока нет. Боюсь, этого недостаточно. В анкете обнаружились ошибки, и, прежде чем двери Академии откроются для тебя, их придётся исправить. Ознакомься с замечаниями ниже, внеси изменения и отправь анкету повторно. На этот раз постарайся быть внимательнее.\n\nЗамечания: {esc(reason)}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning("Не удалось уведомить пользователя %s: %s", user_id, e)

    try:
        await message.bot.delete_message(GROUP_CHAT_ID, request_msg_id)
    except Exception:
        pass

    await state.clear()
    await message.answer("✅ Причина принята, анкета отклонена.")
