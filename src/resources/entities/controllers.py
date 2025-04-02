from fastapi import Depends, APIRouter
from src.datasource.sqlite import bind_service
from pydantic import BaseModel
from .service import EntitiesService
from .models import EntitiesSchema

from src.plugins.scrapers.sites import OlxEntityScraper
from src.plugins.middlewares.loggers import logger

router = APIRouter()
tags = "entities"


class EntitiesCreate(BaseModel):
    name: str
    data: dict = {}


entity_schema = EntitiesSchema()
entities_schema = EntitiesSchema(many=True)


@router.post("/entities/", tags=[tags], deprecated=True)
def create_entites(input_dto: EntitiesCreate,
                   service: EntitiesService = Depends(
                       bind_service(EntitiesService))):
    record = service.create(input_dto.name, input_dto.data)
    return {
        "status": 200,
        "message": "created successful",
        "data": entity_schema.dump(record)
    }


@router.get("/entities/:id", tags=[tags], deprecated=True)
def fetch_entity(entity_id: str,
                 service: EntitiesService = Depends(
                     bind_service(EntitiesService))):
    logger.info(f"fetching entity with id: {entity_id}")
    record = service.get_by_id(entity_id)
    logger.info(f"fetched entity with id: {entity_id} {record.__dict__}")
    return {
        "status": 200,
        "message": "created successful",
        "data": entity_schema.dump(record)
    }


@router.get("/entities/web-scrapper" , tags=[tags], deprecated=True)
async def fetch_leads(website: str):
    h_scraper = OlxEntityScraper()
    record = h_scraper.run(website)
    return {"status": 200, "record": record}
