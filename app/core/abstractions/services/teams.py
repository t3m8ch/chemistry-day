from typing import Protocol

from app.core import models


class TeamsService(Protocol):
    async def create_team(
            self,
            *,
            captain_telegram_id: int,
            captain_full_name: str,
            grade: str,
            team_name: str,
    ) -> models.Team:
        ...
