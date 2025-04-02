from sqlalchemy.orm import Session, joinedload, aliased, selectinload
from sqlalchemy import desc
from uuid import UUID, uuid4
from src.datasource.sqlalchemy.repo import BaseRepository
from datetime import datetime, timedelta
from typing import Dict
from src.core.models.trackers import Trackers


class NewsTrackerService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = BaseRepository(Trackers, db)

    def _prepare(self, tenant_id: str, url: str):
        return Trackers(tenant_id=UUID(tenant_id), url=url)

    def create(self, record: Trackers) -> Trackers:
        return self.repository.create(record)

    def find_record(self, tenant_id: str, url: str):
        return self.repository.db.query(Trackers).filter(
            Trackers.tenant_id == UUID(tenant_id),
            Trackers.url == url).first()
