from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class BaseSchema(SQLAlchemyAutoSchema):
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    created_by = fields.String(dump_only=True)
    updated_by = fields.String(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    deleted_by = fields.String(dump_only=True)

    class Meta:
        load_instance = True
        abstract = True  # Mark this schema as abstract, no direct usage
