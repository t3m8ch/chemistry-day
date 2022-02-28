from typing import Any

from aiogram import BaseMiddleware, Bot


class BotUsernameMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self._bot = bot
        self._username = None

    async def __call__(self, handler, event, data: dict) -> Any:
        if self._username is None:
            me = await self._bot.get_me()
            self._username = me.username

        data["bot_username"] = self._username
        return await handler(event, data)
