from typing import Optional, Dict, List
from uuid import UUID
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.goal_repository import GoalRepository
from src.domain.repositories.planning_repository import PlanningRepository


class AIService:
    """Serviço de IA para assistente financeiro"""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        goal_repository: GoalRepository,
        planning_repository: PlanningRepository,
        api_key: Optional[str] = None,
    ):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.goal_repository = goal_repository
        self.planning_repository = planning_repository
        self.api_key = api_key

    async def get_financial_context(self, user_id: UUID) -> Dict:
        """Obtém contexto financeiro do usuário para IA"""
        accounts = await self.account_repository.get_by_user_id(user_id)
        goals = await self.goal_repository.get_by_user_id(user_id)
        plannings = await self.planning_repository.get_by_user_id(user_id)
        
        # Últimas transações
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        transactions = await self.transaction_repository.get_by_user_id(user_id, start_date, end_date)

        total_balance = sum(float(a.balance) for a in accounts if a.is_active)
        active_goals = [g for g in goals if g.status.value == "active"]
        active_plannings = [p for p in plannings if p.is_active]

        return {
            "total_balance": total_balance,
            "accounts_count": len(accounts),
            "active_goals_count": len(active_goals),
            "active_plannings_count": len(active_plannings),
            "recent_transactions_count": len(transactions),
            "accounts": [
                {"name": a.name, "balance": float(a.balance), "type": a.account_type.value}
                for a in accounts[:5]
            ],
            "goals": [
                {
                    "name": g.name,
                    "target": float(g.target_amount),
                    "current": float(g.current_amount),
                    "percentage": float((g.current_amount / g.target_amount) * 100) if g.target_amount > 0 else 0,
                }
                for g in active_goals[:5]
            ],
        }

    async def chat(
        self, user_id: UUID, message: str, conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Processa mensagem do usuário e retorna resposta da IA
        
        Args:
            user_id: ID do usuário
            message: Mensagem do usuário
            conversation_history: Histórico da conversa
        
        Returns:
            Dict com resposta da IA
        """
        # Obter contexto financeiro
        context = await self.get_financial_context(user_id)

        # Preparar prompt com contexto
        system_prompt = f"""Você é um assistente financeiro pessoal especializado em ajudar pessoas a gerenciar suas finanças.

Contexto do usuário:
- Saldo total: R$ {context['total_balance']:,.2f}
- Contas ativas: {context['accounts_count']}
- Metas ativas: {context['active_goals_count']}
- Planejamentos ativos: {context['active_plannings_count']}

Seja útil, claro e objetivo. Responda em português brasileiro."""

        # Se não tiver API key, retornar resposta simulada
        if not self.api_key:
            return await self._simulate_response(message, context)

        # TODO: Integrar com OpenAI ou Claude
        # Por enquanto, retornar resposta simulada
        return await self._simulate_response(message, context)

    async def _simulate_response(self, message: str, context: Dict) -> Dict:
        """Simula resposta da IA (para desenvolvimento)"""
        message_lower = message.lower()

        if "saldo" in message_lower or "quanto tenho" in message_lower:
            return {
                "response": f"Seu saldo total é R$ {context['total_balance']:,.2f}.",
                "suggestions": ["Ver detalhes das contas", "Adicionar transação"],
            }

        if "meta" in message_lower or "objetivo" in message_lower:
            goals_text = "\n".join(
                [
                    f"- {g['name']}: {g['percentage']:.1f}% (R$ {g['current']:,.2f} / R$ {g['target']:,.2f})"
                    for g in context.get("goals", [])
                ]
            )
            return {
                "response": f"Você tem {context['active_goals_count']} metas ativas:\n{goals_text}",
                "suggestions": ["Ver todas as metas", "Criar nova meta"],
            }

        if "posso comprar" in message_lower or "posso gastar" in message_lower:
            return {
                "response": f"Com base no seu saldo atual de R$ {context['total_balance']:,.2f}, você tem disponibilidade. Mas lembre-se de considerar seus planejamentos e metas!",
                "suggestions": ["Ver planejamentos", "Verificar metas"],
            }

        # Resposta genérica
        return {
            "response": "Entendi sua pergunta. Estou aqui para ajudar com suas finanças. Você pode me perguntar sobre saldo, metas, planejamentos ou transações.",
            "suggestions": ["Ver saldo", "Ver metas", "Ver planejamentos"],
        }

    async def get_suggestions(self, user_id: UUID) -> List[str]:
        """Gera sugestões automáticas baseadas no contexto"""
        context = await self.get_financial_context(user_id)
        suggestions = []

        if context["total_balance"] < 0:
            suggestions.append("⚠️ Seu saldo está negativo. Considere revisar seus gastos.")

        if context["active_goals_count"] == 0:
            suggestions.append("💡 Crie uma meta para começar a economizar!")

        if context["active_plannings_count"] == 0:
            suggestions.append("📊 Crie um planejamento para controlar melhor seus gastos.")

        return suggestions

