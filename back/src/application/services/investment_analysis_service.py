from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
import pytz
from src.domain.repositories.investment_repository import (
    InvestmentAccountRepository,
    InvestmentTransactionRepository,
)
from src.infrastructure.database.models.investment import (
    InvestmentAccount,
    InvestmentTransaction,
    InvestmentTransactionType,
    InvestmentType,
)


class InvestmentAnalysisService:
    """Serviço de análise avançada de investimentos"""

    def __init__(
        self,
        account_repository: InvestmentAccountRepository,
        transaction_repository: InvestmentTransactionRepository,
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository

    async def calculate_portfolio_performance(
        self, user_id: UUID, period_days: int = 365
    ) -> Dict:
        """Calcula performance da carteira"""
        accounts = await self.account_repository.get_by_user_id(user_id)
        end_date = datetime.now(pytz.UTC)
        start_date = end_date - timedelta(days=period_days)

        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        total_invested = Decimal("0")
        current_value = Decimal("0")

        # Calcular total investido (compras - vendas)
        for transaction in transactions:
            if transaction.transaction_type == InvestmentTransactionType.BUY:
                total_invested += transaction.total_amount + transaction.fees
            elif transaction.transaction_type == InvestmentTransactionType.SELL:
                total_invested -= transaction.total_amount - transaction.fees
            elif transaction.transaction_type in [
                InvestmentTransactionType.DIVIDEND,
                InvestmentTransactionType.INTEREST,
            ]:
                current_value += transaction.total_amount

        # Valor atual = saldo das contas
        for account in accounts:
            if account.is_active:
                current_value += account.current_balance

        total_return = current_value - total_invested
        return_percentage = (
            float((total_return / total_invested * 100) if total_invested > 0 else 0)
        )

        return {
            "total_invested": float(total_invested),
            "current_value": float(current_value),
            "return_percentage": return_percentage,
            "return_amount": float(total_return),
            "transactions_count": len(transactions),
        }

    async def get_portfolio_summary(self, user_id: UUID) -> Dict:
        """Resumo completo da carteira"""
        accounts = await self.account_repository.get_by_user_id(user_id)
        now = datetime.now(pytz.UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        all_transactions = await self.transaction_repository.get_by_user_id(user_id)

        # Calcular totais
        total_invested = Decimal("0")
        current_value = Decimal("0")

        for account in accounts:
            if account.is_active:
                current_value += account.current_balance

        # Calcular investido (compras - vendas)
        for transaction in all_transactions:
            if transaction.transaction_type == InvestmentTransactionType.BUY:
                total_invested += transaction.total_amount + transaction.fees
            elif transaction.transaction_type == InvestmentTransactionType.SELL:
                total_invested -= transaction.total_amount - transaction.fees

        total_return = current_value - total_invested
        return_percentage = (
            float((total_return / total_invested * 100) if total_invested > 0 else 0)
        )

        # Variações
        day_transactions = [
            t for t in all_transactions if t.transaction_date >= today_start
        ]
        month_transactions = [
            t for t in all_transactions if t.transaction_date >= month_start
        ]
        year_transactions = [
            t for t in all_transactions if t.transaction_date >= year_start
        ]

        day_variation = self._calculate_variation(day_transactions)
        month_variation = self._calculate_variation(month_transactions)
        year_variation = self._calculate_variation(year_transactions)

        # Distribuição por tipo
        distribution_by_type = defaultdict(Decimal)
        for transaction in all_transactions:
            if transaction.transaction_type == InvestmentTransactionType.BUY:
                distribution_by_type[transaction.investment_type.value] += (
                    transaction.total_amount + transaction.fees
                )

        # Distribuição por conta
        distribution_by_account = {}
        for account in accounts:
            if account.is_active:
                distribution_by_account[account.name] = float(account.current_balance)

        return {
            "total_accounts": len([a for a in accounts if a.is_active]),
            "total_invested": float(total_invested),
            "current_value": float(current_value),
            "total_return": float(total_return),
            "return_percentage": return_percentage,
            "day_variation": float(day_variation),
            "day_variation_percentage": (
                float((day_variation / current_value * 100) if current_value > 0 else 0)
            ),
            "month_variation": float(month_variation),
            "month_variation_percentage": (
                float(
                    (month_variation / current_value * 100) if current_value > 0 else 0
                )
            ),
            "year_variation": float(year_variation),
            "year_variation_percentage": (
                float(
                    (year_variation / current_value * 100) if current_value > 0 else 0
                )
            ),
            "distribution_by_type": {
                k: float(v) for k, v in distribution_by_type.items()
            },
            "distribution_by_account": distribution_by_account,
        }

    def _calculate_variation(self, transactions: List[InvestmentTransaction]) -> Decimal:
        """Calcula variação baseada em transações"""
        variation = Decimal("0")
        for transaction in transactions:
            if transaction.transaction_type == InvestmentTransactionType.BUY:
                variation -= transaction.total_amount + transaction.fees
            elif transaction.transaction_type == InvestmentTransactionType.SELL:
                variation += transaction.total_amount - transaction.fees
            elif transaction.transaction_type in [
                InvestmentTransactionType.DIVIDEND,
                InvestmentTransactionType.INTEREST,
            ]:
                variation += transaction.total_amount
            elif transaction.transaction_type == InvestmentTransactionType.FEE:
                variation -= transaction.total_amount
        return variation

    async def get_diversification(self, user_id: UUID) -> Dict:
        """Análise de diversificação"""
        accounts = await self.account_repository.get_by_user_id(user_id)
        transactions = await self.transaction_repository.get_by_user_id(user_id)

        by_type = defaultdict(Decimal)
        by_account = defaultdict(Decimal)
        by_institution = defaultdict(Decimal)

        for transaction in transactions:
            if transaction.transaction_type == InvestmentTransactionType.BUY:
                by_type[transaction.investment_type.value] += (
                    transaction.total_amount + transaction.fees
                )
                by_account[transaction.account.name] += (
                    transaction.total_amount + transaction.fees
                )
                if transaction.account.institution_name:
                    by_institution[transaction.account.institution_name] += (
                        transaction.total_amount + transaction.fees
                    )

        recommendations = []
        total = sum(by_type.values())
        if total > 0:
            # Verificar concentração
            for inv_type, amount in by_type.items():
                percentage = float((amount / total) * 100)
                if percentage > 50:
                    recommendations.append(
                        f"Alta concentração em {inv_type} ({percentage:.1f}%). Considere diversificar."
                    )

        return {
            "by_type": {k: float(v) for k, v in by_type.items()},
            "by_account": {k: float(v) for k, v in by_account.items()},
            "by_institution": {k: float(v) for k, v in by_institution.items()},
            "recommendations": recommendations,
        }

    async def simulate_investment(
        self,
        initial_amount: Decimal,
        monthly_contribution: Decimal,
        annual_rate: float,
        period_months: int,
        inflation_rate: float = 0,
    ) -> Dict:
        """Simula um investimento"""
        monthly_rate = annual_rate / 12 / 100
        monthly_inflation = inflation_rate / 12 / 100

        current_amount = initial_amount
        total_contributed = initial_amount
        monthly_breakdown = []

        for month in range(1, period_months + 1):
            # Aplicar rendimento
            current_amount *= Decimal(str(1 + monthly_rate))
            # Adicionar aporte
            if monthly_contribution > 0:
                current_amount += monthly_contribution
                total_contributed += monthly_contribution
            # Aplicar inflação (descontar)
            if inflation_rate > 0:
                current_amount /= Decimal(str(1 + monthly_inflation))

            monthly_breakdown.append({
                "month": month,
                "amount": float(current_amount),
                "contributed": float(total_contributed),
            })

        final_amount = current_amount
        total_return = final_amount - total_contributed
        return_percentage = float(
            (total_return / total_contributed * 100) if total_contributed > 0 else 0
        )

        return {
            "initial_amount": float(initial_amount),
            "total_contributed": float(total_contributed),
            "final_amount": float(final_amount),
            "total_return": float(total_return),
            "return_percentage": return_percentage,
            "monthly_breakdown": monthly_breakdown,
        }

    async def calculate_taxes(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Calcula impostos sobre investimentos"""
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        total_gain = Decimal("0")
        taxable_transactions = []

        for transaction in transactions:
            if transaction.transaction_type == InvestmentTransactionType.SELL:
                # Calcular ganho de capital (simplificado)
                # Em produção, precisaria calcular PM (preço médio)
                gain = transaction.total_amount - transaction.fees
                total_gain += gain
                taxable_transactions.append({
                    "id": str(transaction.id),
                    "date": transaction.transaction_date.isoformat(),
                    "symbol": transaction.symbol,
                    "amount": float(gain),
                })
            elif transaction.transaction_type in [
                InvestmentTransactionType.DIVIDEND,
                InvestmentTransactionType.INTEREST,
            ]:
                # Dividendos e juros são tributáveis
                total_gain += transaction.total_amount
                taxable_transactions.append({
                    "id": str(transaction.id),
                    "date": transaction.transaction_date.isoformat(),
                    "symbol": transaction.symbol,
                    "amount": float(transaction.total_amount),
                })

        # Calcular imposto (15% sobre ganhos acima de R$ 20.000/mês)
        # Simplificado - em produção precisa considerar isenções e tabela progressiva
        taxable_amount = max(Decimal("0"), total_gain - Decimal("20000"))
        tax_rate = 0.15  # 15%
        tax_amount = taxable_amount * Decimal(str(tax_rate))

        return {
            "total_gain": float(total_gain),
            "taxable_amount": float(taxable_amount),
            "tax_amount": float(tax_amount),
            "tax_rate": tax_rate * 100,
            "transactions": taxable_transactions,
        }

