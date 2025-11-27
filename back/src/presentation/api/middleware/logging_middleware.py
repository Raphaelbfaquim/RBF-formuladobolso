import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.application.services.logging_service import LoggingService
from src.domain.repositories.log_repository import LogRepository
from src.infrastructure.repositories.log_repository import SQLAlchemyLogRepository
from src.infrastructure.database.base import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging automático de requisições"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar ID único para a requisição
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Obter informações da requisição
        start_time = time.time()
        method = request.method
        endpoint = str(request.url.path)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Obter usuário se autenticado
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
        
        # Executar requisição
        response = None
        error = None
        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            raise
        finally:
            # Calcular tempo de execução
            execution_time = (time.time() - start_time) * 1000  # em milissegundos
            
            # Obter status code
            status_code = response.status_code if response else 500
            
            # Criar log (assíncrono em background)
            # Nota: Em produção, isso deveria ser feito em background task
            # Por enquanto, vamos fazer de forma assíncrona mas sem bloquear a resposta
            try:
                from src.infrastructure.database.base import AsyncSessionLocal
                async with AsyncSessionLocal() as db:
                    log_repo = SQLAlchemyLogRepository(db)
                    logging_service = LoggingService(log_repo)
                    
                    await logging_service.log_api_request(
                        method=method,
                        endpoint=endpoint,
                        user_id=user_id,
                        status_code=status_code,
                        execution_time_ms=execution_time,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        request_id=request_id,
                        error=error,
                    )
            except Exception as log_error:
                # Não falhar a requisição se o log falhar
                import logging
                logging.error(f"Erro ao criar log: {log_error}")
        
        return response

