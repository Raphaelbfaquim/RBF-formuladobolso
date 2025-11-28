'use client'

import { motion } from 'framer-motion'
import {
  FiDollarSign,
  FiTrendingUp,
  FiTarget,
  FiCalendar,
  FiFileText,
  FiBarChart2,
  FiUsers,
  FiZap,
  FiShield,
  FiPieChart,
  FiBook,
  FiSmartphone,
  FiCreditCard,
  FiRepeat
} from 'react-icons/fi'
import FeatureCard from '@/components/FeatureCard'
import CTA from '@/components/CTA'

export default function FeaturesPage() {
  const features = [
    {
      category: 'Gestão Financeira Básica',
      items: [
        {
          icon: <FiDollarSign className="text-indigo-400" />,
          title: 'Múltiplas Contas',
          description: 'Gerencie contas correntes, poupança, cartões de crédito e investimentos em um só lugar.',
        },
        {
          icon: <FiTrendingUp className="text-green-400" />,
          title: 'Transações Detalhadas',
          description: 'Registre receitas, despesas e transferências com categorização inteligente e histórico completo.',
        },
        {
          icon: <FiCreditCard className="text-blue-400" />,
          title: 'Categorização Inteligente',
          description: 'Organize suas transações com categorias hierárquicas e subcategorias personalizadas.',
        },
        {
          icon: <FiBarChart2 className="text-purple-400" />,
          title: 'Saldos em Tempo Real',
          description: 'Acompanhe seus saldos atualizados automaticamente com cada transação registrada.',
        },
      ],
    },
    {
      category: 'Planejamento e Orçamento',
      items: [
        {
          icon: <FiCalendar className="text-pink-400" />,
          title: 'Planejamento Mensal',
          description: 'Defina orçamentos mensais por categoria e acompanhe o progresso em tempo real.',
        },
        {
          icon: <FiTarget className="text-yellow-400" />,
          title: 'Metas e Sonhos',
          description: 'Crie metas financeiras, acompanhe o progresso e receba sugestões de economia mensal.',
        },
        {
          icon: <FiRepeat className="text-orange-400" />,
          title: 'Contas a Pagar/Receber',
          description: 'Gerencie contas recorrentes com lembretes automáticos e integração com transações.',
        },
        {
          icon: <FiFileText className="text-red-400" />,
          title: 'Alertas de Vencimento',
          description: 'Receba notificações de contas próximas do vencimento e evite multas e juros.',
        },
      ],
    },
    {
      category: 'Análise e Insights',
      items: [
        {
          icon: <FiBarChart2 className="text-indigo-400" />,
          title: 'Dashboard Interativo',
          description: 'Visualize seu panorama financeiro com gráficos, estatísticas e resumos personalizados.',
        },
        {
          icon: <FiFileText className="text-green-400" />,
          title: 'Relatórios PDF/Excel',
          description: 'Exporte relatórios mensais em PDF ou Excel para análise detalhada e compartilhamento.',
        },
        {
          icon: <FiZap className="text-blue-400" />,
          title: 'Insights Automáticos',
          description: 'Receba análises inteligentes de padrões de gastos, tendências e recomendações personalizadas.',
        },
        {
          icon: <FiTrendingUp className="text-purple-400" />,
          title: 'Previsões com IA',
          description: 'Simule cenários futuros, preveja saldos e receba alertas sobre possíveis problemas financeiros.',
        },
        {
          icon: <FiPieChart className="text-pink-400" />,
          title: 'Análise de Hábitos',
          description: 'Identifique padrões de consumo por dia da semana, mês e categoria para otimizar seus gastos.',
        },
      ],
    },
    {
      category: 'Colaboração Familiar',
      items: [
        {
          icon: <FiUsers className="text-indigo-400" />,
          title: 'Workspaces Compartilhados',
          description: 'Crie espaços de trabalho financeiros compartilhados com sua família ou equipe.',
        },
        {
          icon: <FiShield className="text-green-400" />,
          title: 'Permissões Granulares',
          description: 'Controle quem pode ver, editar ou deletar cada módulo com sistema de permissões avançado.',
        },
        {
          icon: <FiSmartphone className="text-blue-400" />,
          title: 'Chat Familiar',
          description: 'Comunique-se com sua família sobre finanças através do chat integrado no sistema.',
        },
        {
          icon: <FiTarget className="text-purple-400" />,
          title: 'Aprovações de Gastos',
          description: 'Sistema de aprovação para gastos maiores, garantindo transparência familiar.',
        },
      ],
    },
    {
      category: 'IA e Automação',
      items: [
        {
          icon: <FiZap className="text-indigo-400" />,
          title: 'Chatbot Financeiro 24/7',
          description: 'Assistente virtual que responde perguntas, oferece conselhos e ajuda na tomada de decisões.',
        },
        {
          icon: <FiTrendingUp className="text-green-400" />,
          title: 'Categorização Automática',
          description: 'IA categoriza automaticamente suas transações baseada em histórico e padrões.',
        },
        {
          icon: <FiFileText className="text-blue-400" />,
          title: 'OCR de Notas Fiscais',
          description: 'Escaneie QR codes ou fotos de notas fiscais para extrair dados automaticamente.',
        },
        {
          icon: <FiShield className="text-purple-400" />,
          title: 'Open Banking',
          description: 'Integração nativa com bancos brasileiros para sincronização automática de transações.',
        },
      ],
    },
    {
      category: 'Gamificação e Educação',
      items: [
        {
          icon: <FiTarget className="text-indigo-400" />,
          title: 'Sistema de Níveis',
          description: 'Ganhe experiência e suba de nível conforme usa o sistema e atinge metas financeiras.',
        },
        {
          icon: <FiPieChart className="text-green-400" />,
          title: 'Badges e Conquistas',
          description: 'Desbloqueie badges e conquistas por realizar ações financeiras positivas.',
        },
        {
          icon: <FiTrendingUp className="text-blue-400" />,
          title: 'Desafios Financeiros',
          description: 'Participe de desafios mensais e semanais para melhorar seus hábitos financeiros.',
        },
        {
          icon: <FiBook className="text-purple-400" />,
          title: 'Educação Financeira',
          description: 'Acesse conteúdo educativo, quizzes e aprenda sobre finanças de forma interativa.',
        },
      ],
    },
    {
      category: 'Segurança',
      items: [
        {
          icon: <FiShield className="text-indigo-400" />,
          title: 'Autenticação 2FA',
          description: 'Proteja sua conta com autenticação de dois fatores usando aplicativos autenticadores.',
        },
        {
          icon: <FiFileText className="text-green-400" />,
          title: 'Logs de Auditoria',
          description: 'Todas as ações são registradas em logs de auditoria para rastreabilidade completa.',
        },
        {
          icon: <FiShield className="text-blue-400" />,
          title: 'Criptografia de Dados',
          description: 'Seus dados financeiros são criptografados e protegidos com os mais altos padrões de segurança.',
        },
        {
          icon: <FiSmartphone className="text-purple-400" />,
          title: 'Backup Automático',
          description: 'Seus dados são automaticamente salvos e podem ser restaurados a qualquer momento.',
        },
      ],
    },
  ]

  return (
    <div className="pt-16">
      {/* Hero */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-5xl font-bold mb-6"
          >
            <span className="gradient-text">Funcionalidades</span> Completas
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-muted-foreground"
          >
            Um sistema completo com tudo que você precisa para gerenciar suas finanças de forma inteligente
          </motion.p>
        </div>
      </section>

      {/* Features by Category */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto space-y-16">
          {features.map((category, categoryIndex) => (
            <motion.div
              key={categoryIndex}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-3xl font-bold mb-8 text-center">{category.category}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {category.items.map((item, itemIndex) => (
                  <motion.div
                    key={itemIndex}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: itemIndex * 0.1 }}
                  >
                    <FeatureCard {...item} />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <CTA
        title="Experimente Todas Essas Funcionalidades"
        description="Comece a usar o FormuladoBolso hoje e transforme sua relação com o dinheiro"
        primaryText="Começar Grátis"
        primaryLink="http://3.238.162.190/register"
        secondaryText="Ver Preços"
        secondaryLink="/pricing"
      />
    </div>
  )
}

