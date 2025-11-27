from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.goal_repository import GoalRepository
from src.domain.repositories.planning_repository import PlanningRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.repositories.goal_repository import SQLAlchemyGoalRepository
from src.infrastructure.repositories.planning_repository import SQLAlchemyPlanningRepository
from src.application.services.ai_service import AIService
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from src.shared.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []


def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    goal_repo = SQLAlchemyGoalRepository(db)
    planning_repo = SQLAlchemyPlanningRepository(db)
    
    api_key = getattr(settings, "OPENAI_API_KEY", None) or getattr(settings, "ANTHROPIC_API_KEY", None)
    
    return AIService(transaction_repo, account_repo, goal_repo, planning_repo, api_key)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_data: ChatMessage,
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_active_user),
):
    """Conversa com o assistente financeiro IA"""
    result = await ai_service.chat(
        current_user.id,
        chat_data.message,
        chat_data.conversation_history,
    )
    return result


@router.get("/suggestions")
async def get_ai_suggestions(
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém sugestões automáticas da IA"""
    suggestions = await ai_service.get_suggestions(current_user.id)
    return {"suggestions": suggestions}


@router.get("/context")
async def get_financial_context(
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém contexto financeiro do usuário"""
    context = await ai_service.get_financial_context(current_user.id)
    return context

