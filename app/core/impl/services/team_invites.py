import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import models
from app.core.exceptions.invites import InviteIsNotExists
from app.core.exceptions.players import PlayerWithThisTelegramIdIsAlreadyExists
from app.core.exceptions.teams import TeamIsNotExists
from .utils import create_player


class TeamInvitesServiceImpl:
    def __init__(self, alchemy_session: AsyncSession):
        self._session = alchemy_session

    async def create_invite(self, *, team_id: uuid.UUID) -> models.TeamInvite:
        invite = models.TeamInvite(team_id=team_id)
        self._session.add(invite)

        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise TeamIsNotExists(team_id)

        return invite

    async def accept_invite(
            self,
            *,
            player_telegram_id: int,
            player_full_name: str,
            player_grade: str,
            invite_id: uuid.UUID
    ) -> None:
        player = create_player(
            telegram_id=player_telegram_id,
            full_name=player_full_name,
            grade=player_grade,
            role=models.PlayerRole.ordinary,
        )

        invite = await self._session.get(models.TeamInvite, invite_id)
        if invite is None:
            raise InviteIsNotExists(invite_id)

        player.team_id = invite.team_id
        player.team_invite_id = invite_id

        self._session.add(player)

        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise PlayerWithThisTelegramIdIsAlreadyExists(player_telegram_id)
