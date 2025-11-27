from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.shared.config import settings
from src.infrastructure.cache.redis_client import redis_client
from src.presentation.api.v1.routes import api_router  # routes.py (arquivo, não diretório)
from src.application.tasks.planning_checker import planning_checker
from src.presentation.api.middleware.logging_middleware import LoggingMiddleware
from src.shared.exceptions import (
    BaseAppException,
    NotFoundException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    # Iniciar tarefa de verificação de planejamentos
    planning_checker.start()
    yield
    # Shutdown
    planning_checker.stop()
    await redis_client.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de gerenciamento financeiro pessoal e familiar",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS else ["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# Exception Handlers
@app.exception_handler(BaseAppException)
async def base_app_exception_handler(request: Request, exc: BaseAppException):
    """Handler global para exceções customizadas da aplicação"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    """Handler específico para UnauthorizedException"""
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message}
    )

# Incluir rotas
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "FormuladoBolso API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "cache": "connected"
    }

