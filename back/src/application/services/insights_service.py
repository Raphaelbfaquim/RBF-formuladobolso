from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.category_repository import CategoryRepository


class InsightsService:
    """Serviço de insights automáticos"""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        category_repository: CategoryRepository,
    ):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.category_repository = category_repository

    async def generate_insights(self, user_id: UUID, days: int = 30) -> List[Dict]:
        """Gera insights automáticos baseados em padrões"""
        insights = []

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Obter transações do período
        current_transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        # Período anterior para comparação
        previous_start = start_date - timedelta(days=days)
        previous_transactions = await self.transaction_repository.get_by_user_id(
            user_id, previous_start, start_date
        )

        # Insight 1: Comparação de gastos
        current_expenses = sum(
            float(t.amount) for t in current_transactions
            if t.transaction_type.value == "expense" and t.status.value == "completed"
        )
        previous_expenses = sum(
            float(t.amount) for t in previous_transactions
            if t.transaction_type.value == "expense" and t.status.value == "completed"
        )

        if previous_expenses > 0:
            change_percentage = ((current_expenses - previous_expenses) / previous_expenses) * 100
            if abs(change_percentage) > 10:
                insights.append({
                    "type": "spending_change",
                    "title": "Mudança nos Gastos",
                    "message": f"Seus gastos {'aumentaram' if change_percentage > 0 else 'diminuíram'} {abs(change_percentage):.1f}% em relação ao período anterior.",
                    "severity": "warning" if change_percentage > 0 else "info",
                    "value": change_percentage,
                })

        # Insight 2: Categoria com maior gasto
        expenses_by_category = defaultdict(float)
        for t in current_transactions:
            if t.transaction_type.value == "expense" and t.category:
                expenses_by_category[t.category.name] += float(t.amount)

        if expenses_by_category:
            top_category = max(expenses_by_category.items(), key=lambda x: x[1])
            total_expenses = sum(expenses_by_category.values())
            percentage = (top_category[1] / total_expenses) * 100

            if percentage > 30:
                insights.append({
                    "type": "top_category",
                    "title": "Categoria com Maior Gasto",
                    "message": f"{top_category[0]} representa {percentage:.1f}% dos seus gastos ({top_category[1]:,.2f}).",
                    "severity": "info",
                    "category": top_category[0],
                    "amount": top_category[1],
                })

        # Insight 3: Padrão de dias da semana
        expenses_by_weekday = defaultdict(float)
        for t in current_transactions:
            if t.transaction_type.value == "expense":
                weekday = t.transaction_date.weekday()
                expenses_by_weekday[weekday] += float(t.amount)

        if expenses_by_weekday:
            max_weekday = max(expenses_by_weekday.items(), key=lambda x: x[1])
            weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            insights.append({
                "type": "spending_pattern",
                "title": "Padrão de Gastos",
                "message": f"Você gasta mais às {weekday_names[max_weekday[0]]}s (R$ {max_weekday[1]:,.2f}).",
                "severity": "info",
                "weekday": weekday_names[max_weekday[0]],
            })

        # Insight 4: Transações recorrentes detectadas
        # Agrupar por descrição similar
        description_groups = defaultdict(list)
        for t in current_transactions:
            if t.transaction_type.value == "expense":
                # Normalizar descrição (remover números, espaços extras)
                normalized = " ".join(t.description.lower().split())
                description_groups[normalized].append(t)

        recurring = []
        for desc, transactions in description_groups.items():
            if len(transactions) >= 3:  # Pelo menos 3 ocorrências
                total = sum(float(t.amount) for t in transactions)
                recurring.append({
                    "description": desc,
                    "count": len(transactions),
                    "total": total,
                    "average": total / len(transactions),
                })

        if recurring:
            top_recurring = max(recurring, key=lambda x: x["total"])
            insights.append({
                "type": "recurring_expense",
                "title": "Despesa Recorrente Detectada",
                "message": f"'{top_recurring['description']}' aparece {top_recurring['count']} vezes (total: R$ {top_recurring['total']:,.2f}).",
                "severity": "info",
                "expense": top_recurring,
            })

        return insights

    async def get_spending_trends(self, user_id: UUID, months: int = 6) -> Dict:
        """Analisa tendências de gastos"""
        trends = {
            "monthly_expenses": [],
            "monthly_income": [],
            "trend": "stable",  # increasing, decreasing, stable
        }

        end_date = datetime.now()
        for i in range(months):
            month_start = (end_date - timedelta(days=30 * (i + 1))).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

            transactions = await self.transaction_repository.get_by_user_id(
                user_id, month_start, month_end
            )

            expenses = sum(
                float(t.amount) for t in transactions
                if t.transaction_type.value == "expense" and t.status.value == "completed"
            )
            income = sum(
                float(t.amount) for t in transactions
                if t.transaction_type.value == "income" and t.status.value == "completed"
            )

            trends["monthly_expenses"].append({
                "month": month_start.strftime("%Y-%m"),
                "amount": expenses,
            })
            trends["monthly_income"].append({
                "month": month_start.strftime("%Y-%m"),
                "amount": income,
            })

        # Determinar tendência
        if len(trends["monthly_expenses"]) >= 2:
            recent = trends["monthly_expenses"][0]["amount"]
            previous = trends["monthly_expenses"][1]["amount"]
            change = ((recent - previous) / previous * 100) if previous > 0 else 0

            if change > 5:
                trends["trend"] = "increasing"
            elif change < -5:
                trends["trend"] = "decreasing"

        return trends

    async def get_category_analysis(self, user_id: UUID, days: int = 30) -> Dict:
        """Análise detalhada por categoria"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        category_data = defaultdict(lambda: {"amount": 0.0, "count": 0, "transactions": []})
        
        for t in transactions:
            if t.transaction_type.value == "expense" and t.status.value == "completed" and t.category:
                cat_name = t.category.name
                category_data[cat_name]["amount"] += float(t.amount)
                category_data[cat_name]["count"] += 1
                category_data[cat_name]["transactions"].append({
                    "id": str(t.id),
                    "amount": float(t.amount),
                    "date": t.transaction_date.isoformat(),
                    "description": t.description,
                })

        total_expenses = sum(data["amount"] for data in category_data.values())
        
        categories = []
        for name, data in category_data.items():
            percentage = (data["amount"] / total_expenses * 100) if total_expenses > 0 else 0
            categories.append({
                "name": name,
                "amount": data["amount"],
                "count": data["count"],
                "percentage": percentage,
                "average": data["amount"] / data["count"] if data["count"] > 0 else 0,
            })

        categories.sort(key=lambda x: x["amount"], reverse=True)

        return {
            "categories": categories,
            "total_expenses": total_expenses,
            "period_days": days,
        }

    async def get_spending_patterns(self, user_id: UUID, days: int = 30) -> Dict:
        """Detecta padrões de gastos"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        expenses = [t for t in transactions if t.transaction_type.value == "expense" and t.status.value == "completed"]

        # Por dia da semana
        weekday_expenses = defaultdict(float)
        for t in expenses:
            weekday = t.transaction_date.weekday()
            weekday_expenses[weekday] += float(t.amount)

        weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        weekday_data = [
            {"day": weekday_names[i], "amount": weekday_expenses[i]}
            for i in range(7)
        ]

        # Por hora do dia (se disponível)
        hour_expenses = defaultdict(float)
        for t in expenses:
            hour = t.transaction_date.hour
            hour_expenses[hour] += float(t.amount)

        hour_data = [
            {"hour": f"{i:02d}:00", "amount": hour_expenses[i]}
            for i in range(24)
        ]

        return {
            "by_weekday": weekday_data,
            "by_hour": hour_data,
        }

    async def get_recommendations(self, user_id: UUID, days: int = 30) -> List[Dict]:
        """Gera recomendações personalizadas"""
        recommendations = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        expenses = [t for t in transactions if t.transaction_type.value == "expense" and t.status.value == "completed"]
        income = [t for t in transactions if t.transaction_type.value == "income" and t.status.value == "completed"]

        total_expenses = sum(float(t.amount) for t in expenses)
        total_income = sum(float(t.amount) for t in income)

        # Recomendação 1: Taxa de economia
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            if savings_rate < 10:
                recommendations.append({
                    "type": "savings_rate",
                    "title": "Taxa de Economia Baixa",
                    "message": f"Sua taxa de economia está em {savings_rate:.1f}%. Recomendamos economizar pelo menos 20% da renda.",
                    "severity": "warning",
                    "action": "Criar meta de economia",
                })

        # Recomendação 2: Gastos por categoria
        category_expenses = defaultdict(float)
        for t in expenses:
            if t.category:
                category_expenses[t.category.name] += float(t.amount)

        if category_expenses:
            top_category = max(category_expenses.items(), key=lambda x: x[1])
            total = sum(category_expenses.values())
            percentage = (top_category[1] / total * 100) if total > 0 else 0

            if percentage > 40:
                recommendations.append({
                    "type": "category_concentration",
                    "title": "Concentração de Gastos",
                    "message": f"{top_category[0]} representa {percentage:.1f}% dos seus gastos. Considere diversificar ou reduzir.",
                    "severity": "info",
                    "category": top_category[0],
                })

        # Recomendação 3: Comparação com período anterior
        previous_start = start_date - timedelta(days=days)
        previous_transactions = await self.transaction_repository.get_by_user_id(
            user_id, previous_start, start_date
        )
        previous_expenses = sum(
            float(t.amount) for t in previous_transactions
            if t.transaction_type.value == "expense" and t.status.value == "completed"
        )

        if previous_expenses > 0:
            change = ((total_expenses - previous_expenses) / previous_expenses) * 100
            if change > 20:
                recommendations.append({
                    "type": "spending_increase",
                    "title": "Aumento Significativo de Gastos",
                    "message": f"Seus gastos aumentaram {change:.1f}% em relação ao período anterior. Revise suas despesas.",
                    "severity": "warning",
                    "change_percentage": change,
                })

        return recommendations

    async def get_summary(self, user_id: UUID, days: int = 30) -> Dict:
        """Resumo completo de insights"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        expenses = [t for t in transactions if t.transaction_type.value == "expense" and t.status.value == "completed"]
        income = [t for t in transactions if t.transaction_type.value == "income" and t.status.value == "completed"]

        total_expenses = sum(float(t.amount) for t in expenses)
        total_income = sum(float(t.amount) for t in income)
        savings = total_income - total_expenses
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0

        # Média diária
        avg_daily_expense = total_expenses / days if days > 0 else 0
        avg_daily_income = total_income / days if days > 0 else 0

        # Transações
        expense_count = len(expenses)
        income_count = len(income)

        return {
            "period_days": days,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "savings": savings,
            "savings_rate": savings_rate,
            "avg_daily_income": avg_daily_income,
            "avg_daily_expense": avg_daily_expense,
            "expense_count": expense_count,
            "income_count": income_count,
            "total_transactions": len(transactions),
        }

