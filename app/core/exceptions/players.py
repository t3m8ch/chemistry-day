from dataclasses import dataclass

from .base import CoreException


@dataclass
class PlayerWithThisTelegramIdIsAlreadyExists(CoreException):
    telegram_id: int


@dataclass
class PlayerWithThisTelegramIdIsNotExists(CoreException):
    telegram_id: int
