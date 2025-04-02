from sqlalchemy.orm import Session, joinedload, aliased, selectinload
from sqlalchemy import desc
from uuid import UUID, uuid4
from src.datasource.sqlalchemy.repo import BaseRepository
from .models import Tenants, ApiKeys
from datetime import datetime, timedelta


class TenantsService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = BaseRepository(Tenants, db)

    def create(self, tenant: Tenants) -> Tenants:
        with self.repository.db.begin() as _transaction_ctx:
            self.repository.add([tenant])
            self.repository.db.flush()
            api_key = self.create_api_key(tenant)
            self.repository.add([api_key])
            self.repository.db.commit()
        return tenant

    def create_api_key(self, tenant: Tenants) -> ApiKeys:
        return ApiKeys(
            tenant_id=tenant.id,
            api_key=f"tenant-api-key:{str(uuid4())},name:{tenant.name}",
            expires_at=datetime.utcnow() + timedelta(days=30))

    def generate_key(self, _id: str) -> ApiKeys:
        tenant = self.get_by_id(_id)
        api_key = self.create_api_key(tenant)
        return self.repository.create(api_key)

    def get_by_id(self, _id: str) -> Tenants:
        return self.repository.get_by_id(UUID(_id))

    def get_by_id_and_key(self,
                          _id: str,
                          load_relations: bool = False) -> Tenants | None:
        api_keys_alias = aliased(
            ApiKeys,
            self.repository.db.query(ApiKeys).filter(
                ApiKeys.tenant_id == UUID(_id)).order_by(
                    desc(ApiKeys.expires_at)).limit(2).subquery(),
        )

        query = self.repository.db.query(Tenants).filter(
            Tenants.id == UUID(_id))

        if load_relations:
            query = query.options(
                selectinload(Tenants.api_keys.of_type(api_keys_alias)))

        tenant = query.first()
        return tenant

    def get_records(self, page: int = 1, page_size: int = 10) -> list[Tenants]:
        return self.repository.get_all(page, page_size)

    def delete_record(self, _id: str) -> None:
        self.repository.delete(UUID(_id))

    def update_record(self, _id: str, update_data: dict) -> Tenants:
        return self.repository.update(UUID(_id), update_data)
