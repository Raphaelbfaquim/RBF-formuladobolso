'use client'

import { motion } from 'framer-motion'
import { 
  FiTrendingUp, 
  FiUsers, 
  FiShield, 
  FiZap, 
  FiBarChart2, 
  FiTarget,
  FiDollarSign,
  FiPieChart,
  FiLock,
  FiSmartphone
} from 'react-icons/fi'
import FeatureCard from '@/components/FeatureCard'
import CTA from '@/components/CTA'

export default function HomePage() {
  const mainFeatures = [
    {
      icon: <FiTrendingUp className="text-indigo-400" />,
      title: 'Gestão Completa',
      description: 'Controle total das suas finanças com contas, transações e categorias inteligentes.',
    },
    {
      icon: <FiUsers className="text-purple-400" />,
      title: 'Colaboração Familiar',
      description: 'Workspaces compartilhados com permissões granulares para toda a família.',
    },
    {
      icon: <FiZap className="text-pink-400" />,
      title: 'IA Financeira',
      description: 'Assistente virtual 24/7 que entende seu contexto e oferece recomendações personalizadas.',
    },
    {
      icon: <FiShield className="text-green-400" />,
      title: 'Segurança Avançada',
      description: '2FA, Open Banking, criptografia e logs de auditoria para proteger seus dados.',
    },
    {
      icon: <FiBarChart2 className="text-blue-400" />,
      title: 'Insights Automáticos',
      description: 'Análise inteligente de padrões, previsões e recomendações baseadas em IA.',
    },
    {
      icon: <FiTarget className="text-yellow-400" />,
      title: 'Metas e Sonhos',
      description: 'Acompanhe o progresso das suas metas financeiras com visualizações claras.',
    },
  ]

  const keyDifferentials = [
    {
      icon: <FiZap />,
      title: 'IA Financeira Pessoal',
      description: 'Chatbot inteligente que entende contexto e oferece recomendações personalizadas 24/7.',
    },
    {
      icon: <FiUsers />,
      title: 'Colaboração Familiar Avançada',
      description: 'Permissões granulares, workspaces isolados e chat integrado para gestão familiar completa.',
    },
    {
      icon: <FiPieChart />,
      title: 'Gamificação Completa',
      description: 'Transforme finanças em jogo com níveis, badges, desafios e educação financeira divertida.',
    },
    {
      icon: <FiLock />,
      title: 'Open Banking Nativo',
      description: 'Integração direta com bancos brasileiros, sincronização automática e reconciliação inteligente.',
    },
  ]

  return (
    <div className="pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Gestão Financeira</span>
              <br />
              <span className="text-white">Inteligente</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              O sistema completo de gerenciamento financeiro pessoal e familiar com IA, 
              gamificação e colaboração avançada. Tome controle das suas finanças de forma inteligente.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/app/register"
                className="px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold text-lg"
              >
                Comece Grátis
              </a>
              <a
                href="#features"
                className="px-8 py-4 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors font-semibold text-lg border border-white/20"
              >
                Ver Funcionalidades
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 px-4 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold mb-4">Funcionalidades Completas</h2>
            <p className="text-xl text-muted-foreground">
              Tudo que você precisa para gerenciar suas finanças de forma inteligente
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mainFeatures.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <FeatureCard {...feature} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Diferenciais */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold mb-4">O Que Nos Diferencia</h2>
            <p className="text-xl text-muted-foreground">
              Funcionalidades únicas que você não encontra em outros sistemas
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {keyDifferentials.map((differential, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="glass p-8 rounded-xl"
              >
                <div className="flex items-start gap-4">
                  <div className="text-4xl text-indigo-400">{differential.icon}</div>
                  <div>
                    <h3 className="text-2xl font-semibold mb-2">{differential.title}</h3>
                    <p className="text-muted-foreground">{differential.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="text-4xl font-bold gradient-text mb-2">16+</div>
              <div className="text-muted-foreground">Funcionalidades</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <div className="text-4xl font-bold gradient-text mb-2">100%</div>
              <div className="text-muted-foreground">Seguro</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="text-4xl font-bold gradient-text mb-2">24/7</div>
              <div className="text-muted-foreground">Disponível</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <div className="text-4xl font-bold gradient-text mb-2">IA</div>
              <div className="text-muted-foreground">Inteligente</div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <CTA
        title="Pronto para Transformar Suas Finanças?"
        description="Junte-se a milhares de usuários que já estão no controle das suas finanças"
        primaryText="Começar Agora"
        primaryLink="http://3.238.162.190/register"
        secondaryText="Ver Preços"
        secondaryLink="/pricing"
      />
    </div>
  )
}

