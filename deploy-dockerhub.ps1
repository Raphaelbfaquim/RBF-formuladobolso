# Script de deploy AWS via Docker Hub - Atalho na raiz do projeto
# Uso: .\deploy-dockerhub.ps1 [api|front|all]
#      api   - Deploy apenas da API
#      front - Deploy apenas do Frontend
#      all   - Deploy de ambos (padrao)

param(
    [string]$service = "all"
)

& "$PSScriptRoot\scripts\deploy-aws-images.ps1" -service $service

