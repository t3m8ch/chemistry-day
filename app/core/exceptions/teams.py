import uuid
from dataclasses import dataclass

from .base import CoreException


@dataclass
class TeamWithThisNameIsAlreadyExists(CoreException):
    captain_telegram_id: int
    captain_full_name: str
    grade: str
    team_name: str


@dataclass
class TeamIsNotExists(CoreException):
    team_id: uuid.UUID
