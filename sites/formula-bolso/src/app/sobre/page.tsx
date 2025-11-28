'use client'

import { motion } from 'framer-motion'
import { FiTarget, FiEye, FiHeart } from 'react-icons/fi'
import CTA from '@/components/CTA'

export default function SobrePage() {
  const values = [
    {
      icon: <FiTarget className="text-4xl text-indigo-400" />,
      title: 'Missão',
      description: 'Democratizar o acesso à gestão financeira inteligente, ajudando pessoas e famílias a alcançarem independência financeira através de tecnologia inovadora e educação.',
    },
    {
      icon: <FiEye className="text-4xl text-purple-400" />,
      title: 'Visão',
      description: 'Ser a plataforma de gestão financeira mais completa e inovadora do Brasil, reconhecida por sua tecnologia de IA, gamificação e colaboração familiar avançada.',
    },
    {
      icon: <FiHeart className="text-4xl text-pink-400" />,
      title: 'Valores',
      description: 'Transparência, segurança, inovação e compromisso com a educação financeira. Acreditamos que todos merecem ter controle total sobre suas finanças.',
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
            Sobre o <span className="gradient-text">FormuladoBolso</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-muted-foreground"
          >
            Conheça nossa história, missão e o que nos motiva a criar o melhor sistema de gestão financeira
          </motion.p>
        </div>
      </section>

      {/* História */}
      <section className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="glass p-8 rounded-xl mb-8"
          >
            <h2 className="text-3xl font-bold mb-4">Nossa História</h2>
            <div className="space-y-4 text-muted-foreground">
              <p>
                O FormuladoBolso nasceu da necessidade de ter um sistema de gestão financeira que realmente entendesse
                as necessidades dos brasileiros. Após analisar os principais apps do mercado, identificamos que faltava
                algo: um sistema completo, integrado e que utilizasse tecnologia de ponta para oferecer uma experiência
                verdadeiramente inteligente.
              </p>
              <p>
                Desenvolvido com as mais modernas tecnologias (Next.js, FastAPI, PostgreSQL, IA), o FormuladoBolso
                combina funcionalidades essenciais com inovações como IA financeira pessoal, gamificação completa e
                colaboração familiar avançada.
              </p>
              <p>
                Nossa missão é ajudar pessoas e famílias a alcançarem independência financeira através de uma plataforma
                que não apenas organiza, mas também educa e motiva através de gamificação e insights inteligentes.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Missão, Visão, Valores */}
      <section className="py-12 px-4 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {values.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="glass p-8 rounded-xl text-center"
              >
                <div className="mb-4 flex justify-center">{value.icon}</div>
                <h3 className="text-2xl font-bold mb-4">{value.title}</h3>
                <p className="text-muted-foreground">{value.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Tecnologia */}
      <section className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="glass p-8 rounded-xl"
          >
            <h2 className="text-3xl font-bold mb-4">Tecnologia de Ponta</h2>
            <p className="text-muted-foreground mb-6">
              O FormuladoBolso é construído com as tecnologias mais modernas e seguras do mercado:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {['Next.js 14', 'FastAPI', 'PostgreSQL', 'Redis', 'TypeScript', 'Tailwind CSS', 'IA/ML', 'Open Banking'].map((tech, index) => (
                <div key={index} className="bg-white/5 p-4 rounded-lg text-center">
                  <span className="text-sm font-semibold">{tech}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <CTA
        title="Faça Parte da Nossa História"
        description="Junte-se a nós na missão de transformar a gestão financeira no Brasil"
        primaryText="Começar Agora"
        primaryLink="http://3.238.162.190/register"
        secondaryText="Falar Conosco"
        secondaryLink="/contato"
      />
    </div>
  )
}

