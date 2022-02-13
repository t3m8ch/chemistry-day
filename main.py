import logging

import pydantic
from aiogram import Router, Bot, Dispatcher, types


class Settings(pydantic.BaseSettings):
    bot_token: str

    class Config:
        allow_mutation = False


router = Router()


@router.message(commands={"start"})
async def on_start_command(message: types.Message) -> None:
    await message.answer("Привет!")


def main():
    settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
    logging.basicConfig(level=logging.DEBUG)

    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(settings.bot_token, parse_mode="HTML")
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
