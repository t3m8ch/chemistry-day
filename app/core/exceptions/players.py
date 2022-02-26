from dataclasses import dataclass

from .base import CoreException


@dataclass
class PlayerWithThisTelegramIdIsAlreadyExists(CoreException):
    telegram_id: int
