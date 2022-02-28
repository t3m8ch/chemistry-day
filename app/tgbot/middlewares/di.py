from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker

from app.core.impl.services.players import PlayersServiceImpl
from app.core.impl.services.teams import TeamsServiceImpl


class DIMiddleware(BaseMiddleware):
    def __init__(self, session_maker: sessionmaker):
        self._session_maker = session_maker

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]], Awaitable[Any]
            ],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        session = self._session_maker()

        try:
            data["teams_service"] = TeamsServiceImpl(session)
            data["players_service"] = PlayersServiceImpl(session)
            return await handler(event, data)
        finally:
            await session.close()
