'use client'

import { motion } from 'framer-motion'
import {
  FiZap,
  FiUsers,
  FiPieChart,
  FiShield,
  FiTrendingUp,
  FiSmartphone
} from 'react-icons/fi'
import CTA from '@/components/CTA'

export default function DiferenciaisPage() {
  const diferenciais = [
    {
      icon: <FiZap className="text-5xl text-indigo-400" />,
      title: 'IA Financeira Pessoal',
      subtitle: 'Assistente Virtual Inteligente',
      description: 'Nosso chatbot financeiro não é apenas um bot. Ele entende contexto, aprende com seus hábitos e oferece recomendações personalizadas 24 horas por dia, 7 dias por semana.',
      features: [
        'Perguntas como "Posso comprar isso?" recebem análises completas',
        'Sugestões automáticas de economia baseadas em seu histórico',
        'Alertas inteligentes sobre padrões de gastos',
        'Análise preditiva de saldos futuros',
        'Simulador de compras com impacto financeiro',
      ],
      comparison: 'Outros sistemas: Bots simples com respostas genéricas | FormuladoBolso: IA contextual que entende suas finanças',
    },
    {
      icon: <FiUsers className="text-5xl text-purple-400" />,
      title: 'Colaboração Familiar Avançada',
      subtitle: 'Mais que Compartilhamento',
      description: 'Não é apenas compartilhar dados. É um sistema completo de gestão familiar com permissões granulares, workspaces isolados e comunicação integrada.',
      features: [
        'Permissões por módulo (contas, transações, metas, etc.)',
        'Workspaces isolados para diferentes contextos financeiros',
        'Chat familiar integrado para discussões sobre finanças',
        'Sistema de aprovação para gastos maiores',
        'Dashboard familiar com visão consolidada',
      ],
      comparison: 'Outros sistemas: Compartilhamento básico | FormuladoBolso: Gestão familiar completa com controle total',
    },
    {
      icon: <FiPieChart className="text-5xl text-pink-400" />,
      title: 'Gamificação Completa',
      subtitle: 'Finanças que Motivam',
      description: 'Transforme o gerenciamento financeiro em uma experiência envolvente com níveis, badges, desafios e educação financeira gamificada.',
      features: [
        'Sistema de níveis (1-100+) com experiência e pontos',
        'Badges e conquistas por ações financeiras positivas',
        'Desafios mensais e semanais personalizados',
        'Ranking familiar para competição saudável',
        'Streak de dias consecutivos usando o sistema',
        'Conteúdo educativo interativo com quizzes',
      ],
      comparison: 'Outros sistemas: Sem gamificação | FormuladoBolso: Sistema completo que motiva através de conquistas',
    },
    {
      icon: <FiShield className="text-5xl text-green-400" />,
      title: 'Open Banking Nativo',
      subtitle: 'Integração Brasileira Completa',
      description: 'Integração direta com o ecossistema Open Banking brasileiro, oferecendo sincronização automática e reconciliação inteligente.',
      features: [
        'Conexão via Open Banking (Bacen)',
        'Sincronização automática de todas as contas',
        'Reconciliação inteligente de transações',
        'Suporte a múltiplos bancos simultaneamente',
        'Categorização automática de transações importadas',
        'Detecção de duplicatas',
      ],
      comparison: 'Outros sistemas: Integração manual ou limitada | FormuladoBolso: Open Banking nativo e completo',
    },
    {
      icon: <FiTrendingUp className="text-5xl text-blue-400" />,
      title: 'Design Moderno e Intuitivo',
      subtitle: 'Experiência Visual Única',
      description: 'Interface moderna com glassmorphism, dark mode nativo e micro-interações que tornam o uso do sistema uma experiência agradável.',
      features: [
        'Glassmorphism - Efeito de vidro fosco moderno',
        'Dark mode nativo otimizado',
        'Gradientes dinâmicos que mudam com contexto',
        'Micro-interações sutis e elegantes',
        'Interface 100% responsiva',
        'Acessibilidade em primeiro lugar',
      ],
      comparison: 'Outros sistemas: Interfaces tradicionais | FormuladoBolso: Design moderno e inovador',
    },
    {
      icon: <FiSmartphone className="text-5xl text-yellow-400" />,
      title: 'Sistema Completo e Integrado',
      subtitle: 'Tudo em Um Lugar',
      description: 'Não precisa de múltiplos apps. O FormuladoBolso oferece todas as funcionalidades que você precisa em uma única plataforma integrada.',
      features: [
        '16+ funcionalidades principais integradas',
        'Dashboard unificado com visão completa',
        'Relatórios PDF e Excel integrados',
        'Sistema de notificações completo',
        'Calendário financeiro integrado',
        'Agendamento de transações',
      ],
      comparison: 'Outros sistemas: Funcionalidades fragmentadas | FormuladoBolso: Sistema completo e integrado',
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
            O Que Nos <span className="gradient-text">Diferencia</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-muted-foreground"
          >
            Funcionalidades únicas que você não encontra em outros sistemas de gestão financeira
          </motion.p>
        </div>
      </section>

      {/* Diferenciais */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto space-y-16">
          {diferenciais.map((diferencial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="glass p-8 rounded-xl"
            >
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1">
                  <div className="mb-4">{diferencial.icon}</div>
                  <h2 className="text-3xl font-bold mb-2">{diferencial.title}</h2>
                  <p className="text-indigo-400 font-semibold mb-4">{diferencial.subtitle}</p>
                  <p className="text-muted-foreground">{diferencial.description}</p>
                </div>
                <div className="lg:col-span-2">
                  <h3 className="text-xl font-semibold mb-4">Funcionalidades:</h3>
                  <ul className="space-y-2 mb-6">
                    {diferencial.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start gap-2">
                        <span className="text-green-400 mt-1">✓</span>
                        <span className="text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-4">
                    <p className="text-sm">
                      <strong className="text-indigo-400">Comparação:</strong>{' '}
                      <span className="text-muted-foreground">{diferencial.comparison}</span>
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <CTA
        title="Experimente Nossos Diferenciais"
        description="Veja por que o FormuladoBolso é diferente de todos os outros sistemas"
        primaryText="Começar Agora"
        primaryLink="http://3.238.162.190/register"
        secondaryText="Ver Funcionalidades"
        secondaryLink="/features"
      />
    </div>
  )
}

