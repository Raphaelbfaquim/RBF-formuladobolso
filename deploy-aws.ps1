# Script de deploy AWS - Atalho na raiz do projeto
# Uso: .\deploy-aws.ps1 [api|front|all]
#      api   - Deploy apenas da API
#      front - Deploy apenas do Frontend  
#      all   - Deploy de ambos (padrao)

param(
    [string]$service = "all"
)

& "$PSScriptRoot\scripts\deploy-direto-aws.ps1" -service $service

