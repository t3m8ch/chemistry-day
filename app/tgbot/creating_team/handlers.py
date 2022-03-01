from aiogram import Router, F, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State

from app.core.abstractions.services.players import PlayersService
from app.core.abstractions.services.team_invites import TeamInvitesService
from app.core.abstractions.services.teams import TeamsService
from app.core.exceptions.players import PlayerWithThisTelegramIdIsNotExists
from app.tgbot.invites.utils import send_create_invite_message
from app.tgbot.utils import build_cancel_keyboard, CANCEL_PREFIX

router = Router()
_ACTION = "creating_team"
_cancel_kb = build_cancel_keyboard(_ACTION)


class CreatingTeamSG(StatesGroup):
    input_full_name = State()
    input_grade = State()
    input_team_name = State()


@router.message(F.text == "/start create_team")
@router.message(F.text == "/create_team")
async def on_create_team(
        message: types.Message,
        state: FSMContext,
        players_service: PlayersService,
):
    try:
        player = await players_service.get_by_telegram_id(
            message.from_user.id, load_team=True
        )
    except PlayerWithThisTelegramIdIsNotExists:
        await message.reply(
            "👦 Введите ФИО (Например, <i>Иванов Иван Иванович</i>)",
            reply_markup=_cancel_kb,
        )
        await state.set_state(CreatingTeamSG.input_full_name)
    else:
        if player.team is not None:
            await message.reply("❗ Вы уже состоите в команде")


@router.message(CreatingTeamSG.input_full_name)
async def on_input_full_name(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.reply("❗ Ваше сообщение длиннее 100 символов")
        return

    await message.reply(
        "🎓 Введите класс с буквой (например, <i>10А</i> или <i>6Г</i>",
        reply_markup=_cancel_kb,
    )

    await state.update_data(full_name=message.text)
    await state.set_state(CreatingTeamSG.input_grade)


@router.message(CreatingTeamSG.input_grade)
async def on_input_grade(message: types.Message, state: FSMContext):
    if len(message.text) > 16:
        await message.reply("❗ Ваше сообщение длиннее 16 символов")
        return

    await message.reply(
        "🥋 Введите название команды",
        reply_markup=_cancel_kb,
    )

    await state.update_data(grade=message.text)
    await state.set_state(CreatingTeamSG.input_team_name)


@router.message(CreatingTeamSG.input_team_name)
async def on_input_team_name(
        message: types.Message,
        state: FSMContext,
        teams_service: TeamsService,
        team_invites_service: TeamInvitesService,
):
    if len(message.text) > 100:
        await message.reply("❗ Ваше сообщение длиннее 100 символов")
        return

    data = await state.get_data()

    full_name = data["full_name"]
    grade = data["grade"]

    team = await teams_service.create_team(
        captain_telegram_id=message.from_user.id,
        captain_full_name=full_name,
        grade=grade,
        team_name=message.text,
    )

    await message.reply("✅ Команда создана!")
    await send_create_invite_message(message, team.id, team_invites_service)

    await state.clear()


@router.callback_query(F.data == f"{CANCEL_PREFIX}{_ACTION}")
async def on_cancel_creating_team(cq: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer()
    await cq.message.answer(
        "😥 Создание команды отменено. \n"
        "Если снова захотите поучавствовать в игре, "
        "используйте команду /create_team"
    )
