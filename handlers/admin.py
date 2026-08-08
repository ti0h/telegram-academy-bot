import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import GROUP_CHAT_ID          # абсолютный импорт
from states import RejectReason           # абсолютный импорт
from utils import esc                     # абсолютный импорт

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
        new_text = callback.message.text + f"\n\n✅ <b>Одобрено</b> администратором {admin_mention}"
        try:
            await callback.bot.edit_message_text(
                new_text,
                chat_id=GROUP_CHAT_ID,
                message_id=callback.message.message_id,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ошибка редактирования при одобрении: {e}")
            await callback.answer("⚠️ Ошибка редактирования", show_alert=True)
            return

        try:
            await callback.bot.send_message(
                user_id,
                "🎉 Ваша анкета <b>одобрена</b>! Добро пожаловать.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning("Не удалось уведомить пользователя %s: %s", user_id, e)

        await callback.answer("Анкета принята", show_alert=False)

    elif action == "reject":
        await state.update_data(
            user_id=user_id,
            original_message_id=callback.message.message_id,
            original_text=callback.message.text,
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
    original_text = data['original_text']
    original_msg_id = data['original_message_id']
    admin_mention = data['admin_mention']

    new_text = original_text + f"\n\n❌ <b>Отклонено</b> администратором {admin_mention}\n<b>Причина:</b> {esc(reason)}"
    try:
        await message.bot.edit_message_text(
            new_text,
            chat_id=GROUP_CHAT_ID,
            message_id=original_msg_id,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка редактирования при отклонении: {e}")
        await message.answer(f"⚠️ Ошибка редактирования: {esc(e)}")
        return

    try:
        await message.bot.send_message(
            user_id,
            f"❌ Ваша анкета <b>отклонена</b>.\nПричина: {esc(reason)}",
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
