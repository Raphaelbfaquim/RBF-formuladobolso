"""
Configuração global para testes
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.presentation.api.main import app
from src.infrastructure.database.base import Base, get_db

# URL do banco de dados de teste (SQLite em memória para testes rápidos)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Engine de teste
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Session factory de teste
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
async def db_session():
    """Cria uma sessão de banco de dados para cada teste"""
    # Criar todas as tabelas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Criar sessão
    async with TestSessionLocal() as session:
        yield session
    
    # Limpar após o teste
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session):
    """Cria um cliente de teste FastAPI"""
    # Substituir a dependência get_db pela sessão de teste
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpar override após o teste
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Dados de teste para criação de usuário"""
    return {
        "email": "usuario@teste.com.br",
        "username": "teste",
        "password": "senha123456",
        "full_name": "Usuário Teste"
    }
