from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.system_log import SystemLog, LogLevel, LogCategory


class LogRepository(ABC):
    """Interface do repositório de logs"""

    @abstractmethod
    async def create(self, log: SystemLog) -> SystemLog:
        """Cria um novo log"""
        pass

    @abstractmethod
    async def get_by_id(self, log_id: UUID) -> Optional[SystemLog]:
        """Obtém um log por ID"""
        pass

    @abstractmethod
    async def search(
        self,
        level: Optional[LogLevel] = None,
        category: Optional[LogCategory] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_text: Optional[str] = None,
        is_error: Optional[bool] = None,  # True para ERROR e CRITICAL
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[SystemLog], int]:
        """Busca logs com filtros"""
        pass

    @abstractmethod
    async def get_error_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SystemLog]:
        """Obtém apenas logs de erro (ERROR e CRITICAL)"""
        pass

    @abstractmethod
    async def get_recent_errors(self, hours: int = 24, limit: int = 50) -> List[SystemLog]:
        """Obtém erros recentes"""
        pass

    @abstractmethod
    async def get_logs_by_user(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SystemLog]:
        """Obtém logs de um usuário específico"""
        pass

    @abstractmethod
    async def delete_old_logs(self, before_date: datetime) -> int:
        """Deleta logs antigos (retorna quantidade deletada)"""
        pass

    @abstractmethod
    async def get_log_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Obtém estatísticas de logs"""
        pass

