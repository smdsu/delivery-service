from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.app_settings import app_settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=app_settings.NAME,
        version=app_settings.VERSION,
        description=app_settings.DESCRIPTION,
        debug=app_settings.DEBUG,
        docs_url=app_settings.DOCS_URL,
        redoc_url=app_settings.REDOC_URL,
    )

    app.add_middleware(
        CORSMiddleware,
        **app_settings.get_cors_config(),
    )

    return app


app = create_app()


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": app_settings.VERSION,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=app_settings.DEBUG,
    )
