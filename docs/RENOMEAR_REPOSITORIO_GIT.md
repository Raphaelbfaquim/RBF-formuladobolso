# Como Renomear o Repositório no Git

## Opção 1: Renomear no GitHub (Recomendado)

### Passo 1: Renomear no GitHub
1. Acesse: https://github.com/Raphaelbfaquim/RBF-formuladobolso
2. Vá em **Settings** → **General**
3. Role até **Repository name**
4. Altere de `RBF-formuladobolso` para `RBF`
5. Clique em **Rename**

### Passo 2: Atualizar Remote Local
```powershell
# Verificar remote atual
git remote -v

# Atualizar URL do remote
git remote set-url origin https://github.com/Raphaelbfaquim/RBF.git

# Verificar se foi atualizado
git remote -v
```

### Passo 3: Atualizar no Servidor
```bash
# Conectar no servidor
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@3.238.162.190

# Atualizar remote
cd ~/RBF/formuladobolso
git remote set-url origin https://github.com/Raphaelbfaquim/RBF.git

# Verificar
git remote -v
```

## Opção 2: Manter Nome do Repositório, Mudar Estrutura Local

Se você **NÃO** quiser renomear o repositório no GitHub, pode manter o nome `RBF-formuladobolso` e apenas reorganizar a estrutura local.

### Estrutura no GitHub (mantém):
```
RBF-formuladobolso/  (repositório)
├── back/
├── front/
├── sites/  (ou sites-marketing/)
└── ...
```

### Estrutura Local (reorganizada):
```
RBF/
├── sites-marketing/
└── formuladobolso/  (clone do repositório RBF-formuladobolso)
    ├── back/
    ├── front/
    └── ...
```

### Como Fazer:
```powershell
# 1. Criar estrutura
cd C:\Users\rapha\OneDrive\Documents\src
mkdir RBF
cd RBF
mkdir sites-marketing

# 2. Clonar repositório em formuladobolso/
cd ..
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git RBF\formuladobolso

# 3. Mover sites para sites-marketing
cd RBF\formuladobolso
xcopy /E /I sites ..\sites-marketing
rmdir /S /Q sites

# 4. Commitar remoção da pasta sites
git add .
git commit -m "Reorganização: sites movido para estrutura externa"
git push
```

## Opção 3: Criar Novo Repositório para Sites

Se você quiser separar completamente:

### Repositório 1: `RBF` (projeto principal)
```
RBF/
└── formuladobolso/
    ├── back/
    ├── front/
    └── ...
```

### Repositório 2: `RBF-sites-marketing` (sites)
```
RBF-sites-marketing/
├── formula-bolso/
└── pessoal/
```

### Como Fazer:
```powershell
# 1. Criar novo repositório no GitHub: RBF-sites-marketing

# 2. Criar estrutura local
cd C:\Users\rapha\OneDrive\Documents\src
mkdir RBF
cd RBF
mkdir sites-marketing

# 3. Mover sites e inicializar novo repo
cd ..\RBF-formuladobolso
xcopy /E /I sites ..\RBF\sites-marketing
cd ..\RBF\sites-marketing
git init
git add .
git commit -m "Initial commit: sites de marketing"
git remote add origin https://github.com/Raphaelbfaquim/RBF-sites-marketing.git
git push -u origin main

# 4. Remover sites do repo principal
cd ..\RBF-formuladobolso
rmdir /S /Q sites
git add .
git commit -m "Sites movidos para repositório separado"
git push
```

## Recomendação

**Opção 1** é a mais simples se você quer manter tudo no mesmo repositório:
- Renomeia o repositório no GitHub
- Atualiza os remotes
- Mantém histórico completo
- Não precisa criar novos repositórios

## Atualizar Scripts Após Renomear

Se renomear o repositório, atualize:

### `scripts/deploy-aws-dockerhub.sh`
```bash
# ANTES:
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git

# DEPOIS:
git clone https://github.com/Raphaelbfaquim/RBF.git formuladobolso
```

### `deploy-server.ps1`
```powershell
# Já está usando caminho ~/RBF/formuladobolso, então não precisa mudar
# Mas se o repositório for renomeado, o clone precisa ser ajustado
```

## Verificar Tudo Está Funcionando

```powershell
# Local
git remote -v
git pull

# Servidor (via SSH)
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@3.238.162.190
cd ~/RBF/formuladobolso
git remote -v
git pull
```

