import uuid
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql import func
from src.datasource.sqlite import engine

@as_declarative()
class Base:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

@declarative_mixin
class UserAuditMixin:
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String, nullable=True)

# Combine everything into the final BaseModel
class BaseModel(Base, TimestampMixin, UserAuditMixin):
    __abstract__ = True


def create_tables():
    BaseModel.metadata.create_all(bind=engine)
