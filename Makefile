.PHONY: help install-back install-front dev-back dev-front deploy deploy-front deploy-back setup

help:
	@echo "💰 FormuladoBolso - Comandos disponíveis:"
	@echo ""
	@echo "📦 Instalação:"
	@echo "  make install-back    - Instalar dependências do backend"
	@echo "  make install-front   - Instalar dependências do frontend"
	@echo "  make install         - Instalar tudo"
	@echo ""
	@echo "🚀 Desenvolvimento:"
	@echo "  make dev-back        - Rodar backend (porta 8000)"
	@echo "  make dev-front       - Rodar frontend (porta 3000)"
	@echo "  make dev             - Rodar backend e frontend"
	@echo ""
	@echo "🌐 Deploy:"
	@echo "  make deploy-free     - Deploy 100% GRATUITO (Railway + Vercel + Supabase)"
	@echo "  make deploy          - Deploy completo (interativo)"
	@echo "  make deploy-front    - Deploy apenas frontend (Vercel - Gratuito)"
	@echo "  make deploy-back     - Deploy apenas backend (Render/Railway)"
	@echo "  make deploy-oracle   - Deploy na Oracle Cloud (via SSH local)"
	@echo ""
	@echo "🐳 Docker Hub (Recomendado - Build local + Push):"
	@echo "  make docker-build    - Buildar imagens localmente e fazer push para Docker Hub"
	@echo "  make docker-deploy   - Deploy na AWS usando imagens do Docker Hub (mais rápido!)"
	@echo ""
	@echo "💡 Dica: Configure GitHub Actions para deploy automático!"
	@echo "   Veja: docs/GITHUB_ACTIONS_SETUP.md"
	@echo ""
	@echo "🧪 Testes:"
	@echo "  make test            - Testar sistema (backend + frontend)"
	@echo "  make test-api        - Testar API completa"
	@echo ""
	@echo "🔧 Utilitários:"
	@echo "  make setup           - Setup inicial completo"
	@echo "  make migrate         - Executar migrações do banco"
	@echo "  make check-users     - Verificar usuários no banco"
	@echo "  make clean           - Limpar arquivos temporários"

install-back:
	@echo "📦 Instalando dependências do backend..."
	cd back && python3 -m venv venv || true
	cd back && source venv/bin/activate && pip install -r requirements.txt

install-front:
	@echo "📦 Instalando dependências do frontend..."
	cd front && npm install

install: install-back install-front
	@echo "✅ Instalação completa!"

dev-back:
	@echo "🚀 Iniciando backend..."
	cd back && source venv/bin/activate && uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000

dev-front:
	@echo "🚀 Iniciando frontend..."
	cd front && npm run dev

dev:
	@echo "🚀 Iniciando backend e frontend..."
	@make dev-back & make dev-front

deploy-free:
	@echo "🆓 Deploy 100% GRATUITO..."
	@bash scripts/deploy-free.sh

deploy:
	@echo "🌐 Iniciando deploy..."
	@bash scripts/deploy.sh

deploy-front:
	@echo "🌐 Deploy do frontend na Vercel..."
	cd front && vercel --prod

deploy-back:
	@echo "🌐 Configuração do backend no Render..."
	@echo "📝 Acesse https://render.com e configure manualmente"
	@echo "📄 Use o arquivo back/render.yaml como referência"

deploy-oracle:
	@echo "☁️  Deploy na Oracle Cloud..."
	@echo "📝 Este comando deve ser executado na instância Oracle Cloud"
	@echo "📄 Veja o guia completo em: docs/DEPLOY_ORACLE.md"
	@bash scripts/deploy-oracle.sh

docker-build:
	@echo "🐳 Buildando imagens e fazendo push para Docker Hub..."
	@echo "💡 Certifique-se de estar logado: docker login"
	@bash scripts/build-and-push.sh

docker-deploy:
	@echo "🚀 Deploy na AWS usando imagens do Docker Hub..."
	@echo "💡 Configure DOCKER_USERNAME e DOCKER_PASSWORD"
	@bash scripts/deploy-aws-images.sh

setup:
	@echo "🔧 Setup inicial..."
	@make install
	@echo "✅ Setup completo!"
	@echo "📝 Configure o arquivo back/.env com suas credenciais"
	@echo "📝 Configure o arquivo front/.env.local com NEXT_PUBLIC_API_URL"

migrate:
	@echo "🗄️  Executando migrações..."
	cd back && source venv/bin/activate && alembic upgrade head

check-users:
	@echo "👥 Verificando usuários no banco de dados..."
	@source venv/bin/activate && python scripts/check_users.py

test:
	@echo "🧪 Testando sistema..."
	@bash scripts/test_system.sh

test-api:
	@echo "🧪 Testando API..."
	@bash scripts/test_api.sh

clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "node_modules" -prune -exec rm -r {} + 2>/dev/null || true
	@echo "✅ Limpeza concluída!"
