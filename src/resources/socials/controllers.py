from fastapi import Depends, APIRouter
from src.datasource.sqlite import bind_service
from pydantic import BaseModel
from src.core.models.socials import Socials, Platforms
from src.core.socials.youtube import YoutubePlatform
from uuid import UUID
from dataclasses import asdict
from .service import SocialsService

router = APIRouter()
tags = "socials"

class SocialCreate(BaseModel):
    tokens: dict
    extras: dict = {}
    platform: str = Platforms.twitter


@router.post("/tenants/:id/socials", tags=[tags])
def add_social_keys(tenant_id: str,
                    input_dto: SocialCreate,
                    service: SocialsService = Depends(
                        bind_service(SocialsService))):

    if service.find_token(tenant_id, input_dto.platform):
        service.delete(tenant_id, input_dto.platform)

    socials = service.create(
        Socials(tenant_id=UUID(tenant_id), **input_dto.model_dump()))

    return {
        "status": 200,
        "message": "created successful",
        "data": {
            "id": socials.id
        }
    }


class PostCreate(BaseModel):
    post_body: str
    medias: list[str, str, str, str]
    platform: str


@router.post("/tenants/socials/post", tags=[tags], deprecated=True)
def post_on_social(tenant_id: str,
                   input_dto: PostCreate,
                   service: SocialsService = Depends(
                        bind_service(SocialsService))):

    platform_service = service.get_platform(input_dto.platform, tenant_id)
    if platform_service:
        return asdict(
            platform_service.post(input_dto.post_body,
                                  media_urls=input_dto.medias))
    return {"status": 500, "message": "platform down"}


@router.get("/tenants/{{tenant_id: str}}/socials/youtube-get-auth-url",
            tags=[f"{tags}:{Platforms.youtube}"])
def get_auth_url_for_youtube(tenant_id: str,
                             redirect_uri: str = "http://localhost:8080",
                             service: SocialsService = Depends(
                        bind_service(SocialsService))):
    platform_service: YoutubePlatform = service.get_platform(Platforms.youtube, tenant_id)
    if platform_service:
        tenant_accounts_auth_url = platform_service.token_manager.get_auth_url(
            redirect_uri)
        return {
            "message":
            "go to this url, for which you want to automate the uploads",
            "url": tenant_accounts_auth_url
        }
    return {"status": 500, "message": "platform down"}


class YoutubeAuthCreate(BaseModel):
    code: str
    redirect_uri: str = "http://localhost:8080"

@router.patch("/tenants/{{tenant_id: str}}/socials/youtube-set-auth-tokens",
              tags=[f"{tags}:{Platforms.youtube}"])
def set_auth_tokens_for_youtube(tenant_id: str,
                                input_dto: YoutubeAuthCreate,
                                service: SocialsService = Depends(
                        bind_service(SocialsService))):

    platform_service: YoutubePlatform = service.get_platform(Platforms.youtube, tenant_id)
    if platform_service:
        tenant_accounts_auth_url = platform_service.token_manager.obtain_access_token_from_code(
            input_dto.code, input_dto.redirect_uri)
        return {
            "message": "access tokens set",
            "recieved": True if tenant_accounts_auth_url else False
        }
    return {"status": 500, "message": "platform down"}

@router.get("/tenants/{{tenant_id: str}}/socials/youtube-check-access_token",
            tags=[f"{tags}:{Platforms.youtube}"])
def check_youtube_token_validity(tenant_id: str,
                             service: SocialsService = Depends(
                        bind_service(SocialsService))):
    platform_service: YoutubePlatform = service.get_platform(Platforms.youtube, tenant_id)

    current_token = platform_service.token_manager.get_tokens()
    new_token = platform_service.token_manager.refresh_access_token(current_token.tokens.get("web"))

    if platform_service:
        return {
            "message": "token is still valid",
        }
    return {"status": 500, "message": "platform down"}
