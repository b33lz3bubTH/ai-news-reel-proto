from sqlalchemy import Column, Integer, String, JSON, UniqueConstraint, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.datasource.sqlalchemy.model_base import BaseModel

class Platforms:
    twitter = "twitter"
    youtube = "youtube"
    instagram = "instagram"
    default = "default"

class Socials(BaseModel):
    __tablename__ = "socials"
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    tokens = Column(JSON, nullable=False)  # OAuth token to post on behalf of the user
    extras = Column(JSON, nullable=True)
    platform = Column(String, default=Platforms.default)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'platform', name='tenant_platform_uc'),
    )
