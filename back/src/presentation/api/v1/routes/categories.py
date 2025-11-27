from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from uuid import UUID
from src.presentation.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from src.application.use_cases.category_use_cases import CategoryUseCases
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from src.shared.exceptions import NotFoundException, ValidationException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_category_repository(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    return SQLAlchemyCategoryRepository(db)


def get_category_use_cases(
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryUseCases:
    return CategoryUseCases(category_repository)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    use_cases: CategoryUseCases = Depends(get_category_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma nova categoria"""
    category = await use_cases.create_category(
        name=category_data.name,
        category_type=category_data.category_type,
        user_id=current_user.id,
        description=category_data.description,
        icon=category_data.icon,
        color=category_data.color,
        parent_id=category_data.parent_id,
    )
    return category


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    use_cases: CategoryUseCases = Depends(get_category_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas as categorias do usuário e da família (se aplicável)"""
    from src.infrastructure.repositories.family_repository import SQLAlchemyFamilyRepository, SQLAlchemyFamilyMemberRepository
    from src.infrastructure.repositories.family_permission_repository import SQLAlchemyFamilyPermissionRepository
    from src.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
    from src.infrastructure.database.models.family_permission import ModulePermission
    from sqlalchemy import text
    
    # Buscar categorias do usuário
    user_categories = await use_cases.get_user_categories(current_user.id)
    all_categories = list(user_categories)
    
    # Verificar se usuário está em alguma família e tem permissão para ver categorias
    try:
        family_repo = SQLAlchemyFamilyRepository(db)
        member_repo = SQLAlchemyFamilyMemberRepository(db)
        category_repo = SQLAlchemyCategoryRepository(db)
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        
        families = await family_repo.get_by_user_id(current_user.id)
        
        # Para cada família, buscar categorias se tiver permissão
        for family in families:
            try:
                member = await member_repo.get_member_in_family(current_user.id, family.id)
                if member:
                    # Verificar permissão para ver categorias
                    permission = await permission_repo.get_by_family_member_and_module(
                        member.id, ModulePermission.CATEGORIES
                    )
                    if permission and permission.can_view:
                        # Buscar categorias da família (com family_id)
                        try:
                            family_categories = await category_repo.get_by_family_id(family.id)
                            
                            # Buscar user_ids dos membros da família usando SQL direto
                            result = await db.execute(
                                text("SELECT user_id FROM family_members WHERE family_id = :family_id"),
                                {"family_id": str(family.id)}
                            )
                            member_user_ids = [row[0] for row in result.fetchall()]
                            
                            # Buscar categorias de cada membro
                            existing_ids = {cat.id for cat in all_categories}
                            for member_user_id in member_user_ids:
                                try:
                                    member_categories = await category_repo.get_by_user_id(member_user_id)
                                    for cat in member_categories:
                                        if cat.id not in existing_ids:
                                            all_categories.append(cat)
                                            existing_ids.add(cat.id)
                                except Exception as e:
                                    print(f"⚠️ Erro ao buscar categorias do membro {member_user_id}: {e}")
                                    continue
                            
                            # Adicionar categorias da família
                            for cat in family_categories:
                                if cat.id not in existing_ids:
                                    all_categories.append(cat)
                                    existing_ids.add(cat.id)
                        except Exception as e:
                            print(f"⚠️ Erro ao buscar categorias da família {family.id}: {e}")
                            continue
            except Exception as e:
                print(f"⚠️ Erro ao processar família {family.id}: {e}")
                continue
    except Exception as e:
        print(f"⚠️ Erro ao buscar categorias da família: {e}")
    
    return all_categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    use_cases: CategoryUseCases = Depends(get_category_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma categoria específica"""
    try:
        category = await use_cases.get_category(category_id)
        # Verificar se a categoria pertence ao usuário
        if category.user_id and category.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        return category
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    use_cases: CategoryUseCases = Depends(get_category_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza uma categoria"""
    try:
        # Verificar se a categoria pertence ao usuário
        category = await use_cases.get_category(category_id)
        if category.user_id and category.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        
        updated_category = await use_cases.update_category(
            category_id=category_id,
            name=category_data.name,
            description=category_data.description,
            category_type=category_data.category_type,
            icon=category_data.icon,
            color=category_data.color,
            is_active=category_data.is_active,
            parent_id=category_data.parent_id,
        )
        return updated_category
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    use_cases: CategoryUseCases = Depends(get_category_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta uma categoria"""
    try:
        # Verificar se a categoria pertence ao usuário
        category = await use_cases.get_category(category_id)
        if category.user_id and category.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        
        await use_cases.delete_category(category_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

