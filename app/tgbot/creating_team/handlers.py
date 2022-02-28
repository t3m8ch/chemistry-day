from aiogram import Router, F, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State

from app.core.abstractions.services.players import PlayersService
from app.core.abstractions.services.teams import TeamsService
from app.core.exceptions.players import PlayerWithThisTelegramIdIsNotExists

router = Router()


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
            "👦 Введите ФИО (Например, <i>Иванов Иван Иванович</i>)"
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
        "🎓 Введите класс с буквой (например, <i>10А</i> или <i>6Г</i>"
    )

    await state.update_data(full_name=message.text)
    await state.set_state(CreatingTeamSG.input_grade)


@router.message(CreatingTeamSG.input_grade)
async def on_input_grade(message: types.Message, state: FSMContext):
    if len(message.text) > 16:
        await message.reply("❗ Ваше сообщение длиннее 16 символов")
        return

    await message.reply(
        "🥋 Введите название команды"
    )

    await state.update_data(grade=message.text)
    await state.set_state(CreatingTeamSG.input_team_name)


@router.message(CreatingTeamSG.input_team_name)
async def on_input_team_name(
        message: types.Message,
        state: FSMContext,
        teams_service: TeamsService,
):
    if len(message.text) > 100:
        await message.reply("❗ Ваше сообщение длиннее 100 символов")
        return

    data = await state.get_data()

    full_name = data["full_name"]
    grade = data["grade"]

    await teams_service.create_team(
        captain_telegram_id=message.from_user.id,
        captain_full_name=full_name,
        grade=grade,
        team_name=message.text,
    )

    await message.reply("✅ Команда создана!")

    await state.clear()
