from sqlalchemy import Column, Integer, String, JSON, UniqueConstraint, Boolean, DateTime, ForeignKey, event
from sqlalchemy.dialects.postgresql import UUID
from src.datasource.sqlalchemy.model_base import BaseModel


class Trackers(BaseModel):
    __tablename__ = "trackers"
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    url = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint('tenant_id',
                                       'url',
                                       name='tenant_url_uc'), )

@event.listens_for(Trackers, 'after_insert')
def log_insert(mapper, connection, target):
    print(f"Inserted in trackers {target.id}: ", target)
