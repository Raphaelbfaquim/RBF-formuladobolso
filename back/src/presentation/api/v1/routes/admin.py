from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
import pytz

from src.presentation.api.dependencies import get_current_admin_user, get_db, get_user_repository
from src.infrastructure.database.models.user import User, UserRole
from src.infrastructure.database.models.security import SecurityAlert, AuditLog, TwoFactorAuth
from src.infrastructure.database.models.family import Family
from src.infrastructure.database.models.transaction import Transaction
from src.infrastructure.database.models.account import Account
from src.infrastructure.database.models.family_member import FamilyMember
from src.presentation.schemas.admin import (
    AdminDashboardResponse,
    AdminDashboardStats,
    UserDetailResponse,
    UpdateUserRequest,
)
from src.domain.repositories.user_repository import UserRepository

router = APIRouter()


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard administrativo com estatísticas gerais"""
    try:
        # Estatísticas de usuários
        total_users_stmt = select(func.count(User.id))
        total_users = (await db.execute(total_users_stmt)).scalar() or 0

        active_users_stmt = select(func.count(User.id)).where(User.is_active == True)
        active_users = (await db.execute(active_users_stmt)).scalar() or 0

        inactive_users = total_users - active_users

        # Novos usuários (últimos 7 e 30 dias)
        now = datetime.now(pytz.UTC)
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)

        new_users_7_stmt = select(func.count(User.id)).where(User.created_at >= last_7_days)
        new_users_7 = (await db.execute(new_users_7_stmt)).scalar() or 0

        new_users_30_stmt = select(func.count(User.id)).where(User.created_at >= last_30_days)
        new_users_30 = (await db.execute(new_users_30_stmt)).scalar() or 0

        # Usuários não verificados
        unverified_stmt = select(func.count(User.id)).where(User.is_verified == False)
        unverified_users = (await db.execute(unverified_stmt)).scalar() or 0

        # Total de famílias
        total_families_stmt = select(func.count(Family.id))
        total_families = (await db.execute(total_families_stmt)).scalar() or 0

        # Total de transações
        total_transactions_stmt = select(func.count(Transaction.id))
        total_transactions = (await db.execute(total_transactions_stmt)).scalar() or 0

        # Volume total (soma de todas as transações)
        total_volume_stmt = select(func.coalesce(func.sum(Transaction.amount), 0))
        total_volume = (await db.execute(total_volume_stmt)).scalar() or 0

        # Usuários com 2FA
        users_with_2fa_stmt = select(func.count(TwoFactorAuth.id)).where(
            TwoFactorAuth.is_enabled == True
        )
        users_with_2fa = (await db.execute(users_with_2fa_stmt)).scalar() or 0

        # Alertas de segurança pendentes
        security_alerts_stmt = select(func.count(SecurityAlert.id)).where(
            SecurityAlert.is_read == False
        )
        security_alerts_count = (await db.execute(security_alerts_stmt)).scalar() or 0

        # Usuários recentes (últimos 5)
        recent_users_stmt = (
            select(User)
            .order_by(User.created_at.desc())
            .limit(5)
        )
        recent_users_result = await db.execute(recent_users_stmt)
        recent_users = recent_users_result.scalars().all()

        # Atividades recentes (últimos 10 logs)
        recent_logs_stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(10)
        )
        recent_logs_result = await db.execute(recent_logs_stmt)
        recent_logs = recent_logs_result.scalars().all()

        stats = AdminDashboardStats(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            new_users_last_7_days=new_users_7,
            new_users_last_30_days=new_users_30,
            total_families=total_families,
            total_transactions=total_transactions,
            total_volume=float(total_volume),
            users_with_2fa=users_with_2fa,
            unverified_users=unverified_users,
        )

        return AdminDashboardResponse(
            stats=stats,
            recent_users=[
                {
                    "id": str(u.id),
                    "email": u.email,
                    "username": u.username,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "is_active": u.is_active,
                }
                for u in recent_users
            ],
            security_alerts_count=security_alerts_count,
            recent_activities=[
                {
                    "id": str(log.id),
                    "action": log.action,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in recent_logs
            ],
        )
    except Exception as e:
        print(f"Erro no dashboard admin: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dashboard: {str(e)}"
        )


@router.get("/users")
async def list_users(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    role: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos os usuários com filtros e paginação"""
    try:
        # Construir query base
        stmt = select(User)

        # Aplicar filtros
        conditions = []
        if search:
            conditions.append(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                )
            )
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        if is_verified is not None:
            conditions.append(User.is_verified == is_verified)
        if role:
            conditions.append(User.role == UserRole(role))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Contar total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        # Aplicar paginação e ordenação
        stmt = stmt.order_by(User.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        # Executar query
        result = await db.execute(stmt)
        users = result.scalars().all()

        # Buscar informações adicionais para cada usuário
        users_data = []
        for user in users:
            # Contar famílias
            families_stmt = select(func.count(FamilyMember.id)).where(
                FamilyMember.user_id == user.id
            )
            families_count = (await db.execute(families_stmt)).scalar() or 0

            # Contar contas
            accounts_stmt = select(func.count(Account.id)).where(Account.user_id == user.id)
            accounts_count = (await db.execute(accounts_stmt)).scalar() or 0

            # Contar transações
            transactions_stmt = select(func.count(Transaction.id)).where(
                Transaction.user_id == user.id
            )
            transactions_count = (await db.execute(transactions_stmt)).scalar() or 0

            # Verificar 2FA
            two_factor_stmt = select(TwoFactorAuth).where(
                TwoFactorAuth.user_id == user.id, TwoFactorAuth.is_enabled == True
            )
            two_factor_result = await db.execute(two_factor_stmt)
            has_2fa = two_factor_result.scalar_one_or_none() is not None

            users_data.append({
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "families_count": families_count,
                "accounts_count": accounts_count,
                "transactions_count": transactions_count,
                "has_2fa": has_2fa,
            })

        return {
            "users": users_data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar usuários: {str(e)}"
        )


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém detalhes completos de um usuário"""
    try:
        user_stmt = select(User).where(User.id == user_id)
        result = await db.execute(user_stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Contar famílias
        families_stmt = select(func.count(FamilyMember.id)).where(
            FamilyMember.user_id == user.id
        )
        families_count = (await db.execute(families_stmt)).scalar() or 0

        # Contar contas
        accounts_stmt = select(func.count(Account.id)).where(Account.user_id == user.id)
        accounts_count = (await db.execute(accounts_stmt)).scalar() or 0

        # Contar transações
        transactions_stmt = select(func.count(Transaction.id)).where(
            Transaction.user_id == user.id
        )
        transactions_count = (await db.execute(transactions_stmt)).scalar() or 0

        # Verificar 2FA
        two_factor_stmt = select(TwoFactorAuth).where(
            TwoFactorAuth.user_id == user.id, TwoFactorAuth.is_enabled == True
        )
        two_factor_result = await db.execute(two_factor_stmt)
        two_factor = two_factor_result.scalar_one_or_none()
        has_2fa = two_factor is not None

        # Buscar últimos logs do usuário
        logs_stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user.id)
            .order_by(AuditLog.created_at.desc())
            .limit(20)
        )
        logs_result = await db.execute(logs_stmt)
        logs = logs_result.scalars().all()

        # Buscar alertas de segurança
        alerts_stmt = (
            select(SecurityAlert)
            .where(SecurityAlert.user_id == user.id)
            .order_by(SecurityAlert.created_at.desc())
            .limit(10)
        )
        alerts_result = await db.execute(alerts_stmt)
        alerts = alerts_result.scalars().all()

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            },
            "stats": {
                "families_count": families_count,
                "accounts_count": accounts_count,
                "transactions_count": transactions_count,
                "has_2fa": has_2fa,
            },
            "recent_logs": [
                {
                    "id": str(log.id),
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ],
            "security_alerts": [
                {
                    "id": str(alert.id),
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "severity": alert.severity,
                    "is_read": alert.is_read,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                }
                for alert in alerts
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao obter detalhes do usuário: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter detalhes: {str(e)}"
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    user_update: UpdateUserRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Atualiza um usuário (apenas admin)"""
    try:
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Não permitir que admin remova seu próprio role de admin
        if user_id == current_user.id and user_update.role and user_update.role != "admin":
            raise HTTPException(
                status_code=400, detail="Você não pode remover seu próprio acesso de admin"
            )

        # Atualizar campos
        update_data = {}
        if user_update.email is not None:
            update_data["email"] = user_update.email
        if user_update.username is not None:
            update_data["username"] = user_update.username
        if user_update.full_name is not None:
            update_data["full_name"] = user_update.full_name
        if user_update.is_active is not None:
            update_data["is_active"] = user_update.is_active
        if user_update.is_verified is not None:
            update_data["is_verified"] = user_update.is_verified
        if user_update.role is not None:
            update_data["role"] = UserRole(user_update.role)

        user = await user_repository.update_user(user_id, **update_data)

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Ativa um usuário"""
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user = await user_repository.update_user(user_id, is_active=True)
    return {"message": "Usuário ativado com sucesso", "user_id": str(user.id)}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Desativa um usuário"""
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Não permitir desativar a si mesmo
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta")

    user = await user_repository.update_user(user_id, is_active=False)
    return {"message": "Usuário desativado com sucesso", "user_id": str(user.id)}


@router.post("/users/{user_id}/make-admin")
async def make_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Torna um usuário administrador"""
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user = await user_repository.update_user(user_id, role=UserRole.ADMIN)
    return {"message": "Usuário promovido a administrador", "user_id": str(user.id)}


@router.post("/users/{user_id}/remove-admin")
async def remove_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Remove privilégios de administrador de um usuário"""
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Não permitir remover admin de si mesmo
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Você não pode remover seu próprio acesso de admin"
        )

    user = await user_repository.update_user(user_id, role=UserRole.USER)
    return {"message": "Privilégios de admin removidos", "user_id": str(user.id)}


@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista logs de auditoria (apenas admin)"""
    try:
        stmt = select(AuditLog)

        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if action:
            conditions.append(AuditLog.action.ilike(f"%{action}%"))
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Contar total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        # Aplicar paginação
        stmt = stmt.order_by(AuditLog.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        logs = result.scalars().all()

        return {
            "logs": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id) if log.user_id else None,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": str(log.resource_id) if log.resource_id else None,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "details": log.details,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    except Exception as e:
        print(f"Erro ao listar logs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar logs: {str(e)}"
        )


@router.get("/security-alerts")
async def get_security_alerts(
    severity: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista alertas de segurança (apenas admin)"""
    try:
        stmt = select(SecurityAlert)

        conditions = []
        if severity:
            conditions.append(SecurityAlert.severity == severity)
        if is_read is not None:
            conditions.append(SecurityAlert.is_read == is_read)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Contar total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        # Aplicar paginação
        stmt = stmt.order_by(SecurityAlert.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        alerts = result.scalars().all()

        return {
            "alerts": [
                {
                    "id": str(alert.id),
                    "user_id": str(alert.user_id),
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "severity": alert.severity,
                    "is_read": alert.is_read,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                }
                for alert in alerts
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    except Exception as e:
        print(f"Erro ao listar alertas: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar alertas: {str(e)}"
        )

