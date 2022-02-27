from enum import Enum

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from .base import ModelCommonMixin, Base


class PlayerRole(Enum):
    captain = "captain"
    ordinary = "ordinary"


class Player(ModelCommonMixin, Base):
    __tablename__ = "player"

    telegram_id = sa.Column(sa.BigInteger, nullable=False, unique=True)
    full_name = sa.Column(sa.Unicode(100), nullable=False)
    grade = sa.Column(sa.Unicode(15), nullable=False)
    role = sa.Column(
        ENUM(PlayerRole, name="player_role"),
        nullable=False,
        server_default="ordinary",
    )

    team_id = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("team.id"), nullable=True
    )
    team = relationship("Team", back_populates="players")

    team_invite_id = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("team_invite.id"), nullable=True
    )
    team_invite = relationship("TeamInvite", back_populates="players")

    def __repr__(self):
        return f"Player({self.full_name=}, {self.grade=}, {self.role=})"
