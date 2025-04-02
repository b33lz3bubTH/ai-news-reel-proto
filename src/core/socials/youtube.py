import os
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Dict
from .base import TokenManager, SocialPlatform, PlatformResponse
from ..models.socials import Platforms, Socials
from src.datasource.sqlalchemy.repo import BaseRepository
from datetime import datetime, timedelta


class YoutubeTokenManager(TokenManager):

    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.repository = BaseRepository(Socials, db)

    def get_tokens(self) -> Optional[Socials]:
        """Retrieve token data from the database."""
        return self.repository.db.query(Socials).filter(
            Socials.tenant_id == UUID(self.tenant_id),
            Socials.platform == Platforms.youtube).first()

    def update_tokens(self, new_tokens):
        record = self.get_tokens()
        if record:
            record.tokens = new_tokens
            self.repository.db.commit()
            self.repository.db.refresh(record)
        else:
            raise ValueError(
                "No existing token entry found for the given tenant and platform."
            )

    def get_auth_url(
        self,
        redirect_uri: str,
        scopes: List[str] = ['https://www.googleapis.com/auth/youtube.upload']
    ) -> str:
        token = self.get_tokens()
        token_data = token.tokens["web"]
        auth_url = (
            f"{token_data['auth_uri']}?"
            f"client_id={token_data['client_id']}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={' '.join(scopes)}&"
            f"response_type=code&"
            f"access_type=offline&"  # Ensures a refresh_token is returned
            f"prompt=consent")
        print(f"Please visit this URL to authorize the app: {auth_url}")

        return auth_url

    def refresh_access_token(self, token_data: Dict) -> str:
        if 'refresh_token' not in token_data:
            raise ValueError(
                "No refresh_token found in token_data. Perform OAuth flow first."
            )

        refresh_url = token_data['token_uri']
        payload = {
            'client_id': token_data['client_id'],
            'client_secret': token_data['client_secret'],
            'refresh_token': token_data['refresh_token'],
            'grant_type': 'refresh_token'
        }
        response = requests.post(refresh_url, data=payload)
        response.raise_for_status()
        new_tokens = response.json()

        return new_tokens['access_token']

    def obtain_access_token_from_code(
        self,
        auth_code: str,
        redirect_uri: str,
        scopes: List[str] = ['https://www.googleapis.com/auth/youtube.upload']
    ) -> Dict:
        """Perform OAuth 2.0 flow manually without browser automation."""
        token = self.get_tokens()
        token_data = token.tokens["web"]

        token_url = token_data['token_uri']
        payload = {
            'client_id': token_data['client_id'],
            'client_secret': token_data['client_secret'],
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        tokens = response.json()

        new_tokens = {"web": {**token_data, **tokens}}
        self.update_tokens(new_tokens)

        return {
            'access_token': tokens['access_token'],
            'refresh_token': tokens.get('refresh_token'),
            'client_id': token_data['client_id'],
            'client_secret': token_data['client_secret'],
            'token_uri': token_data['token_uri'],
            'db_entry': new_tokens
        }


class YoutubePlatform(SocialPlatform):

    def __init__(self, tenant_id: str, db: Session):
        self.token_manager = YoutubeTokenManager(db, tenant_id)

    def _get_youtube_credentials(self, token_data: Dict) -> Credentials:
        # Fetch token record from your token manager
        db_token_record = self.token_manager.get_tokens()

        # Assuming db_token_record.updated_at is a datetime object or timestamp
        # If it's a string, you'll need to parse it (e.g., datetime.fromisoformat())
        updated_at = db_token_record.updated_at
        if not updated_at:
            raise Exception(
                "No updated_at timestamp found in token record. Cannot determine expiration."
            )

        # Add the refresh token lifetime (e.g., 600,000 seconds ≈ 6.94 days)
        # Adjust this value based on your actual refresh_token_expires_in (604,799 in your earlier example)
        refresh_token_lifetime = 600000  # Use the exact value from your token data
        expiration_time = updated_at + timedelta(
            seconds=refresh_token_lifetime)

        # Compare with current time
        current_time = datetime.now()
        if current_time >= expiration_time:
            raise Exception(
                "Refresh token has expired. Please re-authenticate via the OAuth flow to obtain a new refresh token."
            )

        # If we reach here, the refresh token is still valid
        # Refresh the access token if a refresh token exists
        if 'refresh_token' in token_data:
            token_data[
                'access_token'] = self.token_manager.refresh_access_token(
                    token_data)
        else:
            raise Exception(
                "No refresh token found. Use the OAuth API to get an authorization code and exchange it for tokens."
            )

        # Return Credentials object with the latest token data
        return Credentials(token=token_data['access_token'],
                           refresh_token=token_data.get('refresh_token'),
                           client_id=token_data['client_id'],
                           client_secret=token_data['client_secret'],
                           token_uri=token_data['token_uri'])

    def post(self,
             text: str,
             media_urls: Optional[List[str]] = None) -> PlatformResponse:
        tokens = self.token_manager.get_tokens()
        if not tokens:
            raise ValueError("No YouTube tokens found for this tenant.")

        youtube_credentials = self._get_youtube_credentials(
            tokens.tokens["web"])
        youtube_service = build('youtube',
                                'v3',
                                credentials=youtube_credentials)

        media_path = self._prepare_media(media_urls[0]) if media_urls else None
        if media_path:
            video_id = self._upload_to_youtube(youtube_service, text,
                                               media_path)
            return PlatformResponse(platform=Platforms.youtube,
                                    post_id=video_id,
                                    post_content=text)
        else:
            raise ValueError("No media provided for upload.")

    def _prepare_media(self, media_url: str) -> str:
        if media_url.startswith("https://"):
            response = requests.get(media_url)
            temp_file = "/tmp/downloaded_media.mp4"
            with open(temp_file, "wb") as f:
                f.write(response.content)
            return temp_file
        return media_url

    def _upload_to_youtube(self, youtube_service, text: str,
                           media_path: str) -> str:
        request_body = {
            'snippet': {
                'title': text[:100],
                'description': text,
                'tags': ['Shorts', 'Reel', 'Video'],
                'categoryId': '22',
            },
            'status': {
                'privacyStatus': 'public',
                'madeForKids': False,
            }
        }

        upload_request = youtube_service.videos().insert(part="snippet,status",
                                                         body=request_body,
                                                         media_body=media_path)
        response = upload_request.execute()
        video_id = response.get('id')
        return video_id
