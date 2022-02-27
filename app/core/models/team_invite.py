import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as ps
from sqlalchemy.orm import relationship

from .base import ModelCommonMixin, Base


class TeamInvite(ModelCommonMixin, Base):
    __tablename__ = "team_invite"

    team_id = sa.Column(
        ps.UUID(as_uuid=True), sa.ForeignKey("team.id"), nullable=False
    )
    team = relationship("Team", back_populates="invites")

    players = relationship("Player", back_populates="team_invite")

    def __repr__(self):
        return (
            f"TeamInvite({self.team_id=}))"
        )
