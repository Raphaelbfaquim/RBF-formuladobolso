from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import pytz
from src.presentation.schemas.log import (
    LogFilter,
    LogResponse,
    LogSearchResponse,
    LogStatisticsResponse,
)
from src.presentation.api.dependencies import get_current_active_user, get_db
from src.domain.repositories.log_repository import LogRepository
from src.infrastructure.repositories.log_repository import SQLAlchemyLogRepository
from src.application.services.logging_service import LoggingService
from src.infrastructure.database.models.user import User
from src.infrastructure.database.models.system_log import LogLevel, LogCategory
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_log_repository(db: AsyncSession = Depends(get_db)) -> LogRepository:
    return SQLAlchemyLogRepository(db)


def get_logging_service(log_repo: LogRepository = Depends(get_log_repository)) -> LoggingService:
    return LoggingService(log_repo)


@router.post("/search", response_model=LogSearchResponse)
async def search_logs(
    filters: LogFilter,
    log_repo: LogRepository = Depends(get_log_repository),
    current_user: User = Depends(get_current_active_user),
):
    """Busca logs com filtros avançados"""
    # Converter string para enum
    level = LogLevel(filters.level) if filters.level else None
    category = LogCategory(filters.category) if filters.category else None
    
    logs, total = await log_repo.search(
        level=level,
        category=category,
        user_id=filters.user_id,
        start_date=filters.start_date,
        end_date=filters.end_date,
        search_text=filters.search_text,
        is_error=filters.is_error,
        limit=filters.page_size,
        offset=(filters.page - 1) * filters.page_size,
    )
    
    total_pages = (total + filters.page_size - 1) // filters.page_size
    
    return LogSearchResponse(
        logs=[LogResponse.from_orm(log) for log in logs],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=total_pages,
    )


@router.get("/errors", response_model=List[LogResponse])
async def get_error_logs(
    hours: int = Query(24, ge=1, le=720, description="Últimas N horas"),
    limit: int = Query(50, ge=1, le=500),
    log_repo: LogRepository = Depends(get_log_repository),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém apenas logs de erro (ERROR e CRITICAL)"""
    logs = await log_repo.get_recent_errors(hours=hours, limit=limit)
    return [LogResponse.from_orm(log) for log in logs]


@router.get("/errors/all", response_model=List[LogResponse])
async def get_all_error_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    log_repo: LogRepository = Depends(get_log_repository),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém todos os logs de erro no período"""
    logs = await log_repo.get_error_logs(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return [LogResponse.from_orm(log) for log in logs]


@router.get("/user/{user_id}", response_model=List[LogResponse])
async def get_user_logs(
    user_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    log_repo: LogRepository = Depends(get_log_repository),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém logs de um usuário específico"""
    # Verificar permissão (apenas próprio usuário ou admin)
    if user_id != current_user.id:
        # TODO: Verificar se é admin
        raise HTTPException(status_code=403, detail="Sem permissão para ver logs de outros usuários")
    
    logs = await log_repo.get_logs_by_user(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return [LogResponse.from_orm(log) for log in logs]


@router.get("/statistics", response_model=LogStatisticsResponse)
async def get_log_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    log_repo: LogRepository = Depends(get_log_repository),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém estatísticas de logs"""
    stats = await log_repo.get_log_statistics(
        start_date=start_date,
        end_date=end_date,
    )
    return LogStatisticsResponse(**stats)


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: UUID,
    log_repo: LogRepository = Depends(get_log_repository),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém um log específico por ID"""
    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log não encontrado")
    
    # Verificar permissão
    if log.user_id and log.user_id != current_user.id:
        # TODO: Verificar se é admin
        raise HTTPException(status_code=403, detail="Sem permissão para ver este log")
    
    return LogResponse.from_orm(log)


@router.delete("/old")
async def delete_old_logs(
    days: int = Query(90, ge=1, description="Deletar logs mais antigos que N dias"),
    log_repo: LogRepository = Depends(get_log_repository),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta logs antigos (apenas admin)"""
    # TODO: Verificar se é admin
    cutoff_date = datetime.now(pytz.UTC) - timedelta(days=days)
    deleted_count = await log_repo.delete_old_logs(cutoff_date)
    return {"message": f"{deleted_count} logs deletados", "deleted_count": deleted_count}

