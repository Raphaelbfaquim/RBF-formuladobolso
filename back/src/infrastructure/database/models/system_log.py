from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class LogLevel(str, enum.Enum):
    """Níveis de log"""
    DEBUG = "debug"  # Informações detalhadas para debug
    INFO = "info"  # Informações gerais
    WARNING = "warning"  # Avisos
    ERROR = "error"  # Erros que não impedem a execução
    CRITICAL = "critical"  # Erros críticos que impedem a execução


class LogCategory(str, enum.Enum):
    """Categorias de log"""
    AUTH = "auth"  # Autenticação e autorização
    TRANSACTION = "transaction"  # Transações financeiras
    ACCOUNT = "account"  # Contas
    PLANNING = "planning"  # Planejamentos
    USER = "user"  # Usuários
    SYSTEM = "system"  # Sistema geral
    API = "api"  # Requisições API
    DATABASE = "database"  # Operações de banco
    NOTIFICATION = "notification"  # Notificações
    INTEGRATION = "integration"  # Integrações externas
    SECURITY = "security"  # Segurança
    PERFORMANCE = "performance"  # Performance
    WORKSPACE = "workspace"  # Workspaces
    TRANSFER = "transfer"  # Transferências
    SCHEDULED = "scheduled"  # Transações agendadas
    CALENDAR = "calendar"  # Calendário


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Informações básicas
    level = Column(SQLEnum(LogLevel), nullable=False, index=True)
    category = Column(SQLEnum(LogCategory), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Detalhes adicionais em JSON
    
    # Contexto
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)  # ID único da requisição
    
    # Informações de erro (quando aplicável)
    error_type = Column(String(200), nullable=True)  # Tipo do erro (ex: ValueError, HTTPException)
    error_message = Column(Text, nullable=True)  # Mensagem do erro
    stack_trace = Column(Text, nullable=True)  # Stack trace completo
    exception_data = Column(JSON, nullable=True)  # Dados adicionais do erro
    
    # Informações de performance
    execution_time_ms = Column(String(20), nullable=True)  # Tempo de execução em milissegundos
    memory_usage_mb = Column(String(20), nullable=True)  # Uso de memória
    
    # Endpoint/Operação
    endpoint = Column(String(500), nullable=True)  # Endpoint da API
    method = Column(String(10), nullable=True)  # Método HTTP
    status_code = Column(String(10), nullable=True)  # Status HTTP
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False, index=True)
    
    # Relacionamentos
    user = relationship("User", backref="logs")

    # Índices compostos para consultas frequentes
    __table_args__ = (
        Index('idx_log_level_category', 'level', 'category'),
        Index('idx_log_user_created', 'user_id', 'created_at'),
        Index('idx_log_error_levels', 'level', 'created_at'),
    )

