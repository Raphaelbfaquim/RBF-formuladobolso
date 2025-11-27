from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository


class PredictionService:
    """Serviço de previsões financeiras com IA"""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository

    async def predict_balance(
        self, user_id: UUID, account_id: UUID, days: int = 30
    ) -> Dict:
        """
        Previsão de saldo futuro
        
        Args:
            user_id: ID do usuário
            account_id: ID da conta
            days: Dias à frente para prever
        
        Returns:
            Dict com previsões
        """
        account = await self.account_repository.get_by_id(account_id)
        if not account:
            return {"error": "Conta não encontrada"}

        # Obter histórico de transações
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 3 meses de histórico

        transactions = await self.transaction_repository.get_by_account_id(
            account_id, start_date, end_date
        )

        # Calcular médias
        income_transactions = [
            t for t in transactions
            if t.transaction_type.value == "income" and t.status.value == "completed"
        ]
        expense_transactions = [
            t for t in transactions
            if t.transaction_type.value == "expense" and t.status.value == "completed"
        ]

        # Média diária
        days_history = (end_date - start_date).days
        avg_daily_income = (
            sum(float(t.amount) for t in income_transactions) / days_history
            if days_history > 0
            else 0
        )
        avg_daily_expense = (
            sum(float(t.amount) for t in expense_transactions) / days_history
            if days_history > 0
            else 0
        )

        # Previsão
        current_balance = float(account.balance)
        predicted_balance = current_balance + (avg_daily_income - avg_daily_expense) * days

        # Cenários
        optimistic_balance = current_balance + (avg_daily_income * 1.1 - avg_daily_expense * 0.9) * days
        pessimistic_balance = current_balance + (avg_daily_income * 0.9 - avg_daily_expense * 1.1) * days

        return {
            "current_balance": current_balance,
            "predicted_balance": predicted_balance,
            "optimistic_balance": optimistic_balance,
            "pessimistic_balance": pessimistic_balance,
            "days": days,
            "avg_daily_income": avg_daily_income,
            "avg_daily_expense": avg_daily_expense,
            "prediction_date": (datetime.now() + timedelta(days=days)).isoformat(),
        }

    async def simulate_purchase(
        self, user_id: UUID, account_id: UUID, amount: Decimal, description: str = ""
    ) -> Dict:
        """
        Simula uma compra e mostra impacto
        
        Args:
            user_id: ID do usuário
            account_id: ID da conta
            amount: Valor da compra
            description: Descrição da compra
        
        Returns:
            Dict com simulação
        """
        account = await self.account_repository.get_by_id(account_id)
        if not account:
            return {"error": "Conta não encontrada"}

        current_balance = float(account.balance)
        new_balance = current_balance - float(amount)

        # Verificar planejamentos ativos
        # TODO: Integrar com planejamentos para verificar impacto

        # Previsão de saldo futuro considerando a compra
        prediction = await self.predict_balance(user_id, account_id, 30)

        return {
            "current_balance": current_balance,
            "purchase_amount": float(amount),
            "new_balance": new_balance,
            "can_afford": new_balance >= 0,
            "impact_on_future": {
                "balance_in_30_days": prediction.get("predicted_balance", 0) - float(amount),
                "optimistic": prediction.get("optimistic_balance", 0) - float(amount),
                "pessimistic": prediction.get("pessimistic_balance", 0) - float(amount),
            },
            "recommendation": self._get_purchase_recommendation(new_balance, prediction),
        }

    def _get_purchase_recommendation(self, new_balance: float, prediction: Dict) -> str:
        """Gera recomendação sobre a compra"""
        if new_balance < 0:
            return "⚠️ Esta compra deixaria seu saldo negativo. Não recomendado."
        
        if new_balance < 100:
            return "⚠️ Esta compra deixaria seu saldo muito baixo. Considere esperar."
        
        pessimistic = prediction.get("pessimistic_balance", 0)
        if pessimistic < 0:
            return "⚠️ Esta compra pode deixar seu saldo negativo em cenários pessimistas."
        
        return "✅ Você pode fazer esta compra com segurança."

    async def calculate_savings_goal(
        self, user_id: UUID, target_amount: Decimal, months: int
    ) -> Dict:
        """
        Calcula quanto precisa economizar por mês para alcançar uma meta
        
        Args:
            user_id: ID do usuário
            target_amount: Valor da meta
            months: Meses para alcançar
        
        Returns:
            Dict com cálculo
        """
        # Obter histórico de receitas e despesas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        total_income = sum(
            float(t.amount) for t in transactions
            if t.transaction_type.value == "income" and t.status.value == "completed"
        )
        total_expense = sum(
            float(t.amount) for t in transactions
            if t.transaction_type.value == "expense" and t.status.value == "completed"
        )

        avg_monthly_income = total_income / 3
        avg_monthly_expense = total_expense / 3
        current_savings_rate = avg_monthly_income - avg_monthly_expense

        monthly_savings_needed = float(target_amount) / months
        additional_savings_needed = monthly_savings_needed - current_savings_rate

        return {
            "target_amount": float(target_amount),
            "months": months,
            "monthly_savings_needed": monthly_savings_needed,
            "current_monthly_savings": current_savings_rate,
            "additional_savings_needed": max(0, additional_savings_needed),
            "can_achieve": current_savings_rate >= monthly_savings_needed,
            "recommendations": self._get_savings_recommendations(
                current_savings_rate, monthly_savings_needed
            ),
        }

    def _get_savings_recommendations(
        self, current_savings: float, needed_savings: float
    ) -> List[str]:
        """Gera recomendações para alcançar meta de economia"""
        recommendations = []

        if current_savings < needed_savings:
            deficit = needed_savings - current_savings
            recommendations.append(
                f"Você precisa economizar R$ {deficit:,.2f} a mais por mês."
            )
            recommendations.append("Considere reduzir despesas não essenciais.")
            recommendations.append("Procure aumentar sua renda se possível.")
        else:
            recommendations.append("✅ Você está no caminho certo!")
            recommendations.append(
                f"Continue economizando R$ {current_savings:,.2f} por mês."
            )

        return recommendations

