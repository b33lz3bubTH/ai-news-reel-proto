import asyncio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.plugins.webplugs.manager import PLUGIN_MANAGER

class PluginExecutorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()  # ✅ Read body once
        body_data = body.decode() if body else None
        asyncio.create_task(PLUGIN_MANAGER.execute(request, body_data))  # Fire and forget

        return await call_next(request)
