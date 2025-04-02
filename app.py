import uvicorn
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.resources import routes
from src.datasource.sqlalchemy.model_base import create_tables
from src.plugins.webplugs.manager import PLUGIN_MANAGER
from src.plugins.middlewares import PluginExecutorMiddleware, LoggerMiddleware 

@asynccontextmanager
async def lifespan(_app: FastAPI):
    PLUGIN_MANAGER.load_plugins()
    print("[+] plugins loading completed.")
    create_tables()  # Run the function on startup
    print("[+] sqlalchemy tables init/sync completed.")
    yield  # Allows the app to continue running
    print("shutting down...")


app = FastAPI(title="Real Estate", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred", "detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

app.add_middleware(LoggerMiddleware)
app.add_middleware(PluginExecutorMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Wildcard to allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


for route in routes:
    app.include_router(route)

@app.get("/health-check")
async def health_check():
    return {"message": "working", "code": 200}

if __name__ == "__main__":
    uvicorn.run(app=app, port=8081)
