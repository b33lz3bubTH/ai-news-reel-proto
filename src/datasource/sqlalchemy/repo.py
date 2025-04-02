from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from typing import Type, TypeVar, Generic, List
from uuid import UUID
import datetime
# Type variable for generic repository
T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def add(self, entities: list[T]) -> None:
        for entity in entities:
            self.db.add(entity)

    def get_by_id(self, entity_id: UUID) -> T:
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def get_all(self, page: int = 1, page_size: int = 10, asc_order: bool = False) -> List[T]:
        offset = (page - 1) * page_size
        order_by_column = asc(self.model.id) if asc_order else desc(self.model.id)  # Conditional sorting

        return (
            self.db.query(self.model)
            .order_by(order_by_column)
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def delete(self, entity_id: UUID) -> None:
        entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if entity:
            self.db.delete(entity)
            self.db.commit()

    def soft_delete(self, entity_id: UUID) -> None:
        return self.update(entity_id, {
            'deleted_at': datetime.datetime.utcnow()
        })

    def update(self, entity_id: UUID, update_data: dict) -> T:
        entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if entity:
            for key, value in update_data.items():
                setattr(entity, key, value)
            self.db.commit()
            self.db.refresh(entity)
        return entity


