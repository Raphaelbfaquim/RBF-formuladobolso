from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.models.user import User
from src.infrastructure.database.models.education import (
    EducationalContent,
    UserProgress,
    Quiz,
    QuizAttempt,
    ContentType,
)
from src.infrastructure.database.base import get_db
import json
from datetime import datetime
import pytz

router = APIRouter()


# ========== Help Content (Ajuda da Aplicação) ==========

@router.get("/help")
async def get_help_content(
    topic: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém conteúdo de ajuda da aplicação"""
    try:
        # Conteúdo de ajuda pré-definido (pode vir do banco no futuro)
        help_content = {
        "dashboard": {
            "title": "📊 Dashboard - Sua Central Financeira",
            "description": "Bem-vindo ao seu painel de controle financeiro! Aqui você tem uma visão completa e organizada de todas as suas finanças.",
            "icon": "📊",
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
            "content": """
# 📊 Dashboard - Sua Central Financeira

Olá! 👋 Bem-vindo ao seu **Dashboard**, o coração do FormuladoBolso! Aqui você encontra tudo que precisa para entender sua situação financeira de forma rápida e clara.

## 🎯 O que você encontra aqui?

### 💰 Indicadores Principais (KPIs)
No topo da página, você verá quatro cartões importantes:

- **💵 Saldo Total**: A soma de todas as suas contas ativas. É o dinheiro que você tem disponível agora!
- **📈 Receitas do Mês**: Todo o dinheiro que entrou este mês. Seu salário, vendas, e outras receitas.
- **📉 Despesas do Mês**: Todo o dinheiro que saiu este mês. Gastos, contas, e compras.
- **💚 Economia**: A diferença entre receitas e despesas. Quanto você conseguiu economizar!

> 💡 **Dica**: Uma economia positiva significa que você está no caminho certo! Se estiver negativa, é hora de revisar seus gastos.

### 📊 Gráficos Interativos

**Evolução Mensal**
- Veja como suas receitas e despesas mudam ao longo do tempo
- Identifique tendências e padrões
- Perfeito para planejar o futuro!

**Distribuição por Categoria**
- Entenda visualmente onde você mais gasta
- Descubra se está gastando demais em alguma área
- Use essas informações para ajustar seu orçamento

### 📝 Últimas Transações
Acompanhe suas transações mais recentes diretamente no dashboard, sem precisar navegar para outra página.

## 🚀 Como usar?

1. **Acompanhe diariamente**: Visite o dashboard todos os dias para manter o controle
2. **Analise os gráficos**: Use os gráficos para identificar padrões
3. **Ajuste conforme necessário**: Se algo não estiver como esperado, faça ajustes nas suas transações ou planejamento

> ✨ **Lembre-se**: O dashboard é atualizado em tempo real! Sempre que você adicionar uma transação, ela aparecerá aqui automaticamente.
            """,
            "tips": [
                "Visite o dashboard diariamente para manter o controle",
                "Use os gráficos para identificar padrões de gastos",
                "Compare mês a mês para ver sua evolução"
            ],
            "video_url": None,
        },
        "transactions": {
            "title": "💸 Transações - Registre Tudo",
            "description": "Aprenda a registrar e gerenciar todas as suas movimentações financeiras de forma simples e organizada.",
            "icon": "💸",
            "image": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800",
            "content": """
# 💸 Transações - O Coração do Seu Controle

As transações são como o diário da sua vida financeira! Cada entrada e saída de dinheiro deve ser registrada aqui para você ter controle total.

## ✨ Por que registrar transações?

- 📊 **Controle total**: Saiba exatamente para onde vai seu dinheiro
- 🎯 **Tomada de decisão**: Dados reais para decidir melhor
- 📈 **Análise de padrões**: Entenda seus hábitos de consumo
- 💰 **Economia**: Identifique onde pode economizar

## ➕ Como criar uma transação?

É super simples! Siga estes passos:

### Passo 1: Acesse a página de Transações
Clique em **"Transações"** no menu lateral e depois em **"Nova Transação"**.

### Passo 2: Preencha os dados

**📝 Descrição** (obrigatório)
- Seja claro e específico
- Exemplos: "Almoço no restaurante", "Salário mensal", "Conta de luz"

**💰 Valor** (obrigatório)
- Digite o valor exato
- Use ponto para decimais (ex: 150.50)

**📊 Tipo** (obrigatório)
- **Receita**: Dinheiro que entra (salário, vendas, etc.)
- **Despesa**: Dinheiro que sai (compras, contas, etc.)

**📅 Data** (obrigatório)
- Selecione a data da transação
- Por padrão, usa a data de hoje

**🏦 Conta** (obrigatório)
- Escolha em qual conta a transação aconteceu
- Pode ser conta corrente, poupança, cartão, etc.

**📁 Categoria** (opcional, mas recomendado!)
- Organize seus gastos por categoria
- Facilita muito na hora de analisar relatórios
- Exemplos: Alimentação, Transporte, Saúde, Lazer

### Passo 3: Salvar
Clique em **"Salvar"** e pronto! Sua transação foi registrada. 🎉

## ✏️ Como editar uma transação?

1. Na lista de transações, encontre a que deseja editar
2. Clique no ícone de **lápis** (✏️) ou no botão **"Editar"**
3. Modifique os campos que precisar
4. Clique em **"Salvar"**

> 💡 **Dica**: Você pode editar qualquer transação, mas tente fazer isso logo após criar, para manter os dados sempre atualizados!

## 🔍 Como filtrar transações?

Use os filtros no topo da página para encontrar transações específicas:

- **📅 Por Período**: Veja transações de um mês, semana ou período específico
- **📊 Por Tipo**: Filtre apenas receitas ou apenas despesas
- **📁 Por Categoria**: Veja todos os gastos de uma categoria específica
- **🏦 Por Conta**: Filtre por conta bancária

## 💡 Dicas Pro

- ✅ **Registre imediatamente**: Não deixe para depois! Registre assim que fizer uma compra
- 📸 **Use descrições claras**: Facilita encontrar transações depois
- 🏷️ **Sempre use categorias**: Ajuda muito na análise de gastos
- 🔄 **Revise regularmente**: Dê uma olhada nas transações da semana para manter o controle

> 🎯 **Meta**: Tente registrar pelo menos 90% das suas transações. Quanto mais completo, melhor será sua análise financeira!
            """,
            "tips": [
                "Registre transações imediatamente após fazer uma compra",
                "Use descrições claras e específicas",
                "Sempre categorize suas transações para melhor análise",
                "Revise suas transações semanalmente"
            ],
            "video_url": None,
        },
        "accounts": {
            "title": "🏦 Contas - Organize Seu Dinheiro",
            "description": "Gerencie todas as suas contas bancárias, cartões e dinheiro em um só lugar. Tenha controle total sobre onde está seu dinheiro!",
            "icon": "🏦",
            "image": "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=800",
            "content": """
# 🏦 Contas - Organize Seu Dinheiro

Ter múltiplas contas pode ser confuso, mas não aqui! No FormuladoBolso você gerencia todas as suas contas em um só lugar, de forma simples e organizada.

## 🎯 Por que cadastrar suas contas?

- 📊 **Visão completa**: Veja todos os seus saldos em um só lugar
- 💰 **Controle total**: Saiba exatamente quanto tem em cada conta
- 🔄 **Transferências fáceis**: Mova dinheiro entre contas com um clique
- 📈 **Análise completa**: Relatórios consideram todas as suas contas

## ➕ Como criar uma conta?

### Passo 1: Acesse Contas
Clique em **"Contas"** no menu lateral e depois em **"Nova Conta"**.

### Passo 2: Preencha as informações

**📝 Nome da Conta** (obrigatório)
- Escolha um nome que você reconheça facilmente
- Exemplos: "Conta Nubank", "Poupança Itaú", "Cartão Visa"

**🏦 Tipo de Conta** (obrigatório)
Escolha o tipo que melhor descreve sua conta:

- **💳 Conta Corrente**: Para uso diário, pagamentos e recebimentos
- **💰 Poupança**: Para suas economias e reservas
- **💳 Cartão de Crédito**: Para controlar faturas e limites
- **💵 Dinheiro**: Para dinheiro físico que você guarda
- **🏛️ Outros**: Para outros tipos de conta

**💵 Saldo Inicial** (opcional)
- Digite quanto você tem nesta conta agora
- Se deixar em branco, começará com R$ 0,00
- Você pode ajustar depois se precisar!

**🏪 Banco** (opcional)
- Nome do banco ou instituição financeira
- Exemplos: "Nubank", "Itaú", "Bradesco", "XP Investimentos"

**📄 Descrição** (opcional)
- Adicione informações extras se quiser
- Exemplo: "Conta principal para receber salário"

### Passo 3: Salvar
Clique em **"Salvar"** e sua conta estará pronta para uso! 🎉

## 📋 Tipos de Conta Explicados

### 💳 Conta Corrente
- Use para: Receber salário, fazer pagamentos, transferências
- Ideal para: Uso diário e movimentações frequentes
- 💡 Dica: Mantenha apenas o necessário para o dia a dia

### 💰 Poupança
- Use para: Guardar dinheiro, reserva de emergência, objetivos
- Ideal para: Economias e dinheiro que não será usado imediatamente
- 💡 Dica: Separe diferentes poupanças por objetivo (ex: "Poupança Emergência", "Poupança Viagem")

### 💳 Cartão de Crédito
- Use para: Controlar faturas e limites
- Ideal para: Acompanhar gastos no cartão
- 💡 Dica: Registre as compras como despesas e o pagamento da fatura como transferência

### 💵 Dinheiro
- Use para: Dinheiro físico que você guarda
- Ideal para: Reserva em casa, dinheiro para emergências
- 💡 Dica: Não esqueça de atualizar quando usar ou guardar dinheiro

## 🔄 Transferências Entre Contas

Precisa mover dinheiro de uma conta para outra? É fácil!

1. Vá em **"Transferências"** no menu
2. Clique em **"Nova Transferência"**
3. Escolha:
   - **De**: Conta de origem (de onde sai o dinheiro)
   - **Para**: Conta de destino (para onde vai o dinheiro)
   - **Valor**: Quanto você quer transferir
4. Clique em **"Transferir"**

> 💡 **Importante**: As transferências atualizam automaticamente os saldos das contas envolvidas!

## ✏️ Gerenciando suas contas

- **Editar**: Clique no botão de editar para modificar informações
- **Desativar**: Se não usar mais uma conta, desative-a em vez de deletar (mantém histórico)
- **Visualizar**: Veja todas as transações de uma conta específica

## 💡 Dicas Pro

- ✅ **Cadastre todas as contas**: Quanto mais completo, melhor o controle
- 🔄 **Atualize saldos regularmente**: Mantenha os saldos sempre atualizados
- 📊 **Use nomes claros**: Facilita identificar cada conta rapidamente
- 🎯 **Organize por propósito**: Separe contas por objetivo (ex: "Conta Pessoal", "Conta Negócio")

> 🎯 **Meta**: Cadastre todas as suas contas principais. Quanto mais completo, melhor será sua visão financeira!
            """,
            "tips": [
                "Cadastre todas as suas contas para ter visão completa",
                "Atualize os saldos regularmente",
                "Use nomes claros e fáceis de identificar",
                "Organize contas por propósito (pessoal, negócio, etc.)"
            ],
            "video_url": None,
        },
        "categories": {
            "title": "📁 Categorias - Organize Seus Gastos",
            "description": "Aprenda a organizar seus gastos por categorias e entenda melhor seus hábitos financeiros!",
            "icon": "📁",
            "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
            "content": """
# 📁 Categorias - Organize Seus Gastos

Categorias são como etiquetas para seus gastos! Elas ajudam você a entender exatamente onde seu dinheiro está indo e facilitam muito a análise financeira.

## 🎯 Por que usar categorias?

- 📊 **Análise clara**: Veja exatamente quanto gasta em cada área da vida
- 🎯 **Controle melhor**: Identifique onde pode economizar
- 📈 **Relatórios precisos**: Gere relatórios detalhados por categoria
- 💡 **Insights valiosos**: Descubra padrões nos seus gastos

## ➕ Como criar uma categoria?

### Passo 1: Acesse Categorias
Clique em **"Categorias"** no menu lateral e depois em **"Nova Categoria"**.

### Passo 2: Configure sua categoria

**📝 Nome** (obrigatório)
- Escolha um nome claro e descritivo
- Exemplos: "Alimentação", "Transporte", "Saúde", "Lazer"

**🎨 Cor** (recomendado)
- Escolha uma cor para identificar visualmente
- Facilita muito na hora de ver gráficos e relatórios
- Use cores diferentes para cada categoria

**🎯 Ícone** (opcional, mas divertido!)
- Escolha um emoji ou ícone que represente a categoria
- Exemplos: 🍔 para Alimentação, 🚗 para Transporte, 🏥 para Saúde

**📊 Tipo** (obrigatório)
- **Receita**: Para categorizar suas receitas (ex: "Salário", "Vendas")
- **Despesa**: Para categorizar seus gastos (ex: "Alimentação", "Transporte")

### Passo 3: Salvar
Clique em **"Salvar"** e sua categoria estará pronta! 🎉

## 📋 Categorias Sugeridas

Aqui estão algumas categorias comuns que você pode criar:

### 💰 Receitas
- **Salário**: Seu salário mensal
- **Freelance**: Trabalhos extras
- **Vendas**: Vendas de produtos ou serviços
- **Investimentos**: Rendimentos de investimentos
- **Outros**: Outras receitas

### 💸 Despesas Essenciais
- **🏠 Moradia**: Aluguel, condomínio, IPTU, água, luz, internet
- **🍔 Alimentação**: Supermercado, restaurantes, delivery
- **🚗 Transporte**: Combustível, transporte público, manutenção do carro
- **🏥 Saúde**: Médicos, remédios, plano de saúde, academia
- **👕 Vestuário**: Roupas, calçados, acessórios

### 🎯 Despesas Pessoais
- **🎬 Lazer**: Cinema, shows, viagens, hobbies
- **📚 Educação**: Cursos, livros, material escolar
- **💅 Beleza**: Salão, produtos de beleza, estética
- **🎁 Presentes**: Presentes para família e amigos

### 💼 Despesas Profissionais
- **💻 Tecnologia**: Software, equipamentos, cursos técnicos
- **📱 Comunicação**: Telefone, internet, serviços online

## 💡 Como usar categorias?

### Ao criar uma transação:
1. Preencha os dados da transação
2. No campo **"Categoria"**, escolha a categoria apropriada
3. Salve a transação

> 💡 **Dica**: Sempre categorize suas transações! Quanto mais organizado, melhor será sua análise.

### Visualizando por categoria:
- **Relatórios**: Veja gráficos de distribuição por categoria
- **Insights**: Receba análises sobre suas categorias de maior gasto
- **Planejamento**: Planeje gastos por categoria

## 🎨 Dicas de Organização

- ✅ **Seja específico**: Em vez de "Compras", use "Supermercado", "Farmácia", etc.
- 🎨 **Use cores diferentes**: Facilita identificar rapidamente
- 📊 **Agrupe quando fizer sentido**: Crie categorias principais e subcategorias
- 🔄 **Revise regularmente**: Ajuste categorias conforme sua vida muda

## 🚀 Categorias Inteligentes

O sistema pode sugerir categorias automaticamente baseado na descrição da transação. Use isso como ponto de partida e ajuste se necessário!

> 🎯 **Meta**: Categorize pelo menos 80% das suas transações. Isso fará uma diferença enorme na qualidade dos seus relatórios!
            """,
            "tips": [
                "Seja específico ao criar categorias (ex: 'Supermercado' em vez de 'Compras')",
                "Use cores diferentes para facilitar identificação visual",
                "Sempre categorize suas transações para melhor análise",
                "Revise e ajuste suas categorias periodicamente"
            ],
            "video_url": None,
        },
        "planning": {
            "title": "📅 Planejamento - Organize Seu Futuro",
            "description": "Planeje suas finanças com antecedência e alcance seus objetivos financeiros!",
            "icon": "📅",
            "image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800",
            "content": """
# 📅 Planejamento - Organize Seu Futuro

O planejamento financeiro é como um GPS para suas finanças! Ele te ajuda a saber exatamente quanto você pode gastar em cada área da vida, evitando surpresas desagradáveis no final do mês.

## 🎯 Por que planejar?

- 🎯 **Controle total**: Saiba exatamente quanto pode gastar em cada categoria
- 💰 **Evite dívidas**: Não gaste mais do que planejou
- 📊 **Acompanhe progresso**: Veja se está seguindo o planejado
- 🚀 **Alcance objetivos**: Planeje para alcançar suas metas financeiras

## ➕ Como criar um planejamento?

### Passo 1: Acesse Planejamento
Clique em **"Planejamento"** no menu lateral.

### Passo 2: Crie um novo planejamento
Clique em **"Novo Planejamento"** e preencha:

**📅 Período**
- Escolha o período do planejamento
- **Mensal**: Para planejamento mensal (mais comum)
- **Semanal**: Para controle semanal
- **Anual**: Para visão anual

**📁 Categoria**
- Escolha a categoria que deseja planejar
- Exemplos: Alimentação, Transporte, Lazer, etc.
- Você pode criar planejamentos para múltiplas categorias

**💰 Valor Planejado**
- Defina quanto você quer gastar nesta categoria
- Seja realista! Baseie-se nos seus gastos anteriores
- Use os insights para ter uma ideia melhor

**📅 Data**
- Selecione o período específico
- Para planejamento mensal, escolha o mês

### Passo 3: Salvar
Clique em **"Salvar"** e seu planejamento estará ativo! 🎉

## 📊 Acompanhando seu planejamento

Na página de Planejamento você verá:

- **📈 Gráfico de Comparação**: Veja quanto planejou vs quanto gastou
- **🎯 Progresso**: Percentual do planejamento já utilizado
- **⚠️ Alertas**: Avisos quando estiver próximo do limite
- **📋 Detalhes**: Veja todas as transações da categoria

> 💡 **Dica**: Revise seu planejamento mensalmente e ajuste conforme necessário. A vida muda, e seu planejamento pode mudar também!

## 💡 Dicas de Planejamento

- ✅ **Seja realista**: Não planeje valores muito baixos que você não conseguirá cumprir
- 📊 **Use dados históricos**: Veja quanto você gastou nos meses anteriores
- 🎯 **Priorize**: Dê mais espaço para categorias essenciais
- 🔄 **Ajuste quando necessário**: Planejamento não é prisão, é guia!

## 🎯 Regra 50/30/20 (Opcional)

Alguns usuários gostam de seguir a regra:
- **50%** para necessidades (moradia, alimentação, transporte)
- **30%** para desejos (lazer, entretenimento)
- **20%** para economia e investimentos

> 🎯 **Meta**: Tente seguir seu planejamento em pelo menos 80% das categorias. Isso já fará uma grande diferença!
            """,
            "tips": [
                "Seja realista ao definir valores planejados",
                "Use dados históricos para planejar melhor",
                "Revise e ajuste seu planejamento mensalmente",
                "Priorize categorias essenciais no planejamento"
            ],
            "video_url": None,
        },
        "goals": {
            "title": "🎯 Metas - Transforme Sonhos em Realidade",
            "description": "Defina metas financeiras claras e acompanhe seu progresso até alcançá-las!",
            "icon": "🎯",
            "image": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800",
            "content": """
# 🎯 Metas - Transforme Sonhos em Realidade

Metas são seus sonhos com prazo e valor! Elas transformam desejos vagos em objetivos concretos e alcançáveis. Com o FormuladoBolso, você pode definir, acompanhar e alcançar qualquer meta financeira.

## 🌟 Por que ter metas?

- 🎯 **Foco**: Você sabe exatamente para onde está indo
- 💪 **Motivação**: Ver o progresso te motiva a continuar
- 📊 **Planejamento**: Você sabe quanto precisa economizar
- 🎉 **Realização**: A sensação de alcançar uma meta é incrível!

## ➕ Como criar uma meta?

### Passo 1: Acesse Metas
Clique em **"Metas"** no menu lateral e depois em **"Nova Meta"**.

### Passo 2: Defina sua meta

**📝 Nome da Meta** (obrigatório)
- Escolha um nome inspirador e claro
- Exemplos: "Viagem para Europa", "Reserva de Emergência", "Entrada do Apartamento"

**💰 Valor Objetivo** (obrigatório)
- Quanto você precisa juntar?
- Seja específico e realista
- Exemplo: R$ 50.000 para entrada do apartamento

**📅 Data Limite** (opcional, mas recomendado!)
- Quando você quer alcançar esta meta?
- Ter um prazo ajuda a manter o foco
- O sistema calcula quanto você precisa economizar por mês

**🎯 Tipo de Meta** (opcional)
Escolha o tipo que melhor descreve sua meta:
- **🏠 Casa**: Comprar casa, reforma, móveis
- **🚗 Carro**: Compra de carro, manutenção
- **✈️ Viagem**: Viagens, férias, passeios
- **💍 Casamento**: Casamento, festa
- **📚 Educação**: Cursos, faculdade, especialização
- **🚨 Emergência**: Reserva de emergência
- **👴 Aposentadoria**: Planejamento para aposentadoria
- **🎯 Outros**: Outras metas

**📄 Descrição** (opcional)
- Adicione detalhes sobre sua meta
- Por que ela é importante para você?
- Isso ajuda a manter a motivação!

**🎨 Personalize** (opcional)
- Escolha uma cor e ícone para sua meta
- Facilita identificar visualmente

### Passo 3: Salvar
Clique em **"Salvar"** e sua meta estará criada! 🎉

## 💰 Como contribuir para sua meta?

### Contribuição Manual
1. Na página da meta, clique em **"Adicionar Contribuição"**
2. Digite o valor que você está adicionando
3. Escolha a conta de origem
4. Clique em **"Adicionar"**

### Contribuição Automática
Você pode configurar contribuições automáticas:
- **Porcentagem das receitas**: Ex: 10% de cada receita vai para a meta
- **Valor fixo mensal**: Ex: R$ 500 todo mês
- **Categoria de economia**: Vincula uma categoria específica

> 💡 **Dica**: Contribuições automáticas são o segredo! Você nem percebe que está economizando.

## 📊 Acompanhando seu progresso

Na página de Metas você verá:

- **📈 Barra de Progresso**: Visualize quanto já foi alcançado
- **💰 Valor Restante**: Quanto ainda falta para alcançar
- **⏰ Tempo Restante**: Quantos dias você tem
- **📅 Data Estimada**: Quando você alcançará se mantiver o ritmo
- **💡 Sugestões**: O sistema sugere quanto economizar por mês

## 🎯 Dicas para alcançar suas metas

- ✅ **Comece pequeno**: Metas muito grandes podem desmotivar
- 💰 **Contribua regularmente**: Mesmo valores pequenos fazem diferença
- 📊 **Acompanhe o progresso**: Visite suas metas regularmente
- 🎉 **Celebre marcos**: Comemore quando alcançar 25%, 50%, 75%
- 🔄 **Ajuste se necessário**: Se algo mudar, ajuste a meta

## 💡 Tipos de Metas Comuns

### 🚨 Reserva de Emergência
- **Objetivo**: 6 meses de despesas
- **Prazo**: 1-2 anos
- **Prioridade**: Alta! Sempre tenha uma reserva

### 🏠 Entrada de Imóvel
- **Objetivo**: 20-30% do valor do imóvel
- **Prazo**: 2-5 anos
- **Dica**: Comece a economizar o quanto antes

### ✈️ Viagem dos Sonhos
- **Objetivo**: Valor total da viagem
- **Prazo**: 6 meses - 2 anos
- **Dica**: Planeje com antecedência para conseguir melhores preços

### 🚗 Compra de Carro
- **Objetivo**: Entrada ou valor total
- **Prazo**: 1-3 anos
- **Dica**: Considere também os custos de manutenção

> 🎯 **Meta**: Defina pelo menos 3 metas: uma de curto prazo (6 meses), uma de médio prazo (1-2 anos) e uma de longo prazo (3+ anos)!
            """,
            "tips": [
                "Defina metas realistas e alcançáveis",
                "Configure contribuições automáticas quando possível",
                "Acompanhe o progresso regularmente",
                "Celebre cada marco alcançado para manter a motivação"
            ],
            "video_url": None,
        },
        "investments": {
            "title": "📈 Investimentos - Faça Seu Dinheiro Trabalhar",
            "description": "Gerencie todos os seus investimentos, acompanhe performance e planeje seu futuro financeiro!",
            "icon": "📈",
            "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
            "content": """
# 📈 Investimentos - Faça Seu Dinheiro Trabalhar

Investir é fazer seu dinheiro trabalhar para você! No FormuladoBolso, você pode gerenciar todos os seus investimentos em um só lugar, acompanhar performance e tomar decisões mais inteligentes.

## 🎯 Por que usar o módulo de investimentos?

- 📊 **Visão completa**: Veja todos os seus investimentos em um só lugar
- 📈 **Acompanhe performance**: Saiba quanto seus investimentos renderam
- 🎯 **Diversificação**: Veja se sua carteira está bem diversificada
- 💰 **Cálculo de impostos**: Calcule IRPF automaticamente
- 🚀 **Simulador**: Simule cenários antes de investir

## ➕ Como começar?

### Passo 1: Criar Conta de Investimento
1. Vá em **"Investimentos"** > **"Contas"** > **"Nova Conta"**
2. Preencha:
   - **Nome**: Ex: "XP Investimentos", "Rico", "Nubank"
   - **Tipo**: Corretora, Banco, Carteira Digital, etc.
   - **Saldo inicial**: Quanto você já tem investido (opcional)

### Passo 2: Registrar seus investimentos
Agora você pode registrar todas as suas transações:

**💵 Compras**
- Quando você compra um ativo (ações, FIIs, etc.)
- Registre o valor, quantidade e data

**💰 Vendas**
- Quando você vende um ativo
- O sistema calcula automaticamente o lucro/prejuízo

**📊 Dividendos e Juros**
- Recebimento de dividendos
- Juros de renda fixa
- Rendimentos de fundos

**🔄 Transferências**
- Movimentações entre contas de investimento

## 📊 Análises Disponíveis

### 📈 Performance da Carteira
- Veja o retorno total dos seus investimentos
- Compare com benchmarks
- Acompanhe evolução ao longo do tempo

### 🎯 Diversificação
- Veja a distribuição dos seus investimentos
- Identifique se está muito concentrado em um ativo
- Receba sugestões de diversificação

### 🧮 Simulador de Investimentos
- Simule quanto você terá no futuro
- Teste diferentes cenários de aporte
- Veja o poder dos juros compostos

### 💰 Cálculo de IRPF
- Calcule automaticamente o imposto devido
- Organize por mês de apuração
- Facilite a declaração de imposto de renda

## 💡 Dicas de Investimento

- ✅ **Diversifique**: Não coloque todos os ovos na mesma cesta
- 📊 **Acompanhe regularmente**: Mas não fique obcecado com variações diárias
- 🎯 **Invista regularmente**: Aporte mensal é melhor que aporte único grande
- 📚 **Eduque-se**: Use o Centro de Educação para aprender mais
- 💰 **Tenha reserva de emergência**: Antes de investir, tenha uma reserva

## 🎯 Tipos de Investimentos Suportados

- **📈 Ações**: Ações brasileiras e internacionais
- **🏢 FIIs**: Fundos Imobiliários
- **💰 Renda Fixa**: CDB, LCI, LCA, Tesouro Direto
- **🌍 ETFs**: Exchange Traded Funds
- **💎 Criptomoedas**: Bitcoin, Ethereum, etc.
- **🏦 Fundos**: Fundos de investimento
- **💼 Previdência**: Previdência privada

> 🎯 **Meta**: Comece investindo pelo menos 10% da sua renda. Com o tempo, aumente esse percentual!
            """,
            "tips": [
                "Diversifique seus investimentos para reduzir riscos",
                "Acompanhe performance regularmente, mas não fique obcecado",
                "Use o simulador antes de fazer grandes investimentos",
                "Mantenha uma reserva de emergência antes de investir"
            ],
            "video_url": None,
        },
        "reports": {
            "title": "📊 Relatórios - Entenda Suas Finanças",
            "description": "Gere relatórios detalhados e profissionais para analisar suas finanças de forma completa!",
            "icon": "📊",
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
            "content": """
# 📊 Relatórios - Entenda Suas Finanças

Relatórios são como exames de saúde para suas finanças! Eles mostram exatamente o que está acontecendo com seu dinheiro, onde você está indo bem e onde pode melhorar.

## 🎯 Por que usar relatórios?

- 📊 **Visão clara**: Entenda sua situação financeira de forma visual
- 🎯 **Identifique problemas**: Veja onde você está gastando demais
- 📈 **Acompanhe evolução**: Compare períodos diferentes
- 💡 **Tome decisões**: Use dados reais para decidir melhor
- 📄 **Compartilhe**: Exporte para PDF ou Excel

## 📋 Tipos de Relatórios Disponíveis

### 📊 Relatório Executivo
- **O que é**: Visão geral completa das suas finanças
- **Quando usar**: Para ter uma visão geral rápida
- **Mostra**: Receitas, despesas, saldo, principais categorias

### 💰 Relatório de Receitas
- **O que é**: Análise detalhada de todas as suas receitas
- **Quando usar**: Para entender de onde vem seu dinheiro
- **Mostra**: Receitas por categoria, por mês, tendências

### 💸 Relatório de Despesas
- **O que é**: Análise detalhada de todos os seus gastos
- **Quando usar**: Para identificar onde você mais gasta
- **Mostra**: Despesas por categoria, maiores gastos, tendências

### 📁 Relatório por Categorias
- **O que é**: Distribuição de gastos por categoria
- **Quando usar**: Para ver onde seu dinheiro está indo
- **Mostra**: Gráficos de pizza, barras, comparações

### 📈 Relatório de Tendências
- **O que é**: Evolução das suas finanças ao longo do tempo
- **Quando usar**: Para ver se está melhorando ou piorando
- **Mostra**: Gráficos de linha, comparações mensais/anuais

### 🎯 Relatório de Metas
- **O que é**: Progresso de todas as suas metas
- **Quando usar**: Para acompanhar se está no caminho certo
- **Mostra**: Progresso, tempo restante, sugestões

### 📅 Relatório Temporal
- **O que é**: Análise por períodos específicos
- **Quando usar**: Para comparar meses, trimestres ou anos
- **Mostra**: Comparações lado a lado, evolução

### 🏦 Relatório de Contas
- **O que é**: Análise por conta bancária
- **Quando usar**: Para ver movimentações por conta
- **Mostra**: Saldos, movimentações, gráficos por conta

## 📤 Como exportar relatórios?

### Exportar em PDF
1. Gere o relatório desejado
2. Clique em **"Exportar PDF"**
3. O arquivo será baixado automaticamente
4. Perfeito para compartilhar ou arquivar

### Exportar em Excel
1. Gere o relatório desejado
2. Clique em **"Exportar Excel"**
3. O arquivo será baixado com todos os dados
4. Perfeito para análises mais detalhadas

## 💡 Dicas para usar relatórios

- ✅ **Gere regularmente**: Faça relatórios mensais para acompanhar
- 📊 **Compare períodos**: Compare mês a mês para ver evolução
- 🎯 **Use filtros**: Filtre por período, categoria ou conta
- 📄 **Exporte e arquive**: Guarde relatórios importantes
- 💡 **Aja com base nos dados**: Use os relatórios para tomar decisões

## 🎯 Como interpretar relatórios?

### Se suas despesas estão aumentando:
- ✅ **Bom**: Se suas receitas também aumentaram proporcionalmente
- ⚠️ **Atenção**: Se suas receitas não aumentaram, você precisa cortar gastos

### Se uma categoria está muito alta:
- 📊 **Analise**: Veja se é necessário ou pode ser reduzido
- 🎯 **Planeje**: Crie um planejamento para essa categoria

### Se suas metas estão atrasadas:
- 💰 **Aumente aportes**: Considere aumentar as contribuições
- 📅 **Ajuste prazos**: Se necessário, ajuste a data limite

> 🎯 **Meta**: Gere pelo menos um relatório mensal para manter o controle das suas finanças!
            """,
            "tips": [
                "Gere relatórios mensais para acompanhar sua evolução",
                "Compare períodos diferentes para identificar tendências",
                "Use os filtros para análises mais específicas",
                "Exporte relatórios importantes para arquivar"
            ],
            "video_url": None,
        },
        "workspaces": {
            "title": "👥 Workspaces - Organize por Contexto",
            "description": "Organize suas finanças em diferentes contextos: pessoal, familiar ou compartilhado!",
            "icon": "👥",
            "image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800",
            "content": """
# 👥 Workspaces - Organize por Contexto

Workspaces são como "pastas" para suas finanças! Eles permitem que você separe suas finanças pessoais das familiares, ou crie espaços compartilhados para projetos em comum.

## 🎯 Por que usar workspaces?

- 🎯 **Organização**: Separe finanças pessoais, familiares e de negócios
- 👥 **Colaboração**: Compartilhe com familiares ou parceiros
- 📊 **Visão isolada**: Veja relatórios específicos de cada contexto
- 🔒 **Privacidade**: Mantenha suas finanças pessoais privadas

## ➕ Como criar um workspace?

### Passo 1: Acesse Workspaces
Clique em **"Workspaces"** no menu lateral e depois em **"Novo Workspace"**.

### Passo 2: Configure seu workspace

**📝 Nome** (obrigatório)
- Escolha um nome claro e descritivo
- Exemplos: "Finanças Pessoais", "Casa da Família", "Projeto Viagem"

**🎯 Tipo** (obrigatório)
Escolha o tipo que melhor descreve seu workspace:

- **👤 Pessoal**: Apenas para você
  - Use para: Suas finanças pessoais
  - Privacidade: Totalmente privado

- **👨‍👩‍👧‍👦 Familiar**: Para sua família
  - Use para: Finanças da casa, contas compartilhadas
  - Privacidade: Compartilhado com membros da família

- **🤝 Compartilhado**: Para projetos ou grupos
  - Use para: Viagens em grupo, eventos, projetos
  - Privacidade: Compartilhado com pessoas específicas

**📄 Descrição** (opcional)
- Adicione detalhes sobre o propósito do workspace
- Exemplo: "Finanças da casa - contas e despesas compartilhadas"

### Passo 3: Salvar
Clique em **"Salvar"** e seu workspace estará criado! 🎉

## 👥 Compartilhando Workspaces

### Como compartilhar?
1. Vá para o workspace desejado
2. Clique em **"Compartilhar"** ou **"Membros"**
3. Digite o email da pessoa
4. Escolha o nível de permissão:
   - **👀 Visualizador**: Pode apenas ver
   - **✏️ Editor**: Pode editar transações e dados
   - **👑 Administrador**: Controle total

### Tipos de compartilhamento

**👨‍👩‍👧‍👦 Familiar**
- Ideal para: Família que divide despesas
- Exemplo: Contas da casa, mercado, etc.
- Membros: Cônjuge, filhos maiores de idade

**🤝 Compartilhado**
- Ideal para: Projetos em comum
- Exemplo: Viagem em grupo, evento, negócio
- Membros: Amigos, parceiros, colegas

## 📊 Usando Workspaces

### Alternando entre workspaces
- Use o seletor no topo da página ou no menu lateral
- Cada workspace tem seus próprios:
  - Contas
  - Transações
  - Categorias
  - Metas
  - Relatórios

### Dados isolados
- Cada workspace é completamente independente
- Transações de um workspace não aparecem em outro
- Relatórios são gerados por workspace

## 💡 Dicas de uso

- ✅ **Crie workspaces específicos**: Separe bem cada contexto
- 👥 **Compartilhe com cuidado**: Só compartilhe com pessoas de confiança
- 📊 **Use para projetos**: Crie workspaces temporários para projetos específicos
- 🔄 **Organize regularmente**: Revise e organize seus workspaces periodicamente

## 🎯 Casos de uso comuns

### 👤 Workspace Pessoal
- Suas finanças pessoais
- Contas e investimentos pessoais
- Metas pessoais
- **Privacidade**: Totalmente privado

### 👨‍👩‍👧‍👦 Workspace Familiar
- Contas da casa
- Despesas compartilhadas
- Planejamento familiar
- **Membros**: Cônjuge, filhos

### 🤝 Workspace de Viagem
- Orçamento da viagem
- Despesas compartilhadas
- Planejamento conjunto
- **Membros**: Grupo de viagem

> 🎯 **Meta**: Organize suas finanças em pelo menos 2 workspaces: um pessoal e um compartilhado (familiar ou projeto)!
            """,
            "tips": [
                "Separe bem suas finanças pessoais das compartilhadas",
                "Compartilhe workspaces apenas com pessoas de confiança",
                "Use workspaces temporários para projetos específicos",
                "Revise e organize seus workspaces periodicamente"
            ],
            "video_url": None,
        },
        "insights": {
            "title": "💡 Insights - Análises Inteligentes",
            "description": "Receba análises automáticas e inteligentes das suas finanças para tomar melhores decisões!",
            "icon": "💡",
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
            "content": """
# 💡 Insights - Análises Inteligentes

Insights são como um consultor financeiro pessoal que analisa seus dados 24/7! Eles identificam padrões, tendências e oportunidades que você pode não ter notado.

## 🎯 Por que usar insights?

- 🔍 **Descubra padrões**: Veja padrões que você não percebeu
- 📊 **Entenda tendências**: Saiba se está melhorando ou piorando
- 💡 **Receba recomendações**: Sugestões personalizadas baseadas nos seus dados
- ⚠️ **Identifique problemas**: Alertas sobre gastos incomuns
- 🚀 **Tome decisões melhores**: Use dados reais para decidir

## 📊 Tipos de Insights Disponíveis

### 🔄 Mudanças nos Gastos
- **O que é**: Compara seus gastos atuais com períodos anteriores
- **Quando aparece**: Quando há mudanças significativas
- **Exemplo**: "Seus gastos com alimentação aumentaram 30% este mês"

### 📈 Padrões de Consumo
- **O que é**: Identifica padrões recorrentes nos seus gastos
- **Quando aparece**: Quando detecta padrões claros
- **Exemplo**: "Você sempre gasta mais aos finais de semana"

### 💰 Recomendações Personalizadas
- **O que é**: Sugestões específicas para você
- **Quando aparece**: Baseado na sua situação financeira
- **Exemplo**: "Considere aumentar sua reserva de emergência"

### 📁 Análise de Categorias
- **O que é**: Análise detalhada de cada categoria
- **Quando aparece**: Mensalmente ou quando solicitado
- **Exemplo**: "Você gasta 40% da sua renda com moradia"

### 📊 Tendências
- **O que é**: Evolução dos seus gastos ao longo do tempo
- **Quando aparece**: Continuamente atualizado
- **Exemplo**: "Suas economias estão aumentando consistentemente"

## 🎯 Como usar insights?

### Visualizar Insights
1. Vá em **"Insights"** no menu lateral
2. Veja os insights automáticos na aba **"Visão Geral"**
3. Explore diferentes tipos de análise nas abas

### Tipos de Análise

**📈 Tendências de Gastos**
- Veja como seus gastos evoluem
- Compare períodos diferentes
- Identifique sazonalidades

**📁 Análise por Categoria**
- Veja quais categorias mais consomem seu orçamento
- Compare com médias
- Receba alertas sobre categorias acima do normal

**🔄 Padrões de Consumo**
- Identifique quando você mais gasta
- Veja padrões semanais, mensais ou anuais
- Use para planejar melhor

**💡 Recomendações**
- Receba sugestões personalizadas
- Baseadas na sua situação real
- Ações práticas que você pode tomar

## 💡 Dicas para aproveitar insights

- ✅ **Revise regularmente**: Veja os insights pelo menos semanalmente
- 📊 **Compare períodos**: Use para ver sua evolução
- 🎯 **Aja nas recomendações**: Implemente as sugestões quando fizer sentido
- 🔄 **Acompanhe tendências**: Use para planejar o futuro
- ⚠️ **Preste atenção em alertas**: Alertas podem indicar problemas

## 🎯 Interpretando Insights

### Se seus gastos aumentaram:
- ✅ **Bom**: Se suas receitas também aumentaram
- ⚠️ **Atenção**: Se suas receitas não aumentaram, você precisa ajustar

### Se uma categoria está alta:
- 📊 **Analise**: Veja se é necessário ou pode ser reduzido
- 🎯 **Planeje**: Crie um planejamento para essa categoria

### Se receber uma recomendação:
- 💡 **Considere**: Avalie se faz sentido para você
- 🚀 **Implemente**: Se fizer sentido, coloque em prática
- 📊 **Acompanhe**: Veja os resultados depois

> 🎯 **Meta**: Revise seus insights pelo menos uma vez por semana para manter o controle e tomar decisões melhores!
            """,
            "tips": [
                "Revise insights regularmente para identificar padrões",
                "Use recomendações para melhorar suas finanças",
                "Compare tendências para ver sua evolução",
                "Preste atenção em alertas sobre gastos incomuns"
            ],
            "video_url": None,
        },
    }

        if topic:
            if topic in help_content:
                return help_content[topic]
            raise HTTPException(status_code=404, detail="Tópico não encontrado")
        
        return {"topics": list(help_content.keys()), "content": help_content}
    except Exception as e:
        import traceback
        print(f"Erro ao carregar conteúdo de ajuda: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar conteúdo de ajuda: {str(e)}"
        )


@router.get("/content")
async def list_educational_content(
    content_type: Optional[str] = Query(None),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista conteúdo educativo"""
    from src.domain.repositories.education_repository import EducationalContentRepository
    from src.infrastructure.repositories.education_repository import SQLAlchemyEducationalContentRepository
    
    content_repo: EducationalContentRepository = SQLAlchemyEducationalContentRepository(db)
    contents = await content_repo.get_all(content_type=content_type, difficulty=difficulty)
    
    # Converter para dict
    result = []
    for content in contents:
        result.append({
            "id": str(content.id),
            "title": content.title,
            "description": content.description,
            "content_type": content.content_type.value if hasattr(content.content_type, 'value') else str(content.content_type),
            "duration_minutes": content.duration_minutes,
            "difficulty_level": content.difficulty_level,
            "image_url": content.image_url,
            "views_count": content.views_count,
            "tags": content.tags.split(',') if content.tags else [],
            "created_at": content.created_at.isoformat() if content.created_at else None,
        })
    
    return result


@router.get("/content/{content_id}")
async def get_educational_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém conteúdo educativo específico"""
    from src.domain.repositories.education_repository import EducationalContentRepository, UserProgressRepository
    from src.infrastructure.repositories.education_repository import (
        SQLAlchemyEducationalContentRepository,
        SQLAlchemyUserProgressRepository,
    )
    from datetime import datetime
    import pytz
    
    content_repo: EducationalContentRepository = SQLAlchemyEducationalContentRepository(db)
    progress_repo: UserProgressRepository = SQLAlchemyUserProgressRepository(db)
    
    content = await content_repo.get_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    
    # Atualizar contador de visualizações
    content.views_count += 1
    await content_repo.update(content)
    
    # Buscar ou criar progresso
    progress = await progress_repo.get_by_user_and_content(current_user.id, content_id)
    if not progress:
        from src.infrastructure.database.models.education import UserProgress
        progress = UserProgress(
            user_id=current_user.id,
            content_id=content_id,
            progress_percentage=0,
            is_completed=False,
            last_accessed_at=datetime.now(pytz.UTC),
        )
        progress = await progress_repo.create(progress)
    else:
        progress.last_accessed_at = datetime.now(pytz.UTC)
        await progress_repo.update(progress)
    
    return {
        "id": str(content.id),
        "title": content.title,
        "description": content.description,
        "content_type": content.content_type.value if hasattr(content.content_type, 'value') else str(content.content_type),
        "content": content.content,
        "video_url": content.video_url,
        "image_url": content.image_url,
        "duration_minutes": content.duration_minutes,
        "difficulty_level": content.difficulty_level,
        "tags": content.tags.split(',') if content.tags else [],
        "views_count": content.views_count,
        "progress": {
            "progress_percentage": progress.progress_percentage,
            "is_completed": progress.is_completed,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            "last_accessed_at": progress.last_accessed_at.isoformat() if progress.last_accessed_at else None,
        },
        "created_at": content.created_at.isoformat() if content.created_at else None,
    }


@router.put("/content/{content_id}/progress")
async def update_content_progress(
    content_id: UUID,
    progress_percentage: int = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza progresso do usuário em um conteúdo"""
    from src.domain.repositories.education_repository import EducationalContentRepository, UserProgressRepository
    from src.infrastructure.repositories.education_repository import (
        SQLAlchemyEducationalContentRepository,
        SQLAlchemyUserProgressRepository,
    )
    from datetime import datetime
    import pytz
    
    content_repo: EducationalContentRepository = SQLAlchemyEducationalContentRepository(db)
    progress_repo: UserProgressRepository = SQLAlchemyUserProgressRepository(db)
    
    content = await content_repo.get_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    
    progress = await progress_repo.get_by_user_and_content(current_user.id, content_id)
    if not progress:
        from src.infrastructure.database.models.education import UserProgress
        progress = UserProgress(
            user_id=current_user.id,
            content_id=content_id,
            progress_percentage=progress_percentage,
            is_completed=progress_percentage >= 100,
            completed_at=datetime.now(pytz.UTC) if progress_percentage >= 100 else None,
            last_accessed_at=datetime.now(pytz.UTC),
        )
        progress = await progress_repo.create(progress)
    else:
        progress.progress_percentage = progress_percentage
        progress.is_completed = progress_percentage >= 100
        if progress_percentage >= 100 and not progress.completed_at:
            progress.completed_at = datetime.now(pytz.UTC)
        progress.last_accessed_at = datetime.now(pytz.UTC)
        progress = await progress_repo.update(progress)
    
    return {
        "progress_percentage": progress.progress_percentage,
        "is_completed": progress.is_completed,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
    }


@router.get("/quizzes")
async def list_quizzes(
    content_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista quizzes disponíveis"""
    from src.domain.repositories.education_repository import QuizRepository
    from src.infrastructure.repositories.education_repository import SQLAlchemyQuizRepository
    import json
    
    quiz_repo: QuizRepository = SQLAlchemyQuizRepository(db)
    
    if content_id:
        quizzes = await quiz_repo.get_by_content_id(content_id)
    else:
        quizzes = await quiz_repo.get_all()
    
    result = []
    for quiz in quizzes:
        try:
            questions = json.loads(quiz.questions) if quiz.questions else []
        except:
            questions = []
        
        result.append({
            "id": str(quiz.id),
            "title": quiz.title,
            "description": quiz.description,
            "content_id": str(quiz.content_id) if quiz.content_id else None,
            "questions_count": len(questions),
            "passing_score": quiz.passing_score,
            "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
        })
    
    return result


@router.get("/quizzes/{quiz_id}")
async def get_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém um quiz específico"""
    from src.domain.repositories.education_repository import QuizRepository
    from src.infrastructure.repositories.education_repository import SQLAlchemyQuizRepository
    import json
    
    quiz_repo: QuizRepository = SQLAlchemyQuizRepository(db)
    quiz = await quiz_repo.get_by_id(quiz_id)
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz não encontrado")
    
    try:
        questions = json.loads(quiz.questions) if quiz.questions else []
    except:
        questions = []
    
    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description,
        "content_id": str(quiz.content_id) if quiz.content_id else None,
        "questions": questions,
        "passing_score": quiz.passing_score,
        "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
    }


@router.post("/quizzes/{quiz_id}/attempt")
async def submit_quiz_attempt(
    quiz_id: UUID,
    answers: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submete tentativa de quiz"""
    from src.domain.repositories.education_repository import QuizRepository, QuizAttemptRepository
    from src.infrastructure.repositories.education_repository import (
        SQLAlchemyQuizRepository,
        SQLAlchemyQuizAttemptRepository,
    )
    from src.infrastructure.database.models.education import QuizAttempt
    import json
    from datetime import datetime
    import pytz
    
    quiz_repo: QuizRepository = SQLAlchemyQuizRepository(db)
    attempt_repo: QuizAttemptRepository = SQLAlchemyQuizAttemptRepository(db)
    
    quiz = await quiz_repo.get_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz não encontrado")
    
    try:
        questions = json.loads(quiz.questions) if quiz.questions else []
    except:
        questions = []
    
    # Calcular pontuação
    correct_answers = 0
    total_questions = len(questions)
    
    for question in questions:
        question_id = question.get('id') or str(questions.index(question))
        user_answer = answers.get(question_id)
        correct_answer = question.get('correct_answer')
        
        if user_answer == correct_answer:
            correct_answers += 1
    
    score = int((correct_answers / total_questions * 100)) if total_questions > 0 else 0
    is_passed = score >= quiz.passing_score
    
    # Criar tentativa
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        answers=json.dumps(answers),
        is_passed=is_passed,
        completed_at=datetime.now(pytz.UTC),
    )
    attempt = await attempt_repo.create(attempt)
    
    return {
        "id": str(attempt.id),
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "is_passed": is_passed,
        "passing_score": quiz.passing_score,
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
    }


@router.get("/progress")
async def get_education_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém progresso educacional do usuário"""
    from src.domain.repositories.education_repository import UserProgressRepository, EducationalContentRepository
    from src.infrastructure.repositories.education_repository import (
        SQLAlchemyUserProgressRepository,
        SQLAlchemyEducationalContentRepository,
    )
    
    progress_repo: UserProgressRepository = SQLAlchemyUserProgressRepository(db)
    content_repo: EducationalContentRepository = SQLAlchemyEducationalContentRepository(db)
    
    all_progress = await progress_repo.get_by_user_id(current_user.id)
    all_content = await content_repo.get_all()
    
    total_content = len(all_content)
    completed_content = len([p for p in all_progress if p.is_completed])
    in_progress_content = len([p for p in all_progress if not p.is_completed and p.progress_percentage > 0])
    
    completion_rate = int((completed_content / total_content * 100)) if total_content > 0 else 0
    
    # Detalhes do progresso
    progress_details = []
    for progress in all_progress:
        if progress.content:
            progress_details.append({
                "content_id": str(progress.content_id),
                "content_title": progress.content.title,
                "content_type": progress.content.content_type.value if hasattr(progress.content.content_type, 'value') else str(progress.content.content_type),
                "progress_percentage": progress.progress_percentage,
                "is_completed": progress.is_completed,
                "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
                "last_accessed_at": progress.last_accessed_at.isoformat() if progress.last_accessed_at else None,
            })
    
    return {
        "total_content": total_content,
        "completed_content": completed_content,
        "in_progress_content": in_progress_content,
        "completion_rate": completion_rate,
        "progress_details": progress_details,
    }


@router.post("/seed-courses")
async def seed_courses(
    force: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Popula o banco com cursos padrão (apenas para desenvolvimento/admin)"""
    from src.domain.repositories.education_repository import EducationalContentRepository
    from src.infrastructure.repositories.education_repository import SQLAlchemyEducationalContentRepository
    from src.infrastructure.database.models.education import EducationalContent, ContentType
    
    content_repo: EducationalContentRepository = SQLAlchemyEducationalContentRepository(db)
    
    # Verificar se já existem cursos
    existing = await content_repo.get_all()
    if len(existing) > 0 and not force:
        return {
            "message": f"Já existem {len(existing)} cursos no banco.",
            "existing_count": len(existing),
            "hint": "Use ?force=true para recriar todos os cursos"
        }
    
    courses = [
        # Finanças Pessoais
        {
            "title": "Fundamentos de Finanças Pessoais",
            "description": "Aprenda os conceitos básicos para gerenciar seu dinheiro",
            "content_type": ContentType.COURSE,
            "content": """
# Fundamentos de Finanças Pessoais

Bem-vindo ao curso de Fundamentos de Finanças Pessoais! Este curso é o primeiro passo para você tomar controle total das suas finanças.

## O que você vai aprender?

### Módulo 1: Introdução às Finanças Pessoais
- O que são finanças pessoais?
- Por que é importante gerenciar seu dinheiro?
- Como começar a organizar suas finanças

### Módulo 2: Orçamento Pessoal
- Como criar um orçamento eficiente
- Diferença entre receitas e despesas
- Como acompanhar seus gastos

### Módulo 3: Economia e Poupança
- Por que economizar é importante
- Como criar uma reserva de emergência
- Estratégias para economizar dinheiro

### Módulo 4: Planejamento Financeiro
- Como planejar seus gastos
- Definindo metas financeiras
- Criando um plano de ação

## Dicas Importantes

- ✅ Anote todos os seus gastos
- ✅ Revise seu orçamento mensalmente
- ✅ Tenha sempre uma reserva de emergência
- ✅ Defina metas claras e alcançáveis

> 💡 **Lembre-se**: O sucesso financeiro não acontece da noite para o dia. É um processo contínuo de aprendizado e disciplina!
            """,
            "duration_minutes": 60,
            "difficulty_level": 1,
            "tags": "finanças pessoais,orçamento,economia,iniciante",
            "image_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800",
        },
        {
            "title": "Orçamento Pessoal",
            "description": "Como criar e manter um orçamento eficiente",
            "content_type": ContentType.COURSE,
            "content": """
# Orçamento Pessoal

Um orçamento bem feito é a base de uma vida financeira saudável. Neste curso, você aprenderá tudo sobre como criar e manter um orçamento eficiente.

## Por que ter um orçamento?

- 📊 **Controle total**: Você sabe exatamente para onde vai seu dinheiro
- 🎯 **Alcançar metas**: Um orçamento ajuda você a alcançar seus objetivos
- 💰 **Evitar dívidas**: Você não gasta mais do que tem
- 📈 **Crescer financeiramente**: Você pode planejar investimentos

## Como criar um orçamento?

### Passo 1: Liste suas receitas
- Salário
- Freelances
- Aluguéis
- Outras receitas

### Passo 2: Liste suas despesas
- Fixas (aluguel, contas)
- Variáveis (alimentação, transporte)
- Ocasionais (presentes, viagens)

### Passo 3: Calcule a diferença
Receitas - Despesas = Resultado

- Se positivo: você está no caminho certo!
- Se negativo: precisa ajustar seus gastos

## Mantendo o orçamento

- ✅ Revise semanalmente
- ✅ Ajuste quando necessário
- ✅ Seja realista
- ✅ Use ferramentas (como o FormuladoBolso!)

> 💡 **Dica**: Comece simples! Um orçamento básico é melhor que nenhum orçamento.
            """,
            "duration_minutes": 45,
            "difficulty_level": 1,
            "tags": "orçamento,planejamento,finanças pessoais",
            "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
        },
        {
            "title": "Como Sair das Dívidas",
            "description": "Estratégias práticas para eliminar dívidas",
            "content_type": ContentType.COURSE,
            "content": """
# Como Sair das Dívidas

Dívidas podem parecer um problema sem solução, mas não são! Neste curso, você aprenderá estratégias práticas e eficazes para eliminar suas dívidas.

## Entendendo suas dívidas

### Tipos de dívidas
- **Dívidas de consumo**: Cartão de crédito, empréstimos pessoais
- **Dívidas de investimento**: Financiamento de imóvel (pode ser bom)
- **Dívidas ruins**: Juros altos, sem benefício

## Estratégias para sair das dívidas

### 1. Método da Bola de Neve
1. Liste todas as suas dívidas
2. Pague o mínimo de todas
3. Use o dinheiro extra para pagar a menor dívida
4. Quando uma for paga, use o dinheiro para a próxima

### 2. Método da Avalanche
1. Liste todas as suas dívidas
2. Pague o mínimo de todas
3. Use o dinheiro extra para a dívida com maior juro
4. Economize mais em juros

### 3. Negociação
- Negocie com credores
- Peça redução de juros
- Considere refinanciamento
- Procure ajuda profissional se necessário

## Dicas importantes

- ✅ Pare de criar novas dívidas
- ✅ Crie uma reserva de emergência (mesmo pequena)
- ✅ Aumente sua renda se possível
- ✅ Seja paciente e persistente

> 💡 **Lembre-se**: Sair das dívidas é uma maratona, não uma corrida. Cada passo conta!
            """,
            "duration_minutes": 90,
            "difficulty_level": 2,
            "tags": "dívidas,finanças pessoais,orçamento",
            "image_url": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800",
        },
        {
            "title": "Reserva de Emergência",
            "description": "Como construir e manter sua reserva de emergência",
            "content_type": ContentType.COURSE,
            "content": """
# Reserva de Emergência

Uma reserva de emergência é como um seguro para sua vida financeira. Neste curso, você aprenderá como construir e manter essa reserva essencial.

## O que é uma reserva de emergência?

É uma quantia de dinheiro guardada especificamente para cobrir despesas inesperadas, como:
- Perda de emprego
- Emergências médicas
- Reparos urgentes
- Outras situações imprevistas

## Quanto você precisa?

### Regra geral
- **Mínimo**: 3 meses de despesas
- **Ideal**: 6 meses de despesas
- **Máximo**: 12 meses (para casos especiais)

### Como calcular?
Some todas as suas despesas mensais essenciais:
- Moradia (aluguel/condomínio)
- Alimentação
- Transporte
- Saúde
- Contas básicas

Multiplique pelo número de meses desejado.

## Onde guardar?

### Características ideais:
- ✅ Fácil acesso (mas não muito fácil)
- ✅ Seguro (sem risco de perda)
- ✅ Rendimento (mesmo que pequeno)
- ✅ Liquidez (pode sacar quando precisar)

### Opções recomendadas:
- **Poupança**: Segura e acessível
- **CDB com liquidez diária**: Melhor rendimento
- **Tesouro Selic**: Seguro e rende bem

## Como construir?

### Estratégia 1: Aporte fixo mensal
- Defina um valor fixo (ex: R$ 500/mês)
- Automatize o depósito
- Não toque nesse dinheiro!

### Estratégia 2: Porcentagem da renda
- Separe 10-20% da sua renda
- Aumente conforme possível
- Seja consistente

### Estratégia 3: Bônus e extras
- Use 13º salário
- Use férias
- Use bônus de trabalho
- Use vendas extras

## Mantendo a reserva

- ✅ Não use para compras desejadas
- ✅ Reponha se usar
- ✅ Revise o valor anualmente
- ✅ Mantenha separada das outras contas

> 💡 **Dica**: Comece pequeno! R$ 1.000 já é um bom começo. O importante é começar!
            """,
            "duration_minutes": 30,
            "difficulty_level": 1,
            "tags": "reserva de emergência,poupança,finanças pessoais",
            "image_url": "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=800",
        },
        {
            "title": "Planejamento para Aposentadoria",
            "description": "Prepare-se financeiramente para o futuro",
            "content_type": ContentType.COURSE,
            "content": """
# Planejamento para Aposentadoria

A aposentadoria pode parecer distante, mas quanto antes você começar a planejar, melhor será sua qualidade de vida no futuro.

## Por que planejar?

- 👴 **Longevidade**: Vivemos mais, precisamos de mais dinheiro
- 💰 **Aposentadoria pública**: Pode não ser suficiente
- 🎯 **Qualidade de vida**: Você quer manter seu padrão de vida
- ⏰ **Tempo**: Quanto mais tempo, mais fácil acumular

## Quanto você precisa?

### Regra dos 25x
Multiplique suas despesas anuais por 25.

Exemplo:
- Despesas anuais: R$ 60.000
- Necessário: R$ 1.500.000

### Regra dos 4%
Você pode retirar 4% do seu patrimônio anualmente sem esgotar.

## Como calcular?

1. **Estime suas despesas futuras**
   - Considere inflação
   - Considere mudanças de estilo de vida
   - Considere saúde

2. **Calcule o patrimônio necessário**
   - Use a regra dos 25x
   - Ajuste conforme sua situação

3. **Defina quanto economizar**
   - Quanto tempo você tem?
   - Quanto pode economizar por mês?
   - Qual retorno esperado?

## Onde investir?

### Para aposentadoria, priorize:
- ✅ **Previdência privada (PGBL/VGBL)**: Benefícios fiscais
- ✅ **Fundos de previdência**: Diversificação
- ✅ **Ações**: Longo prazo, bom retorno
- ✅ **Renda fixa**: Segurança

### Evite:
- ❌ Aplicações de curto prazo
- ❌ Investimentos muito arriscados
- ❌ Deixar tudo na poupança

## Estratégias

### Comece cedo
- Quanto mais cedo, menos precisa economizar
- Juros compostos trabalham a seu favor
- Exemplo: R$ 500/mês por 30 anos = R$ 1.5M (com 8% ao ano)

### Automatize
- Configure aportes automáticos
- "Pague a si mesmo primeiro"
- Não espere sobrar dinheiro

### Aumente gradualmente
- Comece com o que pode
- Aumente quando receber aumento
- Use bônus e extras

## Dicas importantes

- ✅ Comece o quanto antes
- ✅ Seja consistente
- ✅ Revise anualmente
- ✅ Não retire antes do tempo
- ✅ Diversifique seus investimentos

> 💡 **Lembre-se**: O melhor momento para começar foi ontem. O segundo melhor é hoje!
            """,
            "duration_minutes": 120,
            "difficulty_level": 3,
            "tags": "aposentadoria,planejamento,investimentos,longo prazo",
            "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800",
        },
        # Investimentos
        {
            "title": "Introdução aos Investimentos",
            "description": "Conceitos básicos para começar a investir",
            "content_type": ContentType.COURSE,
            "content": """
# Introdução aos Investimentos

Investir é fazer seu dinheiro trabalhar para você! Neste curso, você aprenderá os conceitos fundamentais para começar a investir com segurança.

## O que é investir?

Investir é aplicar seu dinheiro em ativos que têm potencial de gerar retorno ao longo do tempo, como:
- Ações
- Títulos
- Fundos
- Imóveis
- Criptomoedas

## Por que investir?

- 📈 **Crescimento**: Seu dinheiro pode crescer
- 💰 **Renda passiva**: Gerar renda sem trabalhar
- 🎯 **Alcançar metas**: Viagens, casa, aposentadoria
- 🛡️ **Proteção**: Contra inflação

## Conceitos fundamentais

### Risco vs Retorno
- **Baixo risco**: Poupança, CDB (menor retorno)
- **Alto risco**: Ações, cripto (maior retorno possível)
- **Regra**: Maior risco = maior retorno potencial

### Diversificação
- Não coloque todos os ovos na mesma cesta
- Espalhe seus investimentos
- Reduz risco

### Liquidez
- Quão rápido você pode converter em dinheiro
- Poupança: alta liquidez
- Imóveis: baixa liquidez

### Juros Compostos
- Juros sobre juros
- Quanto mais tempo, mais cresce
- "Oitava maravilha do mundo" (Einstein)

## Tipos de investimentos

### Renda Fixa
- **CDB**: Certificado de Depósito Bancário
- **LCI/LCA**: Letras de Crédito
- **Tesouro Direto**: Títulos públicos
- **Características**: Previsível, seguro, menor retorno

### Renda Variável
- **Ações**: Participação em empresas
- **Fundos**: Carteira diversificada
- **ETFs**: Fundos de índice
- **Características**: Mais risco, maior retorno potencial

## Como começar?

### Passo 1: Tenha uma reserva de emergência
- Antes de investir, tenha segurança
- 3-6 meses de despesas

### Passo 2: Defina seus objetivos
- Curto prazo (1-2 anos)
- Médio prazo (3-5 anos)
- Longo prazo (10+ anos)

### Passo 3: Escolha onde investir
- Corretoras online
- Bancos
- Plataformas digitais

### Passo 4: Comece pequeno
- Não precisa de muito para começar
- R$ 100 já é um começo
- Aprenda com o tempo

## Dicas importantes

- ✅ Comece com renda fixa
- ✅ Estude antes de investir
- ✅ Diversifique
- ✅ Invista regularmente
- ✅ Tenha paciência

> 💡 **Lembre-se**: Investir é uma maratona, não uma corrida. Consistência é mais importante que timing!
            """,
            "duration_minutes": 60,
            "difficulty_level": 1,
            "tags": "investimentos,iniciante,renda fixa,renda variável",
            "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
        },
        {
            "title": "Renda Fixa para Iniciantes",
            "description": "Aprenda sobre CDB, LCI, LCA e Tesouro Direto",
            "content_type": ContentType.COURSE,
            "content": """
# Renda Fixa para Iniciantes

Renda fixa é o melhor lugar para começar a investir! É segura, previsível e perfeita para iniciantes.

## O que é Renda Fixa?

São investimentos onde você sabe (ou tem uma boa ideia) de quanto vai receber:
- Taxa de juros definida
- Prazo conhecido
- Retorno previsível

## Tipos de Renda Fixa

### CDB (Certificado de Depósito Bancário)
- **O que é**: Empréstimo para o banco
- **Rendimento**: Geralmente acima da poupança
- **Garantia**: FGC até R$ 250.000
- **Liquidez**: Depende do tipo (pós-fixado, prefixado, híbrido)

### LCI (Letra de Crédito Imobiliário)
- **O que é**: Empréstimo para construção
- **Rendimento**: Competitivo
- **Vantagem**: Isento de IR para pessoa física
- **Prazo**: Geralmente 2-3 anos

### LCA (Letra de Crédito do Agronegócio)
- **O que é**: Empréstimo para agronegócio
- **Rendimento**: Competitivo
- **Vantagem**: Isento de IR para pessoa física
- **Prazo**: Variável

### Tesouro Direto
- **O que é**: Títulos públicos do governo
- **Tipos**: 
  - Selic (curto prazo)
  - IPCA+ (proteção contra inflação)
  - Prefixado (taxa fixa)
- **Vantagem**: Muito seguro, fácil de comprar
- **Desvantagem**: Pode ter marcação a mercado

## Como escolher?

### Considere:
1. **Prazo**: Quando precisa do dinheiro?
2. **Risco**: Quanto risco aceita?
3. **Liquidez**: Precisa sacar antes?
4. **Impostos**: LCI/LCA são isentos de IR

### Para iniciantes:
- ✅ Comece com Tesouro Selic
- ✅ Depois explore CDBs
- ✅ Considere LCI/LCA para médio prazo
- ✅ Sempre verifique a garantia (FGC)

## Impostos

### Tabela Regressiva de IR:
- Até 180 dias: 22,5%
- 181 a 360 dias: 20%
- 361 a 720 dias: 17,5%
- Acima de 720 dias: 15%

### Isentos:
- LCI e LCA (pessoa física)
- Poupança (até limite)

## Dicas importantes

- ✅ Comece com valores pequenos
- ✅ Entenda o que está comprando
- ✅ Verifique a garantia (FGC)
- ✅ Compare taxas
- ✅ Considere a liquidez

> 💡 **Dica**: Renda fixa é segura, mas não deixe tudo lá. Conforme aprende, diversifique!
            """,
            "duration_minutes": 90,
            "difficulty_level": 1,
            "tags": "renda fixa,CDB,LCI,LCA,Tesouro Direto,iniciante",
            "image_url": "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=800",
        },
        {
            "title": "Ações e Bolsa de Valores",
            "description": "Como investir em ações de forma inteligente",
            "content_type": ContentType.COURSE,
            "content": """
# Ações e Bolsa de Valores

Ações podem ser uma excelente forma de fazer seu dinheiro crescer, mas é importante entender como funciona antes de investir.

## O que são ações?

Ações são pequenas partes de uma empresa. Quando você compra uma ação, você se torna sócio daquela empresa.

## Como funciona a Bolsa de Valores?

- **B3**: Bolsa brasileira (antiga BM&FBovespa)
- **Corretoras**: Intermediários para comprar/vender
- **Horário**: 10h às 17h (horário de pregão)
- **Liquidação**: D+2 (2 dias úteis)

## Tipos de ações

### Ações Ordinárias (ON)
- Direito a voto em assembleias
- Participação nas decisões
- Geralmente negociadas com código +3

### Ações Preferenciais (PN)
- Prioridade em dividendos
- Sem direito a voto
- Geralmente negociadas com código +4

## Como escolher ações?

### Análise Fundamentalista
- Analisa a empresa
- Lucros, receitas, dívidas
- Perspectivas de crescimento
- Indicadores (P/L, P/VPA, etc.)

### Análise Técnica
- Analisa gráficos
- Padrões de preço
- Volume de negociação
- Indicadores técnicos

## Estratégias

### Buy and Hold
- Comprar e segurar
- Longo prazo
- Menos trabalho
- Menos impostos

### Day Trade
- Comprar e vender no mesmo dia
- Curto prazo
- Muito trabalho
- Mais risco

### Swing Trade
- Segurar alguns dias/semanas
- Médio prazo
- Balance entre trabalho e retorno

## Riscos

- ⚠️ **Volatilidade**: Preços podem variar muito
- ⚠️ **Perda total**: Empresa pode falir
- ⚠️ **Emocional**: Medo e ganância
- ⚠️ **Timing**: Difícil acertar o momento

## Dicas importantes

- ✅ Comece com pouco
- ✅ Estude antes de investir
- ✅ Diversifique (não coloque tudo em uma ação)
- ✅ Tenha paciência
- ✅ Não invista dinheiro que precisa
- ✅ Considere ETFs para diversificação

## Para iniciantes

- **ETFs**: Fundos de índice (mais seguro)
- **Fundos de ações**: Gestão profissional
- **Ações individuais**: Depois de estudar muito

> 💡 **Lembre-se**: Ações podem dar retornos excelentes, mas também podem dar prejuízos. Invista apenas o que pode perder!
            """,
            "duration_minutes": 120,
            "difficulty_level": 2,
            "tags": "ações,bolsa de valores,renda variável,investimentos",
            "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800",
        },
        {
            "title": "Fundos de Investimento",
            "description": "Entenda como funcionam os fundos",
            "content_type": ContentType.COURSE,
            "content": """
# Fundos de Investimento

Fundos são uma forma prática e profissional de investir, especialmente para quem está começando.

## O que são fundos?

São "cestas" de investimentos gerenciadas por profissionais. Você compra cotas do fundo e o gestor investe seu dinheiro.

## Vantagens

- ✅ **Gestão profissional**: Especialistas cuidam do seu dinheiro
- ✅ **Diversificação**: Investe em vários ativos
- ✅ **Facilidade**: Não precisa escolher ativos individuais
- ✅ **Liquidez**: Geralmente pode resgatar facilmente

## Desvantagens

- ❌ **Taxas**: Cobram taxa de administração e performance
- ❌ **Menos controle**: Você não escolhe os ativos
- ❌ **Transparência**: Pode ser difícil entender onde está investido

## Tipos de fundos

### Fundos de Renda Fixa
- Investem em títulos
- Mais seguros
- Menor retorno

### Fundos de Ações
- Investem em ações
- Mais arriscados
- Maior retorno potencial

### Fundos Multimercado
- Investem em vários tipos
- Balance entre risco e retorno
- Mais diversificados

### Fundos de Curto Prazo
- Liquidez diária
- Baixo risco
- Baixo retorno

## Como escolher?

### Considere:
1. **Objetivo**: Alinhado com seus objetivos?
2. **Risco**: Adequado ao seu perfil?
3. **Taxas**: São razoáveis?
4. **Performance**: Histórico consistente?
5. **Gestor**: Experiência e credibilidade

### Indicadores importantes:
- **Rentabilidade**: Quanto rendeu?
- **Volatilidade**: Quanto variou?
- **Sharpe**: Retorno ajustado ao risco
- **Taxa de administração**: Quanto custa?

## Taxas

### Taxa de Administração
- Cobrada anualmente
- Geralmente 0,5% a 2% ao ano
- Descontada do patrimônio

### Taxa de Performance
- Cobrada quando supera benchmark
- Geralmente 20% do excedente
- Só paga se performar bem

## Dicas importantes

- ✅ Compare taxas
- ✅ Veja o histórico
- ✅ Entenda o que o fundo faz
- ✅ Diversifique entre fundos
- ✅ Revise periodicamente

> 💡 **Dica**: Fundos são ótimos para iniciantes, mas sempre entenda onde seu dinheiro está investido!
            """,
            "duration_minutes": 75,
            "difficulty_level": 2,
            "tags": "fundos,investimentos,gestão profissional",
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
        },
        {
            "title": "Análise Técnica",
            "description": "Técnicas avançadas de análise de gráficos",
            "content_type": ContentType.COURSE,
            "content": """
# Análise Técnica

A análise técnica é uma ferramenta poderosa para investidores que querem entender movimentos de preço e tomar decisões baseadas em gráficos.

## O que é análise técnica?

É o estudo de movimentos de preço e volume para prever tendências futuras. Baseia-se na ideia de que:
- O preço reflete todas as informações
- Os preços se movem em tendências
- A história tende a se repetir

## Conceitos fundamentais

### Suporte e Resistência
- **Suporte**: Nível onde o preço tende a parar de cair
- **Resistência**: Nível onde o preço tende a parar de subir
- Importante para identificar pontos de entrada/saída

### Tendências
- **Alta**: Máximas e mínimas crescentes
- **Baixa**: Máximas e mínimas decrescentes
- **Lateral**: Sem direção clara

### Volume
- Quantidade negociada
- Confirma movimentos
- Volume alto = movimento forte

## Indicadores técnicos

### Médias Móveis
- **MM Simples**: Média dos últimos N períodos
- **MM Exponencial**: Dá mais peso a preços recentes
- Usadas para identificar tendências

### RSI (Relative Strength Index)
- Mede força do movimento
- 0-100 (acima de 70 = sobrecomprado, abaixo de 30 = sobrevendido)
- Identifica reversões

### MACD
- Mostra mudanças de tendência
- Cruzamento de linhas = sinal
- Divergências = alerta

### Bollinger Bands
- Faixas de volatilidade
- Preço próximo da banda superior = sobrecomprado
- Preço próximo da banda inferior = sobrevendido

## Padrões gráficos

### Padrões de Reversão
- **Cabeça e Ombros**: Reversão de alta
- **Topo/Base Duplo**: Reversão
- **Triângulos**: Continuação ou reversão

### Padrões de Continuação
- **Flags**: Pausa na tendência
- **Pennants**: Continuação
- **Triângulos**: Continuação

## Estratégias

### Breakout
- Entrar quando preço rompe resistência
- Stop loss abaixo do suporte
- Alvo baseado em altura do padrão

### Pullback
- Entrar na correção da tendência
- Mais seguro que breakout
- Requer paciência

### Scalping
- Múltiplas operações no dia
- Pequenos lucros
- Muito trabalho

## Limitações

- ⚠️ Não funciona sempre
- ⚠️ Pode gerar sinais falsos
- ⚠️ Requer prática
- ⚠️ Não considera fundamentos

## Dicas importantes

- ✅ Combine com análise fundamentalista
- ✅ Use stop loss sempre
- ✅ Pratique em simuladores primeiro
- ✅ Não confie cegamente
- ✅ Estude muito antes de usar

> 💡 **Lembre-se**: Análise técnica é uma ferramenta, não uma garantia. Use com cuidado e sempre tenha gestão de risco!
            """,
            "duration_minutes": 150,
            "difficulty_level": 4,
            "tags": "análise técnica,gráficos,indicadores,avançado",
            "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800",
        },
        {
            "title": "Diversificação de Carteira",
            "description": "Como montar uma carteira diversificada",
            "content_type": ContentType.COURSE,
            "content": """
# Diversificação de Carteira

Diversificar é uma das regras de ouro do investimento. Aprenda como montar uma carteira bem diversificada.

## O que é diversificação?

É espalhar seus investimentos em diferentes ativos para reduzir risco. A ideia é: se um investimento vai mal, outros podem compensar.

## Por que diversificar?

- 🛡️ **Reduz risco**: Não coloca todos os ovos na mesma cesta
- 📈 **Melhora retorno**: Pode capturar oportunidades em diferentes áreas
- 💰 **Proteção**: Se um setor cai, outros podem subir
- 🎯 **Estabilidade**: Reduz volatilidade da carteira

## Como diversificar?

### Por tipo de ativo
- Renda fixa
- Ações
- Fundos
- Imóveis
- Criptomoedas
- Outros

### Por setor
- Financeiro
- Tecnologia
- Consumo
- Energia
- Saúde
- Outros

### Por geografia
- Brasil
- EUA
- Europa
- Ásia
- Outros países

### Por tamanho de empresa
- Large cap (grandes)
- Mid cap (médias)
- Small cap (pequenas)

## Alocação de ativos

### Perfil Conservador
- 70% Renda Fixa
- 20% Renda Variável
- 10% Outros

### Perfil Moderado
- 50% Renda Fixa
- 40% Renda Variável
- 10% Outros

### Perfil Arrojado
- 30% Renda Fixa
- 60% Renda Variável
- 10% Outros

## Regra da idade

Uma regra simples:
- **100 - sua idade** = % em renda variável
- Restante em renda fixa

Exemplo (30 anos):
- 70% renda variável
- 30% renda fixa

## Rebalanceamento

- Revise periodicamente (trimestral/anual)
- Ajuste quando necessário
- Mantenha a alocação desejada
- Venda o que subiu, compre o que caiu

## Erros comuns

- ❌ **Sobre-diversificação**: Muitos ativos pequenos
- ❌ **Sub-diversificação**: Poucos ativos
- ❌ **Correlação alta**: Ativos que se movem juntos
- ❌ **Não rebalancear**: Deixar desbalanceado

## Dicas importantes

- ✅ Comece simples
- ✅ Diversifique gradualmente
- ✅ Revise regularmente
- ✅ Considere ETFs para diversificação fácil
- ✅ Não diversifique demais

> 💡 **Lembre-se**: Diversificação não elimina risco, mas reduz. O objetivo é ter uma carteira balanceada que se alinha com seus objetivos e perfil de risco!
            """,
            "duration_minutes": 90,
            "difficulty_level": 3,
            "tags": "diversificação,carteira,investimentos,estratégia",
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
        },
    ]
    
    # Se force=True, deletar cursos existentes primeiro
    if force:
        existing = await content_repo.get_all()
        for course in existing:
            await content_repo.delete(course.id)
    
    # Buscar todos os cursos existentes uma vez
    existing = await content_repo.get_all()
    existing_titles = {c.title for c in existing}
    
    created = []
    for course_data in courses:
        # Verificar se já existe
        if course_data["title"] not in existing_titles:
            course = EducationalContent(**course_data)
            course = await content_repo.create(course)
            created.append(course.title)
            existing_titles.add(course.title)  # Adicionar para evitar duplicatas no mesmo batch
    
    if len(created) == 0:
        return {
            "message": "Todos os cursos já existem no banco.",
            "created": [],
            "total": 0,
            "existing_count": len(existing)
        }
    
    return {
        "message": f"{len(created)} cursos criados com sucesso!",
        "created": created,
        "total": len(created)
    }

