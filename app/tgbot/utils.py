from aiogram import types

CANCEL_PREFIX = "cancel_"


def build_cancel_keyboard(action: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text="Отменить",
            callback_data=f"{CANCEL_PREFIX}{action}"
        )
    ]])
