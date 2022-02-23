import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import models
from app.core.exceptions.teams import TeamWithThisNameIsAlreadyExists, \
    CaptainWithThisTelegramIdIsAlreadyExists
from app.core.impl.services.teams import TeamsServiceImpl


@pytest.mark.asyncio
async def test_create_team(db_session: AsyncSession):
    service = TeamsServiceImpl(db_session)
    returned_team = await service.create_team(
        captain_telegram_id=123,
        captain_full_name=" Petrov Ivan Alexandrovich   ",
        grade=" 10a   ",
        team_name="  Chemistry team "
    )

    team = await db_session.scalar(
        sa.select(models.Team).options(selectinload(models.Team.players))
    )
    assert team.name == "Chemistry team"

    assert team.players[0].telegram_id == 123
    assert team.players[0].full_name == "Petrov Ivan Alexandrovich"
    assert team.players[0].grade == "10A"
    assert team.players[0].role == models.PlayerRole.captain

    assert returned_team == team


@pytest.mark.asyncio
async def test_create_team_if_team_with_this_name_is_already_exists(
        db_session: AsyncSession
):
    db_session.add(models.Team(name="dream team"))
    await db_session.commit()

    service = TeamsServiceImpl(db_session)
    try:
        await service.create_team(
            captain_telegram_id=123,
            captain_full_name=" Petrov Ivan Alexandrovich   ",
            grade=" 10A   ",
            team_name=" Dream TeAm  ",
        )
    except TeamWithThisNameIsAlreadyExists as e:
        assert e.captain_telegram_id == 123
        assert e.captain_full_name == " Petrov Ivan Alexandrovich   "
        assert e.grade == " 10A   "
        assert e.team_name == " Dream TeAm  "

        assert await db_session.scalar(
            sa.select(sa.func.count()).select_from(models.Team)
        ) == 1
    else:
        assert False


@pytest.mark.asyncio
async def test_create_team_if_captain_with_this_telegram_id_is_already_exists(
        db_session: AsyncSession
):
    existing_captain = models.Player(
        telegram_id=123,
        full_name="AAA", grade="10A",
        role=models.PlayerRole.captain
    )
    db_session.add(existing_captain)
    await db_session.commit()

    service = TeamsServiceImpl(db_session)
    try:
        await service.create_team(
            captain_telegram_id=123,
            captain_full_name=" Petrov Ivan Alexandrovich   ",
            grade=" 10A   ",
            team_name=" Dream TeAm  ",
        )
    except CaptainWithThisTelegramIdIsAlreadyExists as e:
        assert e.captain_telegram_id == 123
        assert e.captain_full_name == " Petrov Ivan Alexandrovich   "
        assert e.grade == " 10A   "
        assert e.team_name == " Dream TeAm  "

        assert await db_session.scalar(
            sa.select(sa.func.count()).select_from(models.Team)
        ) == 0
    else:
        assert False
