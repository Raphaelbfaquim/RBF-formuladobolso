from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from src.domain.repositories.log_repository import LogRepository
from src.infrastructure.database.models.system_log import SystemLog, LogLevel, LogCategory


class SQLAlchemyLogRepository(LogRepository):
    """Implementação do repositório de logs"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, log: SystemLog) -> SystemLog:
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log

    async def get_by_id(self, log_id: UUID) -> Optional[SystemLog]:
        result = await self.session.execute(
            select(SystemLog).where(SystemLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        level: Optional[LogLevel] = None,
        category: Optional[LogCategory] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_text: Optional[str] = None,
        is_error: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[SystemLog], int]:
        """Busca logs com filtros"""
        query = select(SystemLog)
        count_query = select(func.count(SystemLog.id))
        
        conditions = []
        
        if level:
            conditions.append(SystemLog.level == level)
        
        if category:
            conditions.append(SystemLog.category == category)
        
        if user_id:
            conditions.append(SystemLog.user_id == user_id)
        
        if start_date:
            conditions.append(SystemLog.created_at >= start_date)
        
        if end_date:
            conditions.append(SystemLog.created_at <= end_date)
        
        if search_text:
            search_pattern = f"%{search_text.lower()}%"
            conditions.append(
                or_(
                    SystemLog.message.ilike(search_pattern),
                    SystemLog.error_message.ilike(search_pattern),
                )
            )
        
        if is_error is not None:
            if is_error:
                conditions.append(
                    SystemLog.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
                )
            else:
                conditions.append(
                    SystemLog.level.notin_([LogLevel.ERROR, LogLevel.CRITICAL])
                )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        query = query.order_by(desc(SystemLog.created_at)).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        logs = list(result.scalars().all())
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        return logs, total

    async def get_error_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SystemLog]:
        """Obtém apenas logs de erro"""
        query = select(SystemLog).where(
            SystemLog.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
        )
        
        if start_date:
            query = query.where(SystemLog.created_at >= start_date)
        if end_date:
            query = query.where(SystemLog.created_at <= end_date)
        
        query = query.order_by(desc(SystemLog.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent_errors(self, hours: int = 24, limit: int = 50) -> List[SystemLog]:
        """Obtém erros recentes"""
        cutoff = datetime.now(pytz.UTC) - timedelta(hours=hours)
        query = select(SystemLog).where(
            and_(
                SystemLog.level.in_([LogLevel.ERROR, LogLevel.CRITICAL]),
                SystemLog.created_at >= cutoff,
            )
        ).order_by(desc(SystemLog.created_at)).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_logs_by_user(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SystemLog]:
        """Obtém logs de um usuário"""
        query = select(SystemLog).where(SystemLog.user_id == user_id)
        
        if start_date:
            query = query.where(SystemLog.created_at >= start_date)
        if end_date:
            query = query.where(SystemLog.created_at <= end_date)
        
        query = query.order_by(desc(SystemLog.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_old_logs(self, before_date: datetime) -> int:
        """Deleta logs antigos"""
        from sqlalchemy import delete
        
        stmt = delete(SystemLog).where(SystemLog.created_at < before_date)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def get_log_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Obtém estatísticas de logs"""
        query = select(
            SystemLog.level,
            func.count(SystemLog.id).label('count')
        )
        
        conditions = []
        if start_date:
            conditions.append(SystemLog.created_at >= start_date)
        if end_date:
            conditions.append(SystemLog.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.group_by(SystemLog.level)
        result = await self.session.execute(query)
        
        stats = {}
        for row in result:
            stats[row.level.value] = row.count
        
        # Contar erros
        error_query = select(func.count(SystemLog.id)).where(
            SystemLog.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
        )
        if conditions:
            error_query = error_query.where(and_(*conditions))
        
        error_result = await self.session.execute(error_query)
        error_count = error_result.scalar() or 0
        
        # Contar total
        total_query = select(func.count(SystemLog.id))
        if conditions:
            total_query = total_query.where(and_(*conditions))
        
        total_result = await self.session.execute(total_query)
        total_count = total_result.scalar() or 0
        
        return {
            "by_level": stats,
            "error_count": error_count,
            "total_count": total_count,
            "error_percentage": (error_count / total_count * 100) if total_count > 0 else 0,
        }

