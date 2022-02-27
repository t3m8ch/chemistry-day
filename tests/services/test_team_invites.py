import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import models
from app.core.exceptions.invites import InviteIsNotExists
from app.core.exceptions.players import PlayerWithThisTelegramIdIsAlreadyExists
from app.core.exceptions.teams import TeamIsNotExists
from app.core.impl.services.team_invites import TeamInvitesServiceImpl


@pytest.mark.asyncio
async def test_create_invite(db_session: AsyncSession):
    team_id = uuid.uuid4()
    db_session.add(models.Team(id=team_id, name="team1"))
    await db_session.commit()

    service = TeamInvitesServiceImpl(alchemy_session=db_session)
    returned_invite = await service.create_invite(team_id=team_id)

    invite_in_db = await db_session.scalar(
        sa.select(models.TeamInvite).where(models.TeamInvite.team_id == team_id)
    )

    assert returned_invite == invite_in_db


@pytest.mark.asyncio
async def test_create_invite_if_team_is_not_exists(db_session: AsyncSession):
    team_ids = [uuid.uuid4() for _ in range(3)]
    db_session.add_all([
        models.Team(id=team_id, name=f"team{i}")
        for i, team_id in enumerate(team_ids, start=1)
    ])
    await db_session.commit()

    service = TeamInvitesServiceImpl(alchemy_session=db_session)

    id_non_existing_team = uuid.uuid4()
    try:
        await service.create_invite(team_id=id_non_existing_team)
    except TeamIsNotExists as e:
        assert e.team_id == id_non_existing_team
    else:
        assert False


@pytest.mark.asyncio
async def test_accept_invite(db_session: AsyncSession):
    teams_ids = [uuid.uuid4() for _ in range(2)]
    invites_ids = [uuid.uuid4() for _ in range(3)]
    db_session.add_all([
        models.Team(id=teams_ids[0], name="team1", invites=[
            models.TeamInvite(id=invites_ids[0]),
            models.TeamInvite(id=invites_ids[1]),
        ]),
        models.Team(id=teams_ids[1], name="team2", invites=[
            models.TeamInvite(id=invites_ids[2]),
        ]),
    ])

    service = TeamInvitesServiceImpl(alchemy_session=db_session)
    await service.accept_invite(
        player_telegram_id=123,
        player_full_name=" Ivan  ",
        player_grade=" 10A ",
        invite_id=invites_ids[0],
    )
    await service.accept_invite(
        player_telegram_id=124,
        player_full_name=" Artem  ",
        player_grade=" 11B ",
        invite_id=invites_ids[2],
    )

    team_1 = await db_session.get(
        models.Team, teams_ids[0], options=[selectinload(models.Team.players)]
    )
    team_2 = await db_session.get(
        models.Team, teams_ids[1], options=[selectinload(models.Team.players)]
    )

    assert [(p.telegram_id, p.full_name, p.grade, p.team_invite_id)
            for p in team_1.players] == [(123, "Ivan", "10A", invites_ids[0])]
    assert [(p.telegram_id, p.full_name, p.grade, p.team_invite_id)
            for p in team_2.players] == [(124, "Artem", "11B", invites_ids[2])]


@pytest.mark.asyncio
async def test_accept_invite_if_player_is_exists(db_session: AsyncSession):
    team_id = uuid.uuid4()
    invite_id = uuid.uuid4()
    db_session.add(
        models.Team(
            id=team_id,
            name="team",
            players=[
                models.Player(telegram_id=111, full_name="Ivan", grade="10A")
            ],
            invites=[models.TeamInvite(id=invite_id)],
        )
    )
    await db_session.commit()

    service = TeamInvitesServiceImpl(alchemy_session=db_session)

    try:
        await service.accept_invite(
            player_telegram_id=111,
            player_full_name="asdf",
            player_grade="5G",
            invite_id=invite_id,
        )
    except PlayerWithThisTelegramIdIsAlreadyExists as e:
        assert e.telegram_id == 111
    else:
        assert False


@pytest.mark.asyncio
async def test_accept_invite_if_invite_is_not_exists(db_session: AsyncSession):
    team_id = uuid.uuid4()
    invite_id = uuid.uuid4()
    db_session.add(
        models.Team(
            id=team_id,
            name="team",
            invites=[models.TeamInvite(id=invite_id)],
        )
    )
    await db_session.commit()

    service = TeamInvitesServiceImpl(alchemy_session=db_session)

    id_non_existing_invite = uuid.uuid4()
    try:
        await service.accept_invite(
            player_telegram_id=111,
            player_full_name="asdf",
            player_grade="5G",
            invite_id=id_non_existing_invite,
        )
    except InviteIsNotExists as e:
        assert e.invite_id == id_non_existing_invite
    else:
        assert False
