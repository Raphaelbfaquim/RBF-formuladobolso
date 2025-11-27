"""
Tarefa agendada para verificar planejamentos e enviar notificações
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.database.base import AsyncSessionLocal
from src.domain.repositories.planning_repository import PlanningRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.planning_repository import (
    SQLAlchemyPlanningRepository,
    SQLAlchemyMonthlyPlanningRepository,
    SQLAlchemyWeeklyPlanningRepository,
    SQLAlchemyDailyPlanningRepository,
    SQLAlchemyAnnualPlanningRepository,
    SQLAlchemyQuarterlyGoalRepository,
)
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from src.application.notifications.notification_service import NotificationService
from src.application.use_cases.planning_use_cases import PlanningUseCases
from src.application.use_cases.notification_use_cases import NotificationUseCases
from src.infrastructure.database.models.planning import Planning


class PlanningCheckerTask:
    """Tarefa para verificar planejamentos periodicamente"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def check_plannings(self):
        """Verifica todos os planejamentos ativos"""
        async with AsyncSessionLocal() as session:
            try:
                # Inicializar repositórios
                planning_repo = SQLAlchemyPlanningRepository(session)
                transaction_repo = SQLAlchemyTransactionRepository(session)
                user_repo = SQLAlchemyUserRepository(session)

                # Inicializar serviços
                notification_service = NotificationService()
                planning_use_cases = PlanningUseCases(
                    planning_repository=planning_repo,
                    monthly_repository=SQLAlchemyMonthlyPlanningRepository(session),
                    weekly_repository=SQLAlchemyWeeklyPlanningRepository(session),
                    daily_repository=SQLAlchemyDailyPlanningRepository(session),
                    annual_repository=SQLAlchemyAnnualPlanningRepository(session),
                    quarterly_repository=SQLAlchemyQuarterlyGoalRepository(session),
                    transaction_repository=transaction_repo,
                )
                notification_use_cases = NotificationUseCases(
                    planning_repository=planning_repo,
                    transaction_repository=transaction_repo,
                    user_repository=user_repo,
                    notification_service=notification_service,
                    planning_use_cases=planning_use_cases,
                )

                # Buscar todos os planejamentos ativos
                result = await session.execute(
                    select(Planning).where(
                        Planning.is_active == True
                    )
                )
                plannings = result.scalars().all()

                print(f"[{datetime.now()}] Verificando {len(plannings)} planejamentos...")

                for planning in plannings:
                    try:
                        result = await notification_use_cases.check_and_notify_planning(
                            planning_id=planning.id,
                            threshold=10.0,  # 10% de tolerância
                        )

                        if result.get("notified"):
                            print(
                                f"[{datetime.now()}] Notificação enviada para planejamento {planning.id} "
                                f"(Porcentagem: {result.get('percentage'):.2f}%)"
                            )
                    except Exception as e:
                        print(f"Erro ao verificar planejamento {planning.id}: {e}")

            except Exception as e:
                print(f"Erro na verificação de planejamentos: {e}")

    def start(self):
        """Inicia o agendador"""
        if self.is_running:
            return

        # Verificar a cada hora
        self.scheduler.add_job(
            self.check_plannings,
            trigger=CronTrigger(minute=0),  # Todo minuto 0 de cada hora
            id="check_plannings",
            name="Verificar planejamentos e enviar notificações",
            replace_existing=True,
        )

        # Também verificar diariamente às 8h e 20h
        self.scheduler.add_job(
            self.check_plannings,
            trigger=CronTrigger(hour="8,20", minute=0),
            id="check_plannings_daily",
            name="Verificação diária de planejamentos",
            replace_existing=True,
        )

        self.scheduler.start()
        self.is_running = True
        print("Tarefa de verificação de planejamentos iniciada")

    def stop(self):
        """Para o agendador"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("Tarefa de verificação de planejamentos parada")


# Instância global
planning_checker = PlanningCheckerTask()

