from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.health import router as v1_health_router
from app.api.v1.retrieval import router as v1_retrieval_router
from app.api.v1.doubt import router as v1_doubt_router
from app.api.v1.practice import router as v1_practice_router
from app.api.v1.teacher import router as v1_teacher_router
from app.api.v1.student import router as v1_student_router
from app.api.v1.auth import router as v1_auth_router
from app.core.config import settings
from app.core.logging import setup_logging

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.errors import http_exception_handler, validation_exception_handler, global_exception_handler

# Initialize logging
setup_logging()

app_kwargs = {
    "title": "ShikshaSetu AI API",
    "description": "Backend powering the personalized education platform.",
    "version": "0.1.0",
    "debug": settings.DEBUG,
}

if settings.ENVIRONMENT == "production" and not settings.DEBUG:
    app_kwargs["docs_url"] = None
    app_kwargs["redoc_url"] = None

app = FastAPI(**app_kwargs)

# Register Error Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure CORS
origins = []
if settings.CORS_ORIGINS:
    origins.extend([origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()])
if settings.FRONTEND_URL and settings.FRONTEND_URL not in origins:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep root health endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Register v1 router
app.include_router(v1_health_router, prefix="/api/v1", tags=["health"])
app.include_router(v1_auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(v1_retrieval_router, prefix="/api/v1/retrieval", tags=["retrieval"])
app.include_router(v1_doubt_router, prefix="/api/v1/doubt", tags=["doubt"])
app.include_router(v1_practice_router, prefix="/api/v1/practice", tags=["practice"])
app.include_router(v1_teacher_router, prefix="/api/v1/teacher", tags=["teacher"])
app.include_router(v1_student_router, prefix="/api/v1", tags=["student"])
