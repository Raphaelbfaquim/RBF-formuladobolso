from fastapi import APIRouter, Depends, Query, status, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.presentation.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
    CalendarEventCommentCreate,
    CalendarEventCommentResponse,
    CalendarEventParticipantUpdate,
    CalendarEventParticipantResponse,
    CalendarMonthResponse,
    CalendarEventsByDateResponse,
)
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.calendar_repository import (
    CalendarEventRepository,
    CalendarEventCommentRepository,
    CalendarEventParticipantRepository,
)
from src.infrastructure.repositories.calendar_repository import (
    SQLAlchemyCalendarEventRepository,
    SQLAlchemyCalendarEventCommentRepository,
    SQLAlchemyCalendarEventParticipantRepository,
)
from src.application.use_cases.calendar_use_cases import CalendarUseCases
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from src.infrastructure.database.models.calendar_event import (
    CalendarEvent,
    CalendarEventComment,
    CalendarEventParticipant,
    CalendarEventType,
)

router = APIRouter()


def get_calendar_event_repository(db: AsyncSession = Depends(get_db)) -> CalendarEventRepository:
    return SQLAlchemyCalendarEventRepository(db)


def get_calendar_comment_repository(db: AsyncSession = Depends(get_db)) -> CalendarEventCommentRepository:
    return SQLAlchemyCalendarEventCommentRepository(db)


def get_calendar_participant_repository(db: AsyncSession = Depends(get_db)) -> CalendarEventParticipantRepository:
    return SQLAlchemyCalendarEventParticipantRepository(db)


def get_calendar_use_cases(
    event_repo: CalendarEventRepository = Depends(get_calendar_event_repository),
    comment_repo: CalendarEventCommentRepository = Depends(get_calendar_comment_repository),
    participant_repo: CalendarEventParticipantRepository = Depends(get_calendar_participant_repository),
) -> CalendarUseCases:
    return CalendarUseCases(event_repo, comment_repo, participant_repo)


async def _build_event_response(event: CalendarEvent, current_user_id: UUID, db: AsyncSession) -> dict:
    """Constrói resposta de evento com dados relacionados"""
    from sqlalchemy import select
    from src.infrastructure.database.models.user import User
    from src.infrastructure.database.models.workspace import Workspace

    # Buscar dados do usuário
    user_result = await db.execute(select(User).where(User.id == event.user_id))
    user = user_result.scalar_one_or_none()
    user_name = user.full_name if user else None

    # Buscar dados do criador
    creator_result = await db.execute(select(User).where(User.id == event.created_by))
    creator = creator_result.scalar_one_or_none()
    created_by_name = creator.full_name if creator else None

    # Buscar dados do workspace
    workspace_name = None
    if event.workspace_id:
        workspace_result = await db.execute(select(Workspace).where(Workspace.id == event.workspace_id))
        workspace = workspace_result.scalar_one_or_none()
        workspace_name = workspace.name if workspace else None

    # Buscar comentários e participantes de forma assíncrona
    from src.infrastructure.database.models.calendar_event import CalendarEventComment, CalendarEventParticipant
    comments_query = select(CalendarEventComment).where(CalendarEventComment.event_id == event.id)
    comments_result = await db.execute(comments_query)
    comments = list(comments_result.scalars().all())
    comments_count = len(comments)

    participants_query = select(CalendarEventParticipant).where(CalendarEventParticipant.event_id == event.id)
    participants_result = await db.execute(participants_query)
    participants = list(participants_result.scalars().all())
    participants_count = len(participants)

    # Buscar status de participação do usuário atual
    user_participation = None
    for p in participants:
        if p.user_id == current_user_id:
            user_participation = p.status.value if hasattr(p.status, 'value') else str(p.status)
            break

    return {
        "id": event.id,
        "event_type": event.event_type if isinstance(event.event_type, str) else (event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)),
        "title": event.title,
        "description": event.description,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "all_day": event.all_day,
        "user_id": event.user_id,
        "user_name": user_name,
        "workspace_id": event.workspace_id,
        "workspace_name": workspace_name,
        "family_id": event.family_id,
        "related_transaction_id": event.related_transaction_id,
        "related_bill_id": event.related_bill_id,
        "related_goal_id": event.related_goal_id,
        "color": event.color,
        "icon": event.icon,
        "location": event.location,
        "is_shared": event.is_shared,
        "is_public": event.is_public,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
        "created_by": event.created_by,
        "created_by_name": created_by_name,
        "comments_count": comments_count,
        "participants_count": participants_count,
        "user_participation_status": user_participation,
    }


@router.post("/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: CalendarEventCreate,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria um novo evento"""
    event = await use_cases.create_event(
        event_type=event_data.event_type,
        title=event_data.title,
        start_date=event_data.start_date,
        user_id=current_user.id,
        created_by=current_user.id,
        description=event_data.description,
        end_date=event_data.end_date,
        all_day=event_data.all_day,
        workspace_id=event_data.workspace_id,
        family_id=event_data.family_id,
        related_transaction_id=event_data.related_transaction_id,
        related_bill_id=event_data.related_bill_id,
        related_goal_id=event_data.related_goal_id,
        color=event_data.color,
        icon=event_data.icon,
        location=event_data.location,
        is_shared=event_data.is_shared,
        is_public=event_data.is_public,
    )

    # Buscar evento completo com relacionamentos
    event = await use_cases.get_event(event.id, current_user.id)
    return await _build_event_response(event, current_user.id, db)


@router.get("/", response_model=List[CalendarEventResponse])
async def list_events(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020, le=2100),
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista eventos do usuário"""
    import pytz

    # Se month e year foram fornecidos, calcular start_date e end_date
    if month and year:
        start_date = datetime(year, month, 1, tzinfo=pytz.UTC)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=pytz.UTC)

    events = await use_cases.get_user_events(current_user.id, start_date, end_date)

    # Construir respostas
    responses = []
    for event in events:
        response = await _build_event_response(event, current_user.id, db)
        responses.append(response)

    return responses


@router.get("/month", response_model=CalendarMonthResponse)
async def get_month_events(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém eventos do mês agrupados por data"""
    import pytz

    start_date = datetime(year, month, 1, tzinfo=pytz.UTC)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=pytz.UTC)

    events = await use_cases.get_user_events(current_user.id, start_date, end_date)

    # Agrupar por data
    from collections import defaultdict
    events_by_date = defaultdict(list)

    for event in events:
        date_str = event.start_date.strftime("%Y-%m-%d")
        events_by_date[date_str].append(event)

    # Construir respostas agrupadas
    events_by_date_response = []
    for date_str in sorted(events_by_date.keys()):
        date_events = []
        for event in events_by_date[date_str]:
            response = await _build_event_response(event, current_user.id, db)
            date_events.append(response)
        events_by_date_response.append(
            CalendarEventsByDateResponse(date=date_str, events=date_events)
        )

    return CalendarMonthResponse(
        month=month,
        year=year,
        events_by_date=events_by_date_response,
        total_events=len(events),
    )


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: UUID,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém um evento específico"""
    event = await use_cases.get_event(event_id, current_user.id)
    return await _build_event_response(event, current_user.id, db)


@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: UUID,
    event_update: CalendarEventUpdate,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza um evento"""
    event = await use_cases.update_event(
        event_id=event_id,
        user_id=current_user.id,
        title=event_update.title,
        description=event_update.description,
        start_date=event_update.start_date,
        end_date=event_update.end_date,
        all_day=event_update.all_day,
        color=event_update.color,
        icon=event_update.icon,
        location=event_update.location,
        is_shared=event_update.is_shared,
        is_public=event_update.is_public,
    )

    event = await use_cases.get_event(event.id, current_user.id)
    return await _build_event_response(event, current_user.id, db)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: UUID,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta um evento"""
    await use_cases.delete_event(event_id, current_user.id)
    return None


@router.post("/{event_id}/comments", response_model=CalendarEventCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    event_id: UUID,
    comment_data: CalendarEventCommentCreate,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Adiciona um comentário a um evento"""
    from sqlalchemy import select
    from src.infrastructure.database.models.user import User

    comment = await use_cases.add_comment(event_id, current_user.id, comment_data.comment)

    # Buscar dados do usuário
    user_result = await db.execute(select(User).where(User.id == comment.user_id))
    user = user_result.scalar_one_or_none()

    return {
        "id": comment.id,
        "event_id": comment.event_id,
        "user_id": comment.user_id,
        "user_name": user.full_name if user else None,
        "comment": comment.comment,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
    }


@router.get("/{event_id}/comments", response_model=List[CalendarEventCommentResponse])
async def get_comments(
    event_id: UUID,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém comentários de um evento"""
    from sqlalchemy import select
    from src.infrastructure.database.models.user import User

    comments = await use_cases.get_event_comments(event_id, current_user.id)

    responses = []
    for comment in comments:
        user_result = await db.execute(select(User).where(User.id == comment.user_id))
        user = user_result.scalar_one_or_none()

        responses.append({
            "id": comment.id,
            "event_id": comment.event_id,
            "user_id": comment.user_id,
            "user_name": user.full_name if user else None,
            "comment": comment.comment,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        })

    return responses


@router.put("/{event_id}/participation", response_model=CalendarEventParticipantResponse)
async def update_participation(
    event_id: UUID,
    participation_data: CalendarEventParticipantUpdate,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza status de participação em um evento"""
    from sqlalchemy import select
    from src.infrastructure.database.models.user import User

    participant = await use_cases.update_participation(
        event_id, current_user.id, participation_data.status
    )

    # Buscar dados do usuário
    user_result = await db.execute(select(User).where(User.id == participant.user_id))
    user = user_result.scalar_one_or_none()

    return {
        "id": participant.id,
        "event_id": participant.event_id,
        "user_id": participant.user_id,
        "user_name": user.full_name if user else None,
        "status": participant.status.value,
        "responded_at": participant.responded_at,
        "created_at": participant.created_at,
    }


@router.get("/{event_id}/participants", response_model=List[CalendarEventParticipantResponse])
async def get_participants(
    event_id: UUID,
    use_cases: CalendarUseCases = Depends(get_calendar_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém participantes de um evento"""
    from sqlalchemy import select
    from src.infrastructure.database.models.user import User

    participants = await use_cases.get_event_participants(event_id, current_user.id)

    responses = []
    for participant in participants:
        user_result = await db.execute(select(User).where(User.id == participant.user_id))
        user = user_result.scalar_one_or_none()

        responses.append({
            "id": participant.id,
            "event_id": participant.event_id,
            "user_id": participant.user_id,
            "user_name": user.full_name if user else None,
            "status": participant.status.value,
            "responded_at": participant.responded_at,
            "created_at": participant.created_at,
        })

    return responses


@router.post("/sync-financial-events", status_code=status.HTTP_200_OK)
async def sync_financial_events(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Sincroniza eventos financeiros (transações, contas, metas) para o calendário"""
    from sqlalchemy import select, and_
    from src.infrastructure.database.models.transaction import Transaction, TransactionStatus
    from src.infrastructure.database.models.bill import Bill, BillStatus
    from src.infrastructure.database.models.goal import Goal, GoalStatus
    from src.application.services.calendar_event_service import CalendarEventService
    from src.infrastructure.repositories.calendar_repository import SQLAlchemyCalendarEventRepository
    from src.infrastructure.database.models.account import Account
    from src.infrastructure.database.models.calendar_event import CalendarEvent, CalendarEventType

    calendar_repo = SQLAlchemyCalendarEventRepository(db)
    calendar_service = CalendarEventService(calendar_repo)

    created_count = 0

    # Buscar transações concluídas sem evento
    transactions_query = select(Transaction).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.status == TransactionStatus.COMPLETED,
        )
    )
    transactions_result = await db.execute(transactions_query)
    transactions = list(transactions_result.scalars().all())

    for transaction in transactions:
        # Verificar se já existe evento
        existing_query = select(CalendarEvent).where(
            CalendarEvent.related_transaction_id == transaction.id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            continue

        # Buscar workspace_id da conta
        workspace_id = None
        if transaction.account_id:
            from src.infrastructure.database.models.account import Account
            account_result = await db.execute(
                select(Account).where(Account.id == transaction.account_id)
            )
            account = account_result.scalar_one_or_none()
            if account:
                workspace_id = getattr(account, 'workspace_id', None)

        try:
            await calendar_service.create_transaction_event(
                transaction_id=transaction.id,
                title=transaction.description,
                transaction_date=transaction.transaction_date,
                user_id=transaction.user_id,
                workspace_id=workspace_id,
                amount=transaction.amount,
                transaction_type=transaction.transaction_type.value,
            )
            created_count += 1
        except Exception as e:
            print(f"[DEBUG] Erro ao criar evento para transação {transaction.id}: {e}")

    # Buscar contas a pagar/receber sem evento
    bills_query = select(Bill).where(
        and_(
            Bill.user_id == current_user.id,
            Bill.status == BillStatus.PENDING,
        )
    )
    bills_result = await db.execute(bills_query)
    bills = list(bills_result.scalars().all())

    for bill in bills:
        # Verificar se já existe evento
        existing_query = select(CalendarEvent).where(
            CalendarEvent.related_bill_id == bill.id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            continue

        # Buscar workspace_id da conta
        workspace_id = None
        if bill.account_id:
            account_result = await db.execute(
                select(Account).where(Account.id == bill.account_id)
            )
            account = account_result.scalar_one_or_none()
            if account:
                workspace_id = account.workspace_id

        try:
            await calendar_service.create_bill_event(
                bill_id=bill.id,
                name=bill.name,
                due_date=bill.due_date,
                user_id=bill.user_id,
                workspace_id=workspace_id,
                amount=bill.amount,
                bill_type=bill.bill_type.value,
            )
            created_count += 1
        except Exception as e:
            print(f"[DEBUG] Erro ao criar evento para conta {bill.id}: {e}")

    # Buscar metas com data objetivo sem evento
    goals_query = select(Goal).where(
        and_(
            Goal.user_id == current_user.id,
            Goal.status == GoalStatus.ACTIVE,
            Goal.target_date.isnot(None),
        )
    )
    goals_result = await db.execute(goals_query)
    goals = list(goals_result.scalars().all())

    for goal in goals:
        # Verificar se já existe evento
        existing_query = select(CalendarEvent).where(
            and_(
                CalendarEvent.related_goal_id == goal.id,
                CalendarEvent.event_type == "goal",
            )
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            continue

        try:
            await calendar_service.create_goal_event(
                goal_id=goal.id,
                name=goal.name,
                target_date=goal.target_date,
                user_id=goal.user_id,
                workspace_id=None,
            )
            created_count += 1
        except Exception as e:
            print(f"[DEBUG] Erro ao criar evento para meta {goal.id}: {e}")

    return {"message": f"{created_count} eventos financeiros criados com sucesso", "created": created_count}
