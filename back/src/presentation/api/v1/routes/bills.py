from fastapi import APIRouter, Depends, Query, status, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.presentation.schemas.bill import BillCreate, BillUpdate, BillResponse
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.bill_repository import BillRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.calendar_repository import CalendarEventRepository
from src.infrastructure.repositories.bill_repository import SQLAlchemyBillRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.calendar_repository import SQLAlchemyCalendarEventRepository
from src.application.use_cases.bill_use_cases import BillUseCases
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_bill_repository(db: AsyncSession = Depends(get_db)) -> BillRepository:
    return SQLAlchemyBillRepository(db)


def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    return SQLAlchemyAccountRepository(db)


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    return SQLAlchemyTransactionRepository(db)


def get_calendar_event_repository(
    db: AsyncSession = Depends(get_db)
) -> "CalendarEventRepository":
    from src.domain.repositories.calendar_repository import CalendarEventRepository
    from src.infrastructure.repositories.calendar_repository import SQLAlchemyCalendarEventRepository
    return SQLAlchemyCalendarEventRepository(db)


def get_bill_use_cases(
    bill_repo: BillRepository = Depends(get_bill_repository),
    account_repo: AccountRepository = Depends(get_account_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    calendar_event_repo: "CalendarEventRepository" = Depends(get_calendar_event_repository),
) -> BillUseCases:
    return BillUseCases(bill_repo, account_repo, transaction_repo, calendar_event_repo)


@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: BillCreate,
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma nova conta a pagar/receber"""
    bill = await use_cases.create_bill(
        name=bill_data.name,
        bill_type=bill_data.bill_type,
        amount=bill_data.amount,
        due_date=bill_data.due_date,
        user_id=current_user.id,
        description=bill_data.description,
        account_id=bill_data.account_id,
        category_id=bill_data.category_id,
        is_recurring=bill_data.is_recurring,
        recurrence_type=bill_data.recurrence_type,
        recurrence_day=bill_data.recurrence_day,
        recurrence_end_date=bill_data.recurrence_end_date,
    )
    
    # Adicionar campos calculados
    now = datetime.now(bill.due_date.tzinfo) if bill.due_date.tzinfo else datetime.now()
    days_until_due = (bill.due_date - now).days if bill.due_date > now else None
    is_overdue = bill.due_date < now and bill.status.value == "pending"
    
    # Criar dicionário com todos os campos necessários
    bill_dict = {
        "id": bill.id,
        "name": bill.name,
        "description": bill.description,
        "bill_type": bill.bill_type.value,
        "amount": bill.amount,
        "due_date": bill.due_date,
        "status": bill.status.value,
        "payment_date": bill.payment_date,
        "is_recurring": bill.is_recurring,
        "recurrence_type": bill.recurrence_type.value,
        "recurrence_day": bill.recurrence_day,
        "recurrence_end_date": bill.recurrence_end_date,
        "transaction_id": bill.transaction_id,
        "user_id": bill.user_id,
        "account_id": bill.account_id,
        "category_id": bill.category_id,
        "days_until_due": days_until_due,
        "is_overdue": is_overdue,
        "created_at": bill.created_at,
        "updated_at": bill.updated_at,
    }
    
    return bill_dict


@router.get("/")
async def list_bills(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    bill_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todas as contas do usuário"""
    bills = await use_cases.get_user_bills(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        bill_type=bill_type,
        status=status,
    )
    
    result = []
    now = datetime.now()
    for bill in bills:
        bill_due = bill.due_date.replace(tzinfo=None) if bill.due_date.tzinfo else bill.due_date
        days_until_due = (bill_due - now).days if bill_due > now else None
        is_overdue = bill_due < now and bill.status.value == "pending"
        
        # Criar dicionário manualmente para incluir campos calculados
        bill_dict = {
            "id": bill.id,
            "name": bill.name,
            "description": bill.description,
            "bill_type": bill.bill_type.value,
            "amount": bill.amount,
            "due_date": bill.due_date,
            "status": bill.status.value,
            "payment_date": bill.payment_date,
            "is_recurring": bill.is_recurring,
            "recurrence_type": bill.recurrence_type.value,
            "recurrence_day": bill.recurrence_day,
            "recurrence_end_date": bill.recurrence_end_date,
            "transaction_id": bill.transaction_id,
            "user_id": bill.user_id,
            "account_id": bill.account_id,
            "category_id": bill.category_id,
            "days_until_due": days_until_due,
            "is_overdue": is_overdue,
            "created_at": bill.created_at,
            "updated_at": bill.updated_at,
        }
        
        # Incluir nome da categoria se existir
        if bill.category:
            bill_dict["category"] = {
                "id": bill.category.id,
                "name": bill.category.name,
                "category_type": bill.category.category_type.value,
            }
        
        result.append(bill_dict)
    
    return result


@router.get("/upcoming")
async def get_upcoming_bills(
    days: int = Query(7, ge=1, le=30),
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém contas próximas do vencimento"""
    bills = await use_cases.get_upcoming_bills(current_user.id, days)
    
    result = []
    now = datetime.now()
    for bill in bills:
        bill_due = bill.due_date.replace(tzinfo=None) if bill.due_date.tzinfo else bill.due_date
        days_until_due = (bill_due - now).days if bill_due > now else None
        
        # Criar dicionário manualmente para incluir campos calculados
        bill_dict = {
            "id": bill.id,
            "name": bill.name,
            "description": bill.description,
            "bill_type": bill.bill_type.value,
            "amount": bill.amount,
            "due_date": bill.due_date,
            "status": bill.status.value,
            "payment_date": bill.payment_date,
            "is_recurring": bill.is_recurring,
            "recurrence_type": bill.recurrence_type.value,
            "recurrence_day": bill.recurrence_day,
            "recurrence_end_date": bill.recurrence_end_date,
            "transaction_id": bill.transaction_id,
            "user_id": bill.user_id,
            "account_id": bill.account_id,
            "category_id": bill.category_id,
            "days_until_due": days_until_due,
            "is_overdue": False,
            "created_at": bill.created_at,
            "updated_at": bill.updated_at,
        }
        result.append(bill_dict)
    
    return result


@router.get("/overdue")
async def get_overdue_bills(
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém contas vencidas"""
    bills = await use_cases.get_overdue_bills(current_user.id)
    
    result = []
    for bill in bills:
        # Criar dicionário manualmente para incluir campos calculados
        bill_dict = {
            "id": bill.id,
            "name": bill.name,
            "description": bill.description,
            "bill_type": bill.bill_type.value,
            "amount": bill.amount,
            "due_date": bill.due_date,
            "status": bill.status.value,
            "payment_date": bill.payment_date,
            "is_recurring": bill.is_recurring,
            "recurrence_type": bill.recurrence_type.value,
            "recurrence_day": bill.recurrence_day,
            "recurrence_end_date": bill.recurrence_end_date,
            "transaction_id": bill.transaction_id,
            "user_id": bill.user_id,
            "account_id": bill.account_id,
            "category_id": bill.category_id,
            "days_until_due": None,
            "is_overdue": True,
            "created_at": bill.created_at,
            "updated_at": bill.updated_at,
        }
        result.append(bill_dict)
    
    return result


@router.get("/{bill_id}")
async def get_bill(
    bill_id: UUID,
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma conta específica"""
    bill = await use_cases.get_bill(bill_id)
    
    now = datetime.now()
    bill_due = bill.due_date.replace(tzinfo=None) if bill.due_date.tzinfo else bill.due_date
    days_until_due = (bill_due - now).days if bill_due > now else None
    is_overdue = bill_due < now and bill.status.value == "pending"
    
    # Criar dicionário manualmente para incluir campos calculados
    bill_dict = {
        "id": bill.id,
        "name": bill.name,
        "description": bill.description,
        "bill_type": bill.bill_type.value,
        "amount": bill.amount,
        "due_date": bill.due_date,
        "status": bill.status.value,
        "payment_date": bill.payment_date,
        "is_recurring": bill.is_recurring,
        "recurrence_type": bill.recurrence_type.value,
        "recurrence_day": bill.recurrence_day,
        "recurrence_end_date": bill.recurrence_end_date,
        "transaction_id": bill.transaction_id,
        "user_id": bill.user_id,
        "account_id": bill.account_id,
        "category_id": bill.category_id,
        "days_until_due": days_until_due,
        "is_overdue": is_overdue,
        "created_at": bill.created_at,
        "updated_at": bill.updated_at,
    }
    
    return bill_dict


@router.get("/by-transaction/{transaction_id}")
async def get_bill_by_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém conta relacionada a uma transação"""
    from src.domain.repositories.bill_repository import BillRepository
    from src.infrastructure.repositories.bill_repository import SQLAlchemyBillRepository
    
    bill_repo: BillRepository = SQLAlchemyBillRepository(db)
    bill = await bill_repo.get_by_transaction_id(transaction_id)
    
    if not bill:
        raise HTTPException(status_code=404, detail="Conta não encontrada para esta transação")
    
    if bill.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    now = datetime.now()
    bill_due = bill.due_date.replace(tzinfo=None) if bill.due_date.tzinfo else bill.due_date
    days_until_due = (bill_due - now).days if bill_due > now else None
    is_overdue = bill_due < now and bill.status.value == "pending"
    
    bill_dict = {
        "id": bill.id,
        "name": bill.name,
        "description": bill.description,
        "bill_type": bill.bill_type.value,
        "amount": bill.amount,
        "due_date": bill.due_date,
        "status": bill.status.value,
        "payment_date": bill.payment_date,
        "is_recurring": bill.is_recurring,
        "recurrence_type": bill.recurrence_type.value,
        "recurrence_day": bill.recurrence_day,
        "recurrence_end_date": bill.recurrence_end_date,
        "transaction_id": bill.transaction_id,
        "user_id": bill.user_id,
        "account_id": bill.account_id,
        "category_id": bill.category_id,
        "days_until_due": days_until_due,
        "is_overdue": is_overdue,
        "created_at": bill.created_at,
        "updated_at": bill.updated_at,
    }
    
    return bill_dict


@router.post("/{bill_id}/pay", response_model=BillResponse)
async def pay_bill(
    bill_id: UUID,
    payment_date: Optional[datetime] = None,
    account_id: Optional[UUID] = None,
    create_transaction: bool = True,
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Marca conta como paga"""
    bill = await use_cases.pay_bill(
        bill_id=bill_id,
        payment_date=payment_date,
        account_id=account_id,
        create_transaction=create_transaction,
    )
    
    return BillResponse.model_validate(bill)


@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: UUID,
    bill_update: BillUpdate,
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza uma conta"""
    bill = await use_cases.update_bill(
        bill_id=bill_id,
        name=bill_update.name,
        description=bill_update.description,
        amount=bill_update.amount,
        due_date=bill_update.due_date,
        status=bill_update.status,
        payment_date=bill_update.payment_date,
        account_id=bill_update.account_id,
        category_id=bill_update.category_id,
    )
    
    return BillResponse.model_validate(bill)


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(
    bill_id: UUID,
    use_cases: BillUseCases = Depends(get_bill_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta uma conta"""
    await use_cases.delete_bill(bill_id)
    return None

