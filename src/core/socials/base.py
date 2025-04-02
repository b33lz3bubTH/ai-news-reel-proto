from abc import ABC, abstractmethod
from dataclasses import dataclass


### Platform Token Manager Base Interface ###
class TokenManager(ABC):

    @abstractmethod
    def get_tokens(self) -> str:
        pass


### Base Social Platform Interface ###
class SocialPlatform(ABC):

    @abstractmethod
    def post(self, text: str, media_url: str = None) -> None:
        pass


### Base Response For Post
@dataclass
class PlatformResponse:

    platform: str
    post_id: str
    post_content: dict
