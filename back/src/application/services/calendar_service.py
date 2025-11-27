from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository


class CalendarService:
    """Serviço para visualização de despesas em calendário"""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository

    async def get_daily_expenses(
        self, user_id: UUID, date: datetime, workspace_id: Optional[UUID] = None
    ) -> Dict:
        """Obtém despesas de um dia específico"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        transactions, _ = await self.transaction_repository.search(
            user_id=user_id,
            transaction_type="expense",
            start_date=start_date,
            end_date=end_date,
            workspace_id=workspace_id,
            status="completed",
        )

        total = sum(float(t.amount) for t in transactions)
        
        return {
            "date": date.isoformat(),
            "total_expenses": total,
            "transaction_count": len(transactions),
            "transactions": [
                {
                    "id": str(t.id),
                    "description": t.description,
                    "amount": float(t.amount),
                    "category": t.category.name if t.category else None,
                    "account": t.account.name if t.account else None,
                }
                for t in transactions
            ],
        }

    async def get_monthly_expenses(
        self, user_id: UUID, year: int, month: int, workspace_id: Optional[UUID] = None
    ) -> Dict:
        """Obtém despesas de um mês"""
        start_date = datetime(year, month, 1, 0, 0, 0)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)

        transactions, _ = await self.transaction_repository.search(
            user_id=user_id,
            transaction_type="expense",
            start_date=start_date,
            end_date=end_date,
            workspace_id=workspace_id,
            status="completed",
        )

        # Agrupar por dia
        daily_expenses = {}
        for t in transactions:
            day = t.transaction_date.day
            if day not in daily_expenses:
                daily_expenses[day] = {
                    "date": t.transaction_date.date().isoformat(),
                    "total": 0.0,
                    "count": 0,
                    "transactions": [],
                }
            daily_expenses[day]["total"] += float(t.amount)
            daily_expenses[day]["count"] += 1
            daily_expenses[day]["transactions"].append({
                "id": str(t.id),
                "description": t.description,
                "amount": float(t.amount),
                "category": t.category.name if t.category else None,
            })

        total = sum(float(t.amount) for t in transactions)
        
        return {
            "year": year,
            "month": month,
            "total_expenses": total,
            "transaction_count": len(transactions),
            "daily_expenses": list(daily_expenses.values()),
            "average_daily": total / len(daily_expenses) if daily_expenses else 0,
        }

    async def get_yearly_expenses(
        self, user_id: UUID, year: int, workspace_id: Optional[UUID] = None
    ) -> Dict:
        """Obtém despesas de um ano"""
        start_date = datetime(year, 1, 1, 0, 0, 0)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        transactions, _ = await self.transaction_repository.search(
            user_id=user_id,
            transaction_type="expense",
            start_date=start_date,
            end_date=end_date,
            workspace_id=workspace_id,
            status="completed",
        )

        # Agrupar por mês
        monthly_expenses = {}
        for t in transactions:
            month = t.transaction_date.month
            if month not in monthly_expenses:
                monthly_expenses[month] = {
                    "month": month,
                    "total": 0.0,
                    "count": 0,
                    "transactions": [],
                }
            monthly_expenses[month]["total"] += float(t.amount)
            monthly_expenses[month]["count"] += 1

        total = sum(float(t.amount) for t in transactions)
        
        return {
            "year": year,
            "total_expenses": total,
            "transaction_count": len(transactions),
            "monthly_expenses": list(monthly_expenses.values()),
            "average_monthly": total / 12,
        }

    async def get_calendar_view(
        self, user_id: UUID, year: int, month: int, workspace_id: Optional[UUID] = None
    ) -> Dict:
        """Obtém visualização de calendário completo do mês"""
        monthly_data = await self.get_monthly_expenses(user_id, year, month, workspace_id)
        
        # Criar estrutura de calendário
        calendar = []
        start_date = datetime(year, month, 1)
        
        # Primeiro dia do mês
        first_weekday = start_date.weekday()
        
        # Dias do mês
        if month == 12:
            last_day = (datetime(year + 1, 1, 1) - timedelta(days=1)).day
        else:
            last_day = (datetime(year, month + 1, 1) - timedelta(days=1)).day
        
        # Criar mapa de despesas por dia
        expenses_by_day = {item["date"]: item for item in monthly_data["daily_expenses"]}
        
        # Construir calendário
        current_date = start_date - timedelta(days=first_weekday)  # Começar do primeiro dia da semana
        
        for week in range(6):  # Máximo 6 semanas
            week_data = []
            for day in range(7):  # 7 dias da semana
                day_date = current_date + timedelta(days=day)
                day_key = day_date.date().isoformat()
                
                day_info = {
                    "date": day_key,
                    "day": day_date.day,
                    "is_current_month": day_date.month == month,
                    "expenses": 0.0,
                    "transaction_count": 0,
                }
                
                if day_key in expenses_by_day:
                    day_info["expenses"] = expenses_by_day[day_key]["total"]
                    day_info["transaction_count"] = expenses_by_day[day_key]["count"]
                
                week_data.append(day_info)
            
            calendar.append(week_data)
            current_date += timedelta(days=7)
            
            # Parar se já passou do último dia do mês
            if current_date.month > month or (current_date.month == month and current_date.day > last_day):
                break
        
        return {
            "year": year,
            "month": month,
            "calendar": calendar,
            "summary": {
                "total_expenses": monthly_data["total_expenses"],
                "transaction_count": monthly_data["transaction_count"],
                "average_daily": monthly_data["average_daily"],
            },
        }

