from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.files import router as files_router
from app.api.routes.process import router as process_router
from app.api.routes.image import router as image_router
from app.api.routes.pdf import router as pdf_router
from app.api.routes.document import router as document_router
from app.api.routes.audio import router as audio_router
from app.api.routes.video import router as video_router
from app.api.routes import download
from app.api.routes.ai import router as ai_router


from app.api.routes.processing_history import (
    router as processing_history_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="All-in-one AI-powered file and media workspace",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    auth_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    files_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    process_router,
    prefix="/api/v1",
)

app.include_router(
    image_router,
    prefix="/api/v1",
)

app.include_router(
    pdf_router,
    prefix="/api/v1",
)

app.include_router(
    document_router,
    prefix="/api/v1",
)

app.include_router(
    audio_router,
    prefix="/api/v1",
)

app.include_router(
    video_router,
    prefix="/api/v1",
)

app.include_router(
    processing_history_router,
    prefix="/api/v1",
)

app.include_router(
    download.router,
    prefix="/api/v1",
    )

app.include_router(
    ai_router,
    prefix="/api/v1",
)

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} API is running",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
    }