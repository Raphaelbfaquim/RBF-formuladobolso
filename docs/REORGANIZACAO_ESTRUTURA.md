# Mapeamento Completo: Reorganização da Estrutura de Pastas

## Estrutura Atual
```
RBF-formuladobolso/
├── back/
├── front/
├── sites/
│   ├── formula-bolso/
│   └── pessoal/
├── nginx/
├── scripts/
├── docker-compose.prod.yml
└── ...
```

## Estrutura Desejada
```
RBF/
├── sites-marketing/
│   ├── formula-bolso/
│   └── pessoal/
└── formuladobolso/
    ├── back/
    ├── front/
    ├── nginx/
    ├── scripts/
    ├── docker-compose.prod.yml
    └── ...
```

## Arquivos que Precisam ser Alterados

### 1. Scripts PowerShell (Local)

#### 1.1. `deploy-build-push.ps1`
**Linha 86:** Caminho do Dockerfile do marketing
```powershell
# ANTES:
docker build -t ${DOCKER_USERNAME}/formulado-marketing:${IMAGE_TAG} -f sites/formula-bolso/Dockerfile sites/formula-bolso/

# DEPOIS:
docker build -t ${DOCKER_USERNAME}/formulado-marketing:${IMAGE_TAG} -f ../sites-marketing/formula-bolso/Dockerfile ../sites-marketing/formula-bolso/
```

#### 1.2. `deploy-server.ps1`
**Linha 49:** Caminho do git pull no servidor
```powershell
# ANTES:
& ssh ... "cd ~/RBF-formuladobolso && git fetch origin ..."

# DEPOIS:
& ssh ... "cd ~/RBF/formuladobolso && git fetch origin ..."
```

**Linha 53-54:** Caminhos dos arquivos enviados via SCP
```powershell
# ANTES:
& scp ... "docker-compose.prod.yml" "${AWS_HOST}:~/RBF-formuladobolso/docker-compose.prod.yml"
& scp ... "nginx\nginx.conf" "${AWS_HOST}:~/RBF-formuladobolso/nginx/nginx.conf"

# DEPOIS:
& scp ... "docker-compose.prod.yml" "${AWS_HOST}:~/RBF/formuladobolso/docker-compose.prod.yml"
& scp ... "nginx\nginx.conf" "${AWS_HOST}:~/RBF/formuladobolso/nginx/nginx.conf"
```

**Linha 74:** Caminho do docker-compose ps
```powershell
# ANTES:
& ssh ... "cd ~/RBF-formuladobolso && docker-compose -f docker-compose.prod.yml ps"

# DEPOIS:
& ssh ... "cd ~/RBF/formuladobolso && docker-compose -f docker-compose.prod.yml ps"
```

**Linha 87:** Caminho do docker-compose up
```powershell
# ANTES:
& ssh ... "cd ~/RBF-formuladobolso && docker-compose -f docker-compose.prod.yml up -d marketing"

# DEPOIS:
& ssh ... "cd ~/RBF/formuladobolso && docker-compose -f docker-compose.prod.yml up -d marketing"
```

#### 1.3. `run-migration.ps1`
**Linha 20:** Caminho do docker-compose exec
```powershell
# ANTES:
$migrationCmd = "cd ~/RBF-formuladobolso && docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head"

# DEPOIS:
$migrationCmd = "cd ~/RBF/formuladobolso && docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head"
```

#### 1.4. `scripts/add-new-site.ps1`
**Linha 30:** Caminho base dos sites
```powershell
# ANTES:
$sitePath = "sites\$siteName"

# DEPOIS:
$sitePath = "..\sites-marketing\$siteName"
```

**Todas as referências a `$sitePath`** precisam ser ajustadas para caminhos relativos corretos.

### 2. Scripts Bash (Servidor)

#### 2.1. `scripts/deploy-aws-dockerhub.sh`
**Linha 5-9:** Caminho do diretório no servidor
```bash
# ANTES:
cd ~/RBF-formuladobolso || {
  echo "📦 Clonando repositório..."
  cd ~
  git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
  cd RBF-formuladobolso
}

# DEPOIS:
cd ~/RBF/formuladobolso || {
  echo "📦 Clonando repositório..."
  cd ~/RBF
  git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git formuladobolso
  cd formuladobolso
}
```

### 3. Dockerfiles

#### 3.1. `sites/formula-bolso/Dockerfile`
**Nenhuma alteração necessária** - caminhos são relativos ao contexto do build.

**MAS:** O comando de build precisa ser ajustado:
```powershell
# ANTES (executado de RBF-formuladobolso/):
docker build -f sites/formula-bolso/Dockerfile sites/formula-bolso/

# DEPOIS (executado de RBF/formuladobolso/):
docker build -f ../sites-marketing/formula-bolso/Dockerfile ../sites-marketing/formula-bolso/
```

#### 3.2. `back/docker/Dockerfile`
**Nenhuma alteração necessária** - caminhos são relativos.

#### 3.3. `front/Dockerfile`
**Nenhuma alteração necessária** - caminhos são relativos.

### 4. Docker Compose

#### 4.1. `docker-compose.prod.yml`
**Nenhuma alteração necessária** - não há volumes que referenciem caminhos absolutos.

#### 4.2. `docker-compose.yml` (desenvolvimento)
**Verificar volumes locais** - se houver referências a caminhos relativos, podem precisar ajuste.

### 5. Nginx

#### 5.1. `nginx/nginx.conf`
**Nenhuma alteração necessária** - configuração é relativa ao container.

### 6. Documentação

#### 6.1. `docs/TROUBLESHOOTING_DEPLOY.md`
**Linhas 65, 73, 93, 159, 173:** Atualizar caminhos
```bash
# ANTES:
cd ~/RBF-formuladobolso

# DEPOIS:
cd ~/RBF/formuladobolso
```

#### 6.2. `docs/DEPLOY_MANUAL_AWS.md`
**Linhas 15, 20, 21, 27, 50, 68:** Atualizar caminhos
```bash
# ANTES:
cd ~/RBF-formuladobolso
git clone ... RBF-formuladobolso

# DEPOIS:
cd ~/RBF
git clone ... RBF-formuladobolso formuladobolso
cd formuladobolso
```

#### 6.3. `docs/DEPLOY_TUDO_AWS.md`
**Linha 61:** Atualizar caminho
```bash
# ANTES:
cd ~/RBF-formuladobolso

# DEPOIS:
cd ~/RBF/formuladobolso
```

#### 6.4. `docs/AWS_SETUP.md`
**Linhas 209-210:** Atualizar caminhos
```bash
# ANTES:
git clone ... RBF-formuladobolso.git
cd RBF-formuladobolso/back

# DEPOIS:
cd ~/RBF
git clone ... RBF-formuladobolso.git formuladobolso
cd formuladobolso/back
```

#### 6.5. `docs/DEPLOY_SIMPLES.md`
**Linha 83:** Atualizar caminho de exemplo
```markdown
# ANTES:
- Na pasta do projeto: `C:\Users\rapha\OneDrive\Documents\src\RBF-formuladobolso`

# DEPOIS:
- Na pasta do projeto: `C:\Users\rapha\OneDrive\Documents\src\RBF\formuladobolso`
```

#### 6.6. `sites/README.md`
**Todas as referências a caminhos** precisam ser atualizadas:
```markdown
# ANTES:
docker build -f sites/nome-da-loja/Dockerfile sites/nome-da-loja/

# DEPOIS:
docker build -f ../sites-marketing/nome-da-loja/Dockerfile ../sites-marketing/nome-da-loja/
```

#### 6.7. `sites/TEMPLATE.md`
**Todas as referências a caminhos** precisam ser atualizadas.

#### 6.8. `deploy.txt`
**Nenhuma alteração necessária** - comandos são relativos.

### 7. Git

#### 7.1. Repositório Remoto
**Nenhuma alteração necessária** - o repositório pode manter o nome `RBF-formuladobolso`.

**MAS:** No servidor, o clone precisa ser ajustado:
```bash
# ANTES:
cd ~
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso

# DEPOIS:
cd ~/RBF
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git formuladobolso
cd formuladobolso
```

### 8. Outros Arquivos

#### 8.1. `.gitignore`
**Verificar se há caminhos específicos** que precisam ser atualizados.

#### 8.2. `README.md`
**Atualizar exemplos de caminhos** se houver.

#### 8.3. `Makefile`
**Verificar comandos** que referenciam caminhos.

#### 8.4. `start-system.sh`
**Verificar caminhos** se houver.

## Passos para Executar a Reorganização

### Passo 1: Preparação Local
1. Criar estrutura de pastas:
   ```powershell
   cd C:\Users\rapha\OneDrive\Documents\src
   mkdir RBF
   cd RBF
   mkdir sites-marketing
   ```

2. Mover sites:
   ```powershell
   cd RBF-formuladobolso
   xcopy /E /I sites ..\RBF\sites-marketing
   ```

3. Mover projeto principal (sem a pasta sites):
   ```powershell
   cd RBF-formuladobolso
   # Remover pasta sites antes de mover (já foi copiada)
   rmdir /S /Q sites
   cd ..
   move RBF-formuladobolso RBF\formuladobolso
   ```

### Passo 2: Atualizar Arquivos Locais
1. Atualizar todos os scripts PowerShell listados acima
2. Atualizar todos os scripts Bash listados acima
3. Atualizar toda a documentação listada acima

### Passo 3: Atualizar Servidor
1. Conectar via SSH
2. Criar estrutura:
   ```bash
   cd ~
   mkdir -p RBF
   ```
3. Mover repositório existente:
   ```bash
   # Criar estrutura
   mkdir -p ~/RBF/sites-marketing
   # Mover sites
   mv ~/RBF-formuladobolso/sites/* ~/RBF/sites-marketing/
   # Mover projeto (sem sites)
   mv ~/RBF-formuladobolso ~/RBF/formuladobolso
   ```
4. Verificar estrutura:
   ```bash
   # Estrutura final deve ser:
   # ~/RBF/sites-marketing/formula-bolso/
   # ~/RBF/formuladobolso/back/
   # ~/RBF/formuladobolso/front/
   # etc.
   ```

### Passo 4: Testar
1. Testar build local:
   ```powershell
   cd RBF\formuladobolso
   # Verificar se o caminho ../sites-marketing/formula-bolso existe
   powershell -ExecutionPolicy Bypass -File .\deploy-build-push.ps1 marketing
   ```

2. Testar deploy:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\deploy-server.ps1 all
   ```

## Resumo de Alterações

### Total de Arquivos a Alterar: ~15-20 arquivos

**Scripts PowerShell:** 4 arquivos
- deploy-build-push.ps1
- deploy-server.ps1
- run-migration.ps1
- scripts/add-new-site.ps1

**Scripts Bash:** 1 arquivo
- scripts/deploy-aws-dockerhub.sh

**Documentação:** 8 arquivos
- docs/TROUBLESHOOTING_DEPLOY.md
- docs/DEPLOY_MANUAL_AWS.md
- docs/DEPLOY_TUDO_AWS.md
- docs/AWS_SETUP.md
- docs/DEPLOY_SIMPLES.md
- sites/README.md
- sites/TEMPLATE.md
- README.md (se necessário)

**Outros:** 2-3 arquivos
- Makefile (se necessário)
- start-system.sh (se necessário)
- .gitignore (se necessário)

## Esforço Estimado

- **Tempo:** 1-2 horas
- **Complexidade:** Média
- **Risco:** Baixo (todos os caminhos são mapeados)
- **Testes Necessários:** Build local, deploy no servidor

## Observações Importantes

1. **Backup:** Fazer backup antes de iniciar
2. **Git:** Commitar mudanças antes de reorganizar
3. **Servidor:** Atualizar servidor após reorganização local
4. **Testes:** Testar cada script após alteração
5. **Documentação:** Atualizar README principal se necessário

