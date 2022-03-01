import uuid

import base58
from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State

from app.core.abstractions.services.team_invites import TeamInvitesService
from app.core.exceptions.invites import InviteIsNotExists
from app.core.exceptions.players import PlayerWithThisTelegramIdIsAlreadyExists
from .constants import SEND_INVITE_PREFIX, ACCEPT_INVITE_PREFIX
from ..utils import build_cancel_keyboard, CANCEL_PREFIX

router = Router()
_ACTION = "invite_accepting"
_cancel_kb = build_cancel_keyboard(_ACTION)


@router.inline_query(F.query.startswith(SEND_INVITE_PREFIX))
async def on_send_invite_inline_query(iq: types.InlineQuery, bot_username: str):
    base58_invite_id = iq.query[len(SEND_INVITE_PREFIX):]
    url = (
        f"https://t.me/{bot_username}"
        f"?start={ACCEPT_INVITE_PREFIX}{base58_invite_id}"
    )

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


class AcceptingInviteSG(StatesGroup):
    input_full_name = State()
    input_grade = State()


@router.message(F.text.startswith(f"/start {ACCEPT_INVITE_PREFIX}"))
async def on_accept_invite(message: types.Message, state: FSMContext):
    base58_invite_id = message.text[len(f"/start {ACCEPT_INVITE_PREFIX}"):]
    await state.update_data(base58_invite_id=base58_invite_id)

    await state.set_state(AcceptingInviteSG.input_full_name)
    await message.reply(
        "👦 Введите ФИО (Например, <i>Иванов Иван Иванович</i>)",
        reply_markup=_cancel_kb,
    )


@router.message(AcceptingInviteSG.input_full_name)
async def on_accepting_invite_input_full_name(
        message: types.Message, state: FSMContext
):
    if len(message.text) > 100:
        await message.reply("❗ Ваше сообщение длиннее 100 символов")
        return

    await message.reply(
        "🎓 Введите класс с буквой (например, <i>10А</i> или <i>6Г</i>",
        reply_markup=_cancel_kb,
    )

    await state.update_data(full_name=message.text)
    await state.set_state(AcceptingInviteSG.input_grade)


@router.message(AcceptingInviteSG.input_grade)
async def on_accepting_invite_input_grade(
        message: types.Message,
        state: FSMContext,
        team_invites_service: TeamInvitesService,
):
    if len(message.text) > 16:
        await message.reply("❗ Ваше сообщение длиннее 16 символов")
        return

    data = await state.get_data()

    full_name = data["full_name"]
    grade = message.text

    base58_invite_id = data["base58_invite_id"]
    invite_id = uuid.UUID(bytes=base58.b58decode(base58_invite_id))

    try:
        await team_invites_service.accept_invite(
            player_telegram_id=message.from_user.id,
            player_full_name=full_name,
            player_grade=grade,
            invite_id=invite_id,
        )
    except InviteIsNotExists:
        await message.reply("❗ Приглашение было удалено или не существует")
        await state.clear()
    except PlayerWithThisTelegramIdIsAlreadyExists:
        await state.clear()
        await message.reply("❗ Вы уже состоите в команде")
    else:
        await message.reply("✅ Вы в команде!")


@router.callback_query(F.data == f"{CANCEL_PREFIX}{_ACTION}")
async def on_cancel_creating_team(cq: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer()
    await cq.message.answer("😥 Вы отменили принятие приглашения.")
