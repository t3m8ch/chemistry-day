from typing import Protocol

from app.core import models


class PlayersService(Protocol):
    async def get_by_telegram_id(
            self, telegram_id: int, *, load_team=False
    ) -> models.Player:
        ...
