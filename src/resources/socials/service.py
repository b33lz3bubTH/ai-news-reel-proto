from sqlalchemy.orm import Session
from uuid import UUID
from src.datasource.sqlalchemy.repo import BaseRepository
from src.core.models.socials import Socials, Platforms
from src.core.socials.base import SocialPlatform
from src.core.socials.x_com import TwitterPlatform
from src.core.socials.instagram import InstagramPlatform
from src.core.socials.youtube import YoutubePlatform
from typing import Dict

class SocialsService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = BaseRepository(Socials, db)
        self.platforms: Dict[str, SocialPlatform] = {
            Platforms.twitter: TwitterPlatform,
            Platforms.instagram: InstagramPlatform,
            Platforms.youtube: YoutubePlatform
        }

    def get_platform(self, platform: str, tenant_id: str) -> SocialPlatform:
        if not self.platforms.get(platform):
            raise Exception("invalid platform")
        return self.platforms[platform](tenant_id, self.db)

    def create(self, record: Socials) -> Socials:
        return self.repository.create(record)

    def find_token(self, tenant_id: str, platform: str):
        return self.repository.db.query(Socials).filter(
            Socials.tenant_id == UUID(tenant_id),
            Socials.platform == platform).first()

    def delete(self, tenant_id: str, platform: str):
        token = self.find_token(tenant_id, platform)
        if token:
            self.repository.delete(token.id)
