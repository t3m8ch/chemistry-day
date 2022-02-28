from typing import Any

import pydantic
import tomli


class BaseSettings(pydantic.BaseModel):
    class Config:
        allow_mutation = False


class TgBotSettings(BaseSettings):
    token: str


class DBSettings(BaseSettings):
    url: str


class AppSettings(BaseSettings):
    tgbot: TgBotSettings
    db: DBSettings


class UnitTestsSettings(BaseSettings):
    db: DBSettings


class DBScriptsSettings(BaseSettings):
    db: DBSettings


def load_settings(path: str = None, type_=AppSettings):
    default_paths: dict[Any, str] = {
        UnitTestsSettings: "config.tests.toml",
    }
    if path is None:
        path = default_paths.get(type_) or "config.app.toml"

    toml_dict = _load_toml(path)
    return type_(**toml_dict)


def _load_toml(path: str) -> dict:
    with open(path, "rb") as f:
        return tomli.load(f)
