import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core import models
from app.core.exceptions.players import PlayerWithThisTelegramIdIsNotExists


class PlayersServiceImpl:
    def __init__(self, alchemy_session: AsyncSession):
        self._session = alchemy_session

    async def get_by_telegram_id(
            self, telegram_id: int, *, load_team=False
    ) -> models.Player:
        query = sa.select(models.Player).where(
            models.Player.telegram_id == telegram_id
        )

        if load_team:
            query = query.options(joinedload(models.Player.team))

        if (player := await self._session.scalar(query)) is None:
            raise PlayerWithThisTelegramIdIsNotExists(telegram_id)

        return player
