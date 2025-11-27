.PHONY: deploy-aws help

# Deploy na AWS
deploy-aws:
	@powershell -ExecutionPolicy Bypass -File .\scripts\deploy-direto-aws.ps1

# Ajuda
help:
	@echo "Comandos disponiveis:"
	@echo "  make deploy-aws  - Faz deploy completo na AWS"

