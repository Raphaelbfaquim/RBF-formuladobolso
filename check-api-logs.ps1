# Verificar logs da API no servidor
$AWS_HOST = "ubuntu@3.238.162.190"
$SSH_KEY = "$env:USERPROFILE\.ssh\LightsailDefaultKey-us-east-1.pem"

Write-Host "Verificando logs da API..." -ForegroundColor Cyan
& ssh -i $SSH_KEY -o StrictHostKeyChecking=no $AWS_HOST "docker logs formulado_api --tail 50"

