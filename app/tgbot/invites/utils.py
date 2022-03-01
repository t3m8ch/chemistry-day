import uuid

import base58
from aiogram import types

from app.core.abstractions.services.team_invites import TeamInvitesService
from .constants import SEND_INVITE_PREFIX


async def send_create_invite_message(
        message: types.Message,
        team_id: uuid.UUID,
        team_invites_service: TeamInvitesService,
) -> None:
    invite = await team_invites_service.create_invite(team_id=team_id)
    await message.answer(
        "🎎 Теперь вы можете пригласить своих друзей в команду. "
        "Для этого используйте кнопку ниже",
        reply_markup=_build_send_invite_kb(invite.id),
    )


def _build_send_invite_kb(invite_id: uuid.UUID):
    base58_invite_id = base58.b58encode(invite_id.bytes).decode("utf-8")
    return types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text="Отправить приглашение",
            switch_inline_query=f"{SEND_INVITE_PREFIX}{base58_invite_id}"
        )
    ]])
