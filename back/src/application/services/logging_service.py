from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import traceback
import sys
import pytz
from src.domain.repositories.log_repository import LogRepository
from src.infrastructure.database.models.system_log import SystemLog, LogLevel, LogCategory


class LoggingService:
    """Serviço centralizado de logging"""

    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository

    async def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        user_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        execution_time_ms: Optional[float] = None,
        exception: Optional[Exception] = None,
    ) -> SystemLog:
        """Cria um log genérico"""
        log = SystemLog(
            level=level,
            category=category,
            message=message,
            details=details,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            status_code=str(status_code) if status_code else None,
            execution_time_ms=str(execution_time_ms) if execution_time_ms else None,
        )

        # Adicionar informações de erro se houver exceção
        if exception:
            log.error_type = type(exception).__name__
            log.error_message = str(exception)
            log.stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            log.exception_data = {
                "exception_type": type(exception).__name__,
                "exception_args": str(exception.args) if exception.args else None,
            }

        return await self.log_repository.create(log)

    async def log_info(
        self,
        category: LogCategory,
        message: str,
        **kwargs
    ) -> SystemLog:
        """Log de informação"""
        return await self.log(LogLevel.INFO, category, message, **kwargs)

    async def log_warning(
        self,
        category: LogCategory,
        message: str,
        **kwargs
    ) -> SystemLog:
        """Log de aviso"""
        return await self.log(LogLevel.WARNING, category, message, **kwargs)

    async def log_error(
        self,
        category: LogCategory,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs
    ) -> SystemLog:
        """Log de erro"""
        return await self.log(LogLevel.ERROR, category, message, exception=exception, **kwargs)

    async def log_critical(
        self,
        category: LogCategory,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs
    ) -> SystemLog:
        """Log crítico"""
        return await self.log(LogLevel.CRITICAL, category, message, exception=exception, **kwargs)

    async def log_debug(
        self,
        category: LogCategory,
        message: str,
        **kwargs
    ) -> SystemLog:
        """Log de debug"""
        return await self.log(LogLevel.DEBUG, category, message, **kwargs)

    async def log_api_request(
        self,
        method: str,
        endpoint: str,
        user_id: Optional[UUID] = None,
        status_code: int = 200,
        execution_time_ms: Optional[float] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        error: Optional[Exception] = None,
    ) -> SystemLog:
        """Log específico para requisições API"""
        level = LogLevel.ERROR if status_code >= 500 else (LogLevel.WARNING if status_code >= 400 else LogLevel.INFO)
        message = f"{method} {endpoint} - {status_code}"
        
        if error:
            return await self.log_error(
                LogCategory.API,
                message,
                exception=error,
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                execution_time_ms=execution_time_ms,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )
        
        return await self.log(
            level,
            LogCategory.API,
            message,
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            execution_time_ms=execution_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )

    async def log_transaction(
        self,
        action: str,
        transaction_id: UUID,
        user_id: UUID,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
    ) -> SystemLog:
        """Log específico para transações"""
        message = f"Transação {action}: {transaction_id}"
        level = LogLevel.ERROR if error else LogLevel.INFO
        
        log_details = {"transaction_id": str(transaction_id), **(details or {})}
        
        if error:
            return await self.log_error(
                LogCategory.TRANSACTION,
                message,
                exception=error,
                user_id=user_id,
                details=log_details,
            )
        
        return await self.log(
            level,
            LogCategory.TRANSACTION,
            message,
            user_id=user_id,
            details=log_details,
        )

    async def log_auth(
        self,
        action: str,
        user_id: Optional[UUID] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        error: Optional[Exception] = None,
    ) -> SystemLog:
        """Log específico para autenticação"""
        message = f"Autenticação {action}: {'Sucesso' if success else 'Falha'}"
        level = LogLevel.ERROR if error or not success else LogLevel.INFO
        
        if error:
            return await self.log_error(
                LogCategory.AUTH,
                message,
                exception=error,
                user_id=user_id,
                ip_address=ip_address,
            )
        
        return await self.log(
            level,
            LogCategory.AUTH,
            message,
            user_id=user_id,
            ip_address=ip_address,
        )

