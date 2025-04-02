from sqlalchemy import Column, Integer, String, JSON, UniqueConstraint, Boolean
from src.datasource.sqlalchemy.model_base import BaseModel
from src.datasource.sqlalchemy.schema_base import BaseSchema


class Entities(BaseModel):
    __tablename__ = "entities"
    name = Column(String, index=True)
    available =  Column(Boolean, default=True)
    data = Column(JSON, nullable=True)

    # Composite unique constraint
    __table_args__ = (
       # UniqueConstraint('_id', name='sys_id'),
    )

class EntitiesSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Entities
