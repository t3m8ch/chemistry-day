import uuid
from typing import Protocol

from app.core import models


class TeamInvitesService(Protocol):
    async def create_invite(self, *, team_id: uuid.UUID) -> models.TeamInvite:
        ...

    async def accept_invite(
            self,
            *,
            player_telegram_id: int,
            player_full_name: str,
            player_grade: str,
            invite_id: uuid.UUID
    ) -> None:
        ...
