from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.models.user import User
from src.infrastructure.database.models.account import Account
from src.infrastructure.database.models.transaction import Transaction, TransactionType, TransactionStatus
from src.domain.repositories.workspace_repository import (
    WorkspaceRepository,
    WorkspaceMemberRepository,
)
from src.domain.repositories.family_repository import FamilyMemberRepository
from src.infrastructure.repositories.workspace_repository import (
    SQLAlchemyWorkspaceRepository,
    SQLAlchemyWorkspaceMemberRepository,
)
from src.infrastructure.repositories.family_repository import SQLAlchemyFamilyMemberRepository
from src.application.use_cases.workspace_use_cases import WorkspaceUseCases
from src.infrastructure.database.base import get_db
from src.presentation.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceShareRequest,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_workspace_use_cases(db: AsyncSession = Depends(get_db)) -> WorkspaceUseCases:
    workspace_repo = SQLAlchemyWorkspaceRepository(db)
    member_repo = SQLAlchemyWorkspaceMemberRepository(db)
    family_member_repo = SQLAlchemyFamilyMemberRepository(db)
    
    return WorkspaceUseCases(workspace_repo, member_repo, family_member_repo)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    use_cases: WorkspaceUseCases = Depends(get_workspace_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria um novo workspace/contexto financeiro"""
    workspace = await use_cases.create_workspace(
        name=workspace_data.name,
        description=workspace_data.description,
        workspace_type=workspace_data.workspace_type,
        owner_id=current_user.id,
        family_id=workspace_data.family_id,
        color=workspace_data.color,
        icon=workspace_data.icon,
    )
    return workspace


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    use_cases: WorkspaceUseCases = Depends(get_workspace_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todos os workspaces acessíveis pelo usuário"""
    workspaces = await use_cases.get_user_workspaces(current_user.id)
    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    use_cases: WorkspaceUseCases = Depends(get_workspace_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém detalhes de um workspace"""
    try:
        workspace = await use_cases.get_workspace(workspace_id, current_user.id)
        return workspace
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    workspace_data: WorkspaceUpdate,
    use_cases: WorkspaceUseCases = Depends(get_workspace_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza um workspace"""
    try:
        workspace = await use_cases.update_workspace(
            workspace_id=workspace_id,
            user_id=current_user.id,
            name=workspace_data.name,
            description=workspace_data.description,
            color=workspace_data.color,
            icon=workspace_data.icon,
        )
        return workspace
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    use_cases: WorkspaceUseCases = Depends(get_workspace_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta um workspace"""
    try:
        await use_cases.delete_workspace(workspace_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{workspace_id}/share", status_code=status.HTTP_201_CREATED)
async def share_workspace(
    workspace_id: UUID,
    share_data: WorkspaceShareRequest,
    use_cases: WorkspaceUseCases = Depends(get_workspace_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Compartilha workspace com outro usuário"""
    try:
        member = await use_cases.share_workspace(
            workspace_id=workspace_id,
            owner_id=current_user.id,
            user_id=share_data.user_id,
            can_edit=share_data.can_edit,
            can_delete=share_data.can_delete,
        )
        return {"message": "Workspace compartilhado com sucesso", "member_id": member.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: UUID,
    use_cases: WorkspaceUseCases = Depends(get_workspace_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém estatísticas do workspace"""
    # Verificar acesso
    workspace = await use_cases.get_workspace(workspace_id, current_user.id)
    
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    month_end = month_end.replace(hour=23, minute=59, second=59)
    
    # Contas do workspace
    accounts_query = select(Account).where(
        and_(
            Account.workspace_id == workspace_id,
            Account.is_active == True
        )
    )
    accounts_result = await db.execute(accounts_query)
    accounts = list(accounts_result.scalars().all())
    total_balance = sum(float(a.balance) for a in accounts)
    
    # Transações do mês
    transactions_query = select(Transaction).where(
        and_(
            Transaction.workspace_id == workspace_id,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.transaction_date >= month_start,
            Transaction.transaction_date <= month_end
        )
    )
    transactions_result = await db.execute(transactions_query)
    transactions = list(transactions_result.scalars().all())
    
    monthly_income = sum(
        float(t.amount) for t in transactions
        if t.transaction_type == TransactionType.INCOME
    )
    monthly_expenses = sum(
        float(t.amount) for t in transactions
        if t.transaction_type == TransactionType.EXPENSE
    )
    monthly_savings = monthly_income - monthly_expenses
    
    # Últimas transações
    recent_query = select(Transaction).where(
        Transaction.workspace_id == workspace_id
    ).options(
        joinedload(Transaction.category),
        joinedload(Transaction.account)
    ).order_by(
        Transaction.transaction_date.desc()
    ).limit(10)
    recent_result = await db.execute(recent_query)
    recent_transactions = list(recent_result.scalars().all())
    
    return {
        "workspace_id": str(workspace_id),
        "total_accounts": len(accounts),
        "total_balance": total_balance,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "monthly_savings": monthly_savings,
        "transactions_count": len(transactions),
        "recent_transactions": [
            {
                "id": str(t.id),
                "description": t.description,
                "amount": float(t.amount),
                "transaction_type": t.transaction_type.value,
                "transaction_date": t.transaction_date.isoformat(),
                "category": t.category.name if t.category else None,
                "account": t.account.name if t.account else None,
            }
            for t in recent_transactions
        ]
    }

