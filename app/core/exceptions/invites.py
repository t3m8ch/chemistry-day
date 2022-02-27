import uuid
from dataclasses import dataclass

from .base import CoreException


@dataclass
class InviteIsNotExists(CoreException):
    invite_id: uuid.UUID
