from typing import List, Optional
from uuid import UUID
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.database.models.category import Category, CategoryType
from src.shared.exceptions import NotFoundException, ValidationException


class CategoryUseCases:
    """Casos de uso para gerenciamento de categorias"""

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    async def create_category(
        self,
        name: str,
        category_type: str,
        user_id: UUID,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        parent_id: Optional[UUID] = None,
    ) -> Category:
        """Cria uma nova categoria"""
        # Validar tipo de categoria
        try:
            CategoryType(category_type)
        except ValueError:
            raise ValidationException(f"Tipo de categoria inválido: {category_type}")

        # Validar parent se fornecido
        if parent_id:
            parent = await self.category_repository.get_by_id(parent_id)
            if not parent:
                raise NotFoundException("Categoria pai", str(parent_id))

        category = Category(
            name=name,
            description=description,
            category_type=CategoryType(category_type),
            icon=icon,
            color=color,
            user_id=user_id,
            parent_id=parent_id,
            is_active=True,
        )

        return await self.category_repository.create(category)

    async def get_category(self, category_id: UUID) -> Category:
        """Obtém uma categoria por ID"""
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise NotFoundException("Categoria", str(category_id))
        return category

    async def get_user_categories(self, user_id: UUID) -> List[Category]:
        """Obtém todas as categorias do usuário"""
        return await self.category_repository.get_by_user_id(user_id)

    async def update_category(
        self,
        category_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category_type: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[UUID] = None,
    ) -> Category:
        """Atualiza uma categoria"""
        category = await self.get_category(category_id)

        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if category_type is not None:
            try:
                category.category_type = CategoryType(category_type)
            except ValueError:
                raise ValidationException(f"Tipo de categoria inválido: {category_type}")
        if icon is not None:
            category.icon = icon
        if color is not None:
            category.color = color
        if is_active is not None:
            category.is_active = is_active
        if parent_id is not None:
            if parent_id:
                parent = await self.category_repository.get_by_id(parent_id)
                if not parent:
                    raise NotFoundException("Categoria pai", str(parent_id))
            category.parent_id = parent_id

        return await self.category_repository.update(category)

    async def delete_category(self, category_id: UUID) -> bool:
        """Deleta uma categoria (soft delete)"""
        category = await self.get_category(category_id)
        return await self.category_repository.delete(category_id)

