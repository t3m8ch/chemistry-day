import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import ModelCommonMixin, Base


class Team(ModelCommonMixin, Base):
    __tablename__ = "team"

    name = sa.Column(sa.Unicode(100), nullable=False, unique=True)

    players = relationship("Player", back_populates="team")
