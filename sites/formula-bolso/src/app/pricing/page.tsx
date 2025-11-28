'use client'

import { motion } from 'framer-motion'
import { FiCheck } from 'react-icons/fi'
import CTA from '@/components/CTA'

export default function PricingPage() {
  const plans = [
    {
      name: 'Básico',
      price: 'Grátis',
      period: '',
      description: 'Perfeito para começar a organizar suas finanças pessoais',
      features: [
        'Até 3 contas financeiras',
        'Transações ilimitadas',
        'Categorias básicas',
        'Dashboard pessoal',
        'Metas simples',
        'Relatórios básicos',
        'Suporte por email',
      ],
      cta: 'Começar Grátis',
      ctaLink: 'http://3.238.162.190/register',
      popular: false,
    },
    {
      name: 'Premium',
      price: 'R$ 29,90',
      period: '/mês',
      description: 'Para quem quer controle total e funcionalidades avançadas',
      features: [
        'Contas ilimitadas',
        'Workspaces pessoais',
        'IA Financeira (Chatbot)',
        'Insights automáticos',
        'Previsões com IA',
        'Relatórios PDF/Excel',
        'OCR de notas fiscais',
        'Gamificação completa',
        'Suporte prioritário',
      ],
      cta: 'Assinar Premium',
      ctaLink: 'http://3.238.162.190/register',
      popular: true,
    },
    {
      name: 'Família',
      price: 'R$ 49,90',
      period: '/mês',
      description: 'Ideal para famílias que querem gerenciar finanças juntas',
      features: [
        'Tudo do Premium',
        'Colaboração familiar',
        'Workspaces compartilhados',
        'Permissões granulares',
        'Chat familiar',
        'Dashboard familiar',
        'Até 5 membros',
        'Ranking familiar',
        'Suporte dedicado',
      ],
      cta: 'Assinar Família',
      ctaLink: 'http://3.238.162.190/register',
      popular: false,
    },
    {
      name: 'Empresarial',
      price: 'Sob Consulta',
      period: '',
      description: 'Solução customizada para empresas e equipes maiores',
      features: [
        'Tudo do Família',
        'Membros ilimitados',
        'Workspaces ilimitados',
        'API personalizada',
        'Integrações customizadas',
        'Treinamento da equipe',
        'Suporte 24/7',
        'Gerente de conta dedicado',
        'Customizações sob medida',
      ],
      cta: 'Falar com Vendas',
      ctaLink: '/contato',
      popular: false,
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
            Planos e <span className="gradient-text">Preços</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-muted-foreground"
          >
            Escolha o plano ideal para suas necessidades financeiras
          </motion.p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`glass p-8 rounded-xl relative ${
                  plan.popular ? 'ring-2 ring-indigo-500 scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Mais Popular
                    </span>
                  </div>
                )}
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="mb-2">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    {plan.period && <span className="text-muted-foreground">{plan.period}</span>}
                  </div>
                  <p className="text-sm text-muted-foreground">{plan.description}</p>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start gap-2">
                      <FiCheck className="text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-sm text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
                <a
                  href={plan.ctaLink}
                  target={plan.ctaLink.startsWith('http') ? '_blank' : undefined}
                  rel={plan.ctaLink.startsWith('http') ? 'noopener noreferrer' : undefined}
                  className={`block w-full text-center px-6 py-3 rounded-lg font-semibold transition-colors ${
                    plan.popular
                      ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                      : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                  }`}
                >
                  {plan.cta}
                </a>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-12 px-4 bg-white/5">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">Perguntas Frequentes</h2>
          <div className="space-y-6">
            <div className="glass p-6 rounded-xl">
              <h3 className="font-semibold mb-2">Posso mudar de plano depois?</h3>
              <p className="text-muted-foreground">
                Sim! Você pode fazer upgrade ou downgrade do seu plano a qualquer momento. As mudanças são aplicadas imediatamente.
              </p>
            </div>
            <div className="glass p-6 rounded-xl">
              <h3 className="font-semibold mb-2">Há período de teste?</h3>
              <p className="text-muted-foreground">
                O plano Básico é gratuito para sempre. Para os planos pagos, oferecemos 14 dias de teste gratuito sem necessidade de cartão de crédito.
              </p>
            </div>
            <div className="glass p-6 rounded-xl">
              <h3 className="font-semibold mb-2">Meus dados estão seguros?</h3>
              <p className="text-muted-foreground">
                Absolutamente! Utilizamos criptografia de ponta a ponta, autenticação 2FA e seguimos os mais altos padrões de segurança do mercado.
              </p>
            </div>
            <div className="glass p-6 rounded-xl">
              <h3 className="font-semibold mb-2">O que acontece se eu cancelar?</h3>
              <p className="text-muted-foreground">
                Você mantém acesso até o final do período pago. Seus dados são preservados e você pode retomar a qualquer momento.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTA
        title="Pronto para Começar?"
        description="Escolha seu plano e comece a transformar sua relação com o dinheiro hoje mesmo"
        primaryText="Ver Planos"
        primaryLink="#pricing"
      />
    </div>
  )
}

