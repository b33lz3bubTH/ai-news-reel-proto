import requests
from sqlalchemy.orm import Session
from .base import TokenManager, SocialPlatform, PlatformResponse
from ..models.socials import Platforms, Socials
from uuid import UUID
import tweepy
from typing import Optional, List
import os

from src.datasource.sqlalchemy.repo import BaseRepository


### Twitter Token Manager ###
class TwitterTokenManager(TokenManager):

    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.repository = BaseRepository(Socials, db)

    def get_tokens(self):
        tokens = self.repository.db.query(Socials).filter(
            Socials.tenant_id == UUID(self.tenant_id),
            Socials.platform == Platforms.twitter).first()
        return tokens


### Twitter Platform ###
class TwitterPlatform(SocialPlatform):

    def __init__(self, tenant_id: str, db: Session):
        self.token_manager = TwitterTokenManager(db, tenant_id)

    def tweet(self, text: str, media_url: str = None):
        tenant_config = self.token_manager.get_tokens()

        client = tweepy.Client(
            consumer_key=tenant_config.tokens.get("consumer_key"),
            consumer_secret=tenant_config.tokens.get("consumer_secret"),
            access_token=tenant_config.tokens.get("access_token"),
            access_token_secret=tenant_config.tokens.get(
                "access_token_secret"))
        return client.create_tweet(text=text)

    def post(self, text: str, media_urls: Optional[List[str]] = None):
        try:
            # Get authentication tokens
            tenant_config = self.token_manager.get_tokens()

            # Set up v2 Client for posting
            client = tweepy.Client(
                consumer_key=tenant_config.tokens.get("consumer_key"),
                consumer_secret=tenant_config.tokens.get("consumer_secret"),
                access_token=tenant_config.tokens.get("access_token"),
                access_token_secret=tenant_config.tokens.get(
                    "access_token_secret"))

            # Set up v1.1 API for media upload
            auth = tweepy.OAuth1UserHandler(
                tenant_config.tokens.get("consumer_key"),
                tenant_config.tokens.get("consumer_secret"),
                tenant_config.tokens.get("access_token"),
                tenant_config.tokens.get("access_token_secret"))
            api = tweepy.API(auth)

            media_ids = []
            if media_urls:
                if len(media_urls) > 4:
                    return (
                        400,
                        "Error: Twitter allows a maximum of 4 media items per tweet"
                    )

                for url in media_urls:
                    if url.startswith("http://") or url.startswith("https://"):
                        try:
                            response = requests.get(url, stream=True)
                            if response.status_code != 200:
                                return (
                                    400,
                                    f"Error downloading media from {url}: {response.status_code}"
                                )

                            temp_path = f"/tmp/{os.path.basename(url)}"
                            with open(temp_path, "wb") as temp_file:
                                for chunk in response.iter_content(
                                        chunk_size=8192):
                                    temp_file.write(chunk)
                        except Exception as e:
                            return (400, f"Error downloading media: {str(e)}")
                    else:
                        if not os.path.exists(url):
                            return (400,
                                    f"Error: Local file not found at {url}")
                        temp_path = url

                    try:
                        media = api.media_upload(filename=temp_path)
                        media_ids.append(media.media_id_string)
                    finally:
                        if url.startswith("http://") or url.startswith(
                                "https://"):
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)

            # Post the tweet
            if media_ids:
                response = client.create_tweet(text=text, media_ids=media_ids)
            else:
                response = client.create_tweet(text=text)

            return PlatformResponse(platform=Platforms.twitter,
                                    post_id=response.data["id"],
                                    post_content={
                                        "text": text,
                                        "medias": {
                                            "id":
                                            media_ids if media_ids else None,
                                            "orginal": media_urls
                                        },
                                        "response": response
                                    })

        except Exception as e:
            raise e
