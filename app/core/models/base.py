import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declarative_mixin

Base = declarative_base()


@declarative_mixin
class ModelCommonMixin:
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )
