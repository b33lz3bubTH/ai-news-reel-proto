from marshmallow import fields
from sqlalchemy import Column, Integer, String, JSON, UniqueConstraint, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.datasource.sqlalchemy.model_base import BaseModel
from src.datasource.sqlalchemy.schema_base import BaseSchema


class ApiKeys(BaseModel):
    __tablename__ = "api_keys"
    api_key = Column(String, nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id"),
                       nullable=False,
                       index=True)
    expires_at = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True, nullable=False)


class Tenants(BaseModel):
    __tablename__ = "tenants"
    name = Column(String, index=True)
    available = Column(Boolean, default=True)
    data = Column(JSON, nullable=True)
    email = Column(String, index=True)

    api_keys = relationship("ApiKeys", backref="tenant", lazy="noload")

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('email', 'name', name='tenant_email_name'),
    )


class ApiKeysSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = ApiKeys


class TenantsSchema(BaseSchema):
    api_keys = fields.Nested(ApiKeysSchema,
                             many=True)  # Add the nested relationship

    class Meta(BaseSchema.Meta):
        model = Tenants
