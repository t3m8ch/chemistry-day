from aiogram import Router, types, F

from .constants import SEND_INVITE_PREFIX

router = Router()


@router.inline_query(F.query.startswith(SEND_INVITE_PREFIX))
async def on_send_invite_inline_query(iq: types.InlineQuery, bot_username: str):
    base58_invite_id = iq.query[len(SEND_INVITE_PREFIX):]
    url = f"https://t.me/{bot_username}?start=accept_invite_{base58_invite_id}"

    await iq.answer([types.InlineQueryResultArticle(
        id=base58_invite_id,
        title="Отправить приглашение",
        input_message_content=types.InputTextMessageContent(
            message_text="🎎 Вам пришло приглашение в команду",
        ),
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(
                text="Принять приглашение",
                url=url,
            )
        ]])
    )])
