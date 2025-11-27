from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from src.domain.repositories.goal_repository import GoalRepository, GoalContributionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.calendar_repository import CalendarEventRepository
from src.application.services.calendar_event_service import CalendarEventService
from src.infrastructure.database.models.goal import Goal, GoalContribution, GoalType, GoalStatus
from src.shared.exceptions import NotFoundException, ValidationException


class GoalUseCases:
    """Casos de uso para gerenciamento de metas"""

    def __init__(
        self,
        goal_repository: GoalRepository,
        contribution_repository: GoalContributionRepository,
        account_repository: AccountRepository,
        calendar_event_repository: Optional[CalendarEventRepository] = None,
    ):
        self.goal_repository = goal_repository
        self.contribution_repository = contribution_repository
        self.account_repository = account_repository
        self.calendar_event_service = (
            CalendarEventService(calendar_event_repository) if calendar_event_repository else None
        )

    async def create_goal(
        self,
        name: str,
        goal_type: str,
        target_amount: Decimal,
        user_id: UUID,
        description: Optional[str] = None,
        target_date: Optional[datetime] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        savings_category_id: Optional[UUID] = None,
        auto_contribution_percentage: Optional[Decimal] = None,
    ) -> Goal:
        """Cria uma nova meta"""
        try:
            GoalType(goal_type)
        except ValueError:
            raise ValidationException(f"Tipo de meta inválido: {goal_type}")

        goal = Goal(
            name=name,
            description=description,
            goal_type=GoalType(goal_type),
            target_amount=target_amount,
            current_amount=Decimal("0"),
            target_date=target_date,
            status=GoalStatus.ACTIVE,
            icon=icon,
            color=color,
            user_id=user_id,
            savings_category_id=savings_category_id,
            auto_contribution_percentage=auto_contribution_percentage,
        )

        goal = await self.goal_repository.create(goal)

        # Criar evento do calendário se tiver data objetivo
        if target_date and self.calendar_event_service:
            try:
                await self.calendar_event_service.create_goal_event(
                    goal_id=goal.id,
                    name=name,
                    target_date=target_date,
                    user_id=user_id,
                    workspace_id=None,  # Metas são pessoais por padrão
                )
            except Exception as e:
                print(f"[DEBUG] Erro ao criar evento de calendário para meta: {e}")

        return goal

    async def get_goal(self, goal_id: UUID) -> Goal:
        """Obtém uma meta por ID"""
        goal = await self.goal_repository.get_by_id(goal_id)
        if not goal:
            raise NotFoundException("Meta", str(goal_id))
        return goal

    async def get_user_goals(self, user_id: UUID) -> List[Goal]:
        """Obtém todas as metas de um usuário"""
        return await self.goal_repository.get_by_user_id(user_id)

    async def add_contribution(
        self,
        goal_id: UUID,
        amount: Decimal,
        contribution_date: datetime,
        notes: Optional[str] = None,
        transaction_id: Optional[UUID] = None,
    ) -> GoalContribution:
        """Adiciona uma contribuição para a meta"""
        goal = await self.get_goal(goal_id)

        if goal.status != GoalStatus.ACTIVE:
            raise ValidationException("Não é possível adicionar contribuições a uma meta inativa")

        contribution = GoalContribution(
            goal_id=goal_id,
            amount=amount,
            contribution_date=contribution_date,
            notes=notes,
            transaction_id=transaction_id,
        )

        contribution = await self.contribution_repository.create(contribution)

        # Atualizar valor atual da meta
        goal.current_amount += amount
        await self.goal_repository.update(goal)

        # Verificar se meta foi alcançada
        if goal.current_amount >= goal.target_amount:
            goal.status = GoalStatus.COMPLETED
            await self.goal_repository.update(goal)

        # Criar evento do calendário para contribuição
        if self.calendar_event_service:
            try:
                await self.calendar_event_service.create_goal_contribution_event(
                    goal_id=goal_id,
                    goal_name=goal.name,
                    contribution_date=contribution_date,
                    user_id=goal.user_id,
                    amount=amount,
                    workspace_id=None,
                )
            except Exception as e:
                print(f"[DEBUG] Erro ao criar evento de calendário para contribuição: {e}")

        return contribution

    async def calculate_goal_progress(self, goal_id: UUID) -> dict:
        """Calcula o progresso de uma meta"""
        goal = await self.get_goal(goal_id)

        percentage = float((goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0.0
        remaining = goal.target_amount - goal.current_amount

        days_remaining = None
        estimated_completion_date = None
        monthly_savings_needed = None

        if goal.target_date:
            now = datetime.now(goal.target_date.tzinfo) if goal.target_date.tzinfo else datetime.now()
            days_remaining = (goal.target_date - now).days

            if days_remaining > 0 and remaining > 0:
                months_remaining = days_remaining / 30.0
                monthly_savings_needed = remaining / Decimal(str(months_remaining)) if months_remaining > 0 else None

                # Estimar data de conclusão baseada na média atual
                contributions = await self.contribution_repository.get_by_goal_id(goal_id)
                if contributions:
                    total_contributed = sum(c.amount for c in contributions)
                    days_active = (now - goal.created_at.replace(tzinfo=goal.target_date.tzinfo)).days
                    if days_active > 0 and total_contributed > 0:
                        daily_average = total_contributed / Decimal(str(days_active))
                        if daily_average > 0:
                            days_to_complete = float(remaining / daily_average)
                            estimated_completion_date = now + timedelta(days=int(days_to_complete))

        return {
            "goal_id": goal_id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "percentage": round(percentage, 2),
            "remaining_amount": remaining,
            "days_remaining": days_remaining,
            "estimated_completion_date": estimated_completion_date,
            "is_on_track": days_remaining is None or (days_remaining > 0 and monthly_savings_needed and monthly_savings_needed > 0),
            "monthly_savings_needed": monthly_savings_needed,
        }

    async def update_goal(
        self,
        goal_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        target_amount: Optional[Decimal] = None,
        target_date: Optional[datetime] = None,
        status: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        savings_category_id: Optional[UUID] = None,
        auto_contribution_percentage: Optional[Decimal] = None,
    ) -> Goal:
        """Atualiza uma meta"""
        goal = await self.get_goal(goal_id)

        if name:
            goal.name = name
        if description is not None:
            goal.description = description
        if target_amount:
            goal.target_amount = target_amount
        if target_date is not None:
            goal.target_date = target_date
        if status:
            try:
                goal.status = GoalStatus(status)
            except ValueError:
                raise ValidationException(f"Status inválido: {status}")
        if icon is not None:
            goal.icon = icon
        if color is not None:
            goal.color = color
        if savings_category_id is not None:
            goal.savings_category_id = savings_category_id
        if auto_contribution_percentage is not None:
            goal.auto_contribution_percentage = auto_contribution_percentage

        return await self.goal_repository.update(goal)

    async def delete_goal(self, goal_id: UUID) -> bool:
        """Deleta uma meta"""
        goal = await self.get_goal(goal_id)
        return await self.goal_repository.delete(goal_id)

