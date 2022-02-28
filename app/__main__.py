import logging

from aiogram import Bot, Dispatcher, Router, types
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.init.settings import load_settings
from app.tgbot import creating_team
from app.tgbot.middlewares.di import DIMiddleware

router = Router()


@router.message(commands={"start"})
async def on_start_command(message: types.Message) -> None:
    await message.answer("Привет!")


def main():
    settings = load_settings()
    logging.basicConfig(level=logging.DEBUG)

    dp = Dispatcher()

    alchemy_engine = create_async_engine(settings.db.url)
    session_maker = sessionmaker(alchemy_engine, class_=AsyncSession)

    dp.update.middleware(DIMiddleware(session_maker))

    dp.include_router(creating_team.router)
    dp.include_router(router)

    bot = Bot(settings.tgbot.token, parse_mode="HTML")
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
