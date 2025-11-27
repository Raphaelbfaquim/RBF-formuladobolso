from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories.planning_repository import PlanningRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.user_repository import UserRepository
from src.application.notifications.notification_service import NotificationService
from src.application.use_cases.planning_use_cases import PlanningUseCases
from src.shared.exceptions import NotFoundException


class NotificationUseCases:
    """Casos de uso para notificações de planejamento"""

    def __init__(
        self,
        planning_repository: PlanningRepository,
        transaction_repository: TransactionRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
        planning_use_cases: PlanningUseCases,
    ):
        self.planning_repository = planning_repository
        self.transaction_repository = transaction_repository
        self.user_repository = user_repository
        self.notification_service = notification_service
        self.planning_use_cases = planning_use_cases

    async def check_and_notify_planning(
        self,
        planning_id: UUID,
        threshold: float = 10.0,
        force_notification: bool = False,
    ) -> dict:
        """
        Verifica planejamento e envia notificações se necessário
        
        Args:
            planning_id: ID do planejamento
            threshold: Limite de tolerância em porcentagem
            force_notification: Forçar envio mesmo se não atender critérios
        
        Returns:
            dict com resultado da verificação e notificações
        """
        # Obter planejamento
        planning = await self.planning_repository.get_by_id(planning_id)
        if not planning:
            raise NotFoundException("Planejamento", str(planning_id))

        # Obter usuário
        user = await self.user_repository.get_by_id(planning.user_id)
        if not user:
            raise NotFoundException("Usuário", str(planning.user_id))

        # Calcular progresso
        progress = await self.planning_use_cases.calculate_planning_progress(planning_id)

        percentage = progress["percentage"]
        target_amount = progress["target_amount"]
        actual_amount = progress["actual_amount"]

        # Verificar se deve enviar notificação
        should_notify = (
            force_notification
            or self.notification_service.should_send_notification(percentage, threshold)
        )

        if not should_notify:
            return {
                "notified": False,
                "reason": "Não atende critérios para notificação",
                "percentage": percentage,
            }

        # Obter número de telefone do usuário (se disponível)
        # TODO: Adicionar campo phone_number no modelo User
        phone_number = getattr(user, "phone_number", None)

        # Enviar notificações
        notification_result = await self.notification_service.send_planning_notification(
            user_email=user.email,
            user_name=user.full_name or user.username,
            phone_number=phone_number,
            planning_name=planning.name,
            target_amount=target_amount,
            actual_amount=actual_amount,
            percentage=percentage,
            threshold=threshold,
        )

        return {
            "notified": True,
            "notification_result": notification_result,
            "percentage": percentage,
            "is_over_budget": progress["is_on_track"] is False,
            "is_on_track": progress["is_on_track"],
        }

    async def check_all_active_plannings(
        self, threshold: float = 10.0
    ) -> List[dict]:
        """
        Verifica todos os planejamentos ativos e envia notificações
        
        Args:
            threshold: Limite de tolerância em porcentagem
        
        Returns:
            Lista com resultados de cada verificação
        """
        # Obter todos os planejamentos ativos
        # TODO: Implementar método get_all_active no repositório
        # Por enquanto, vamos buscar por usuários conhecidos
        results = []

        # Esta é uma implementação simplificada
        # Em produção, você deve ter um método para buscar todos os planejamentos ativos
        # ou iterar por usuários e seus planejamentos

        return results

