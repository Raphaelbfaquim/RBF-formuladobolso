from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
from src.domain.repositories.transaction_repository import TransactionRepository


class HabitAnalysisService:
    """Serviço de análise de hábitos de consumo"""

    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    async def analyze_consumption_habits(self, user_id: UUID, days: int = 90) -> Dict:
        """Analisa hábitos de consumo do usuário"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        expenses = [
            t for t in transactions
            if t.transaction_type.value == "expense" and t.status.value == "completed"
        ]

        # Análise por dia da semana
        expenses_by_weekday = defaultdict(float)
        for t in expenses:
            weekday = t.transaction_date.weekday()
            expenses_by_weekday[weekday] += float(t.amount)

        # Análise por dia do mês
        expenses_by_day = defaultdict(float)
        for t in expenses:
            day = t.transaction_date.day
            expenses_by_day[day] += float(t.amount)

        # Análise por horário (se disponível)
        expenses_by_hour = defaultdict(float)
        for t in expenses:
            hour = t.transaction_date.hour
            expenses_by_hour[hour] += float(t.amount)

        # Identificar padrões
        patterns = []

        # Padrão: Gasta mais em determinado dia da semana
        if expenses_by_weekday:
            max_weekday = max(expenses_by_weekday.items(), key=lambda x: x[1])
            weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            patterns.append({
                "type": "weekday_pattern",
                "description": f"Você gasta mais às {weekday_names[max_weekday[0]]}s",
                "value": max_weekday[1],
            })

        # Padrão: Gasta mais no início/fim do mês
        first_half = sum(v for k, v in expenses_by_day.items() if k <= 15)
        second_half = sum(v for k, v in expenses_by_day.items() if k > 15)
        
        if first_half > second_half * 1.2:
            patterns.append({
                "type": "month_pattern",
                "description": "Você gasta mais no início do mês",
                "value": first_half,
            })
        elif second_half > first_half * 1.2:
            patterns.append({
                "type": "month_pattern",
                "description": "Você gasta mais no final do mês",
                "value": second_half,
            })

        return {
            "analysis_period_days": days,
            "total_expenses": sum(float(t.amount) for t in expenses),
            "expenses_by_weekday": dict(expenses_by_weekday),
            "expenses_by_day_of_month": dict(expenses_by_day),
            "expenses_by_hour": dict(expenses_by_hour),
            "patterns": patterns,
            "recommendations": self._generate_recommendations(patterns, expenses_by_weekday),
        }

    def _generate_recommendations(
        self, patterns: List[Dict], expenses_by_weekday: Dict
    ) -> List[str]:
        """Gera recomendações baseadas nos padrões"""
        recommendations = []

        for pattern in patterns:
            if pattern["type"] == "weekday_pattern":
                recommendations.append(
                    "💡 Considere fazer compras em dias com menor movimento para evitar gastos por impulso."
                )
            elif pattern["type"] == "month_pattern":
                if "início" in pattern["description"]:
                    recommendations.append(
                        "💡 Você gasta muito no início do mês. Considere fazer um planejamento mais rigoroso."
                    )
                else:
                    recommendations.append(
                        "💡 Você gasta muito no final do mês. Pode ser útil reservar uma parte do salário no início."
                    )

        return recommendations

    async def compare_with_average(self, user_id: UUID, category: Optional[str] = None) -> Dict:
        """Compara gastos do usuário com média (simulada)"""
        # TODO: Implementar comparação com dados agregados reais
        return {
            "user_average": 0.0,
            "market_average": 0.0,
            "difference_percentage": 0.0,
            "message": "Comparação com média em desenvolvimento",
        }

