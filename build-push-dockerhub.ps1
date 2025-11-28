# Script de build e push para Docker Hub - Atalho na raiz do projeto
# Uso: .\build-push-dockerhub.ps1 [api|front|all]
#      api   - Build e push apenas da API
#      front - Build e push apenas do Frontend
#      all   - Build e push de ambos (padrao)

param(
    [string]$service = "all"
)

& "$PSScriptRoot\scripts\build-and-push-dockerhub.ps1" -service $service

