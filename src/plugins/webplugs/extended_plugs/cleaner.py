from fastapi import Request
from src.plugins.webplugs.manager import BasePlugin

class CleanerPlugin(BasePlugin):
    async def exec(self, request: Request, data: any):
        print("[CLEANER] Cleaning data...", request.url, data)
