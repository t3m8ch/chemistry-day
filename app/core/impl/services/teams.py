import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import models
from app.core.exceptions.teams import (
    TeamWithThisNameIsAlreadyExists,
    CaptainWithThisTelegramIdIsAlreadyExists,
)
from .utils import create_player


class TeamsServiceImpl:
    def __init__(self, alchemy_session: AsyncSession):
        self._session = alchemy_session

    async def create_team(
            self,
            *,
            captain_telegram_id: int,
            captain_full_name: str,
            grade: str,
            team_name: str,
    ) -> models.Team:
        await self._ensure_team_name_is_unique(
            captain_telegram_id, captain_full_name, grade, team_name
        )

        formatted_team_name = team_name.strip()
        captain = create_player(
            telegram_id=captain_telegram_id,
            full_name=captain_full_name,
            grade=grade,
            role=models.PlayerRole.captain
        )

        team = models.Team(name=formatted_team_name, players=[captain])

        self._session.add(team)
        await self._commit(
            captain_telegram_id, captain_full_name, grade, team_name
        )

        return team

    async def _ensure_team_name_is_unique(
            self,
            captain_telegram_id,
            captain_full_name,
            grade,
            team_name,
    ) -> None:
        team_names = (
            row[0].strip().lower()
            for row in await self._session.execute(sa.select(models.Team.name))
        )
        if team_name.strip().lower() in team_names:
            raise TeamWithThisNameIsAlreadyExists(
                captain_telegram_id,
                captain_full_name,
                grade,
                team_name,
            )

    async def _commit(
            self,
            captain_telegram_id,
            captain_full_name,
            grade,
            team_name,
    ) -> None:
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise CaptainWithThisTelegramIdIsAlreadyExists(
                captain_telegram_id,
                captain_full_name,
                grade,
                team_name,
            )
