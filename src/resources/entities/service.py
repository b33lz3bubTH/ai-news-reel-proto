from sqlalchemy.orm import Session
from uuid import UUID
from src.datasource.sqlalchemy.repo import BaseRepository
from .models import Entities
from src.plugins.middlewares.loggers import logger


class EntitiesService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = BaseRepository(Entities, db)

    def create(self, name: str, data: dict = {}) -> Entities:
        record = Entities(name=name, data=data)
        return self.repository.create(record)

    def get_by_id(self, _id: str) -> Entities:
        logger.info(f"get_records with id: {_id} UUID({UUID(_id)})")
        return self.repository.get_by_id(UUID(_id))

    def get_records(self,
                    page: int = 1,
                    page_size: int = 10) -> list[Entities]:
        return self.repository.get_all(page, page_size)

    def delete_record(self, _id: str) -> None:
        self.repository.delete(UUID(_id))

    def update_record(self, _id: str, update_data: dict) -> Entities:
        return self.repository.update(UUID(_id), update_data)
