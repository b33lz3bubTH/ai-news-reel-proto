import os
import requests
from sqlalchemy.orm import Session
from .base import TokenManager, SocialPlatform, PlatformResponse
from ..models.socials import Platforms, Socials
from uuid import UUID
from typing import Optional, List
from src.datasource.sqlalchemy.repo import BaseRepository


### Instagram Token Manager ###
class InstagramTokenManager(TokenManager):

    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.repository = BaseRepository(Socials, db)

    def get_tokens(self):
        tokens = self.repository.db.query(Socials).filter(
            Socials.tenant_id == UUID(self.tenant_id),
            Socials.platform == Platforms.instagram).first()
        return tokens


### Instagram Platform ###
class InstagramPlatform(SocialPlatform):

    def __init__(self, tenant_id: str, db: Session):
        self.token_manager = InstagramTokenManager(db, tenant_id)

    def post(self, text: str, media_urls: Optional[List[str]] = None):
        return PlatformResponse(platform=Platforms.instagram, post_id="______", post_content="============")
