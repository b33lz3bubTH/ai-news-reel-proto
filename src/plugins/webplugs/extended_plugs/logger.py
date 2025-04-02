from fastapi import Request
from src.plugins.webplugs.manager import BasePlugin

class LoggerPlugin(BasePlugin):
    async def exec(self, request: Request, data):
        print(f"[LOGGER] {request.method} {request.url} {request.headers}")
        print("data: ", data)

