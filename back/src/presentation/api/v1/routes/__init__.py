from fastapi import APIRouter
from src.presentation.api.v1.routes import (
    auth,
    users,
    accounts,
    transactions,
    categories,
    planning,
    monthly_budget,
    receipts,
    investments,
    notifications,
    goals,
    gamification,
    bills,
    reports,
    dashboard,
    ai,
    predictions,
    insights,
    open_banking,
    education,
    habits,
    family_collaboration,
    security,
    workspaces,
    transfers,
    calendar,
    scheduled_transactions,
    logs,
)

api_router = APIRouter()

# Incluir rotas
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(planning.router, prefix="/planning", tags=["planning"])
api_router.include_router(monthly_budget.router, prefix="/monthly-budget", tags=["monthly-budget"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(investments.router, prefix="/investments", tags=["investments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(bills.router, prefix="/bills", tags=["bills"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai-assistant"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(open_banking.router, prefix="/open-banking", tags=["open-banking"])
api_router.include_router(education.router, prefix="/education", tags=["education"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])
api_router.include_router(family_collaboration.router, prefix="/family", tags=["family-collaboration"])
api_router.include_router(security.router, prefix="/security", tags=["security"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(scheduled_transactions.router, prefix="/scheduled-transactions", tags=["scheduled-transactions"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])

