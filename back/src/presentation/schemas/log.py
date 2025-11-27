from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.system_log import LogLevel, LogCategory


class LogFilter(BaseModel):
    """Filtros para busca de logs"""
    level: Optional[str] = Field(None, description="Nível: debug, info, warning, error, critical")
    category: Optional[str] = Field(None, description="Categoria do log")
    user_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = Field(None, description="Busca por texto")
    is_error: Optional[bool] = Field(None, description="True para apenas erros (error e critical)")
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)


class LogResponse(BaseModel):
    """Resposta de log"""
    id: UUID
    level: str
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    execution_time_ms: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LogSearchResponse(BaseModel):
    """Resposta da busca de logs"""
    logs: List[LogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LogStatisticsResponse(BaseModel):
    """Estatísticas de logs"""
    by_level: Dict[str, int]
    error_count: int
    total_count: int
    error_percentage: float

