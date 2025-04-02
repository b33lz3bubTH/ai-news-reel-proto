from fastapi import Depends, APIRouter
from src.datasource.sqlite import bind_service
from pydantic import BaseModel
from .models import Tenants, TenantsSchema, ApiKeysSchema
from .service import TenantsService

router = APIRouter()
tags = "tenants"


class TenantsCreate(BaseModel):
    name: str
    data: dict = {}
    email: str


tenant_schema = TenantsSchema()


@router.post("/tenants/", tags=[tags])
def create_entites(input_dto: TenantsCreate,
                   service: TenantsService = Depends(
                       bind_service(TenantsService))):
    record = service.create(Tenants(**input_dto.model_dump()))
    print("record: ", record, type(record))
    return {
        "status": 200,
        "message": "created successful",
        "data": tenant_schema.dump(record)
    }


@router.get("/tenants/:id", tags=[tags])
def fetch_tenant(entity_id: str,
                 service: TenantsService = Depends(
                     bind_service(TenantsService))):
    record = service.get_by_id_and_key(entity_id)
    return {
        "status": 200,
        "message": "created successful",
        "data": tenant_schema.dump(record)
    }


api_key_schema = ApiKeysSchema()


@router.get("/tenants/:id/generate-key", tags=[tags])
def add_new_key(tenant_id: str,
                service: TenantsService = Depends(
                    bind_service(TenantsService))):
    api_key = service.generate_key(tenant_id)
    return {
        "status": 200,
        "message": "created successful",
        "data": api_key_schema.dump(api_key)
    }


