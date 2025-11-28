import Link from 'next/link'
import { FiMail, FiPhone, FiGithub, FiLinkedin } from 'react-icons/fi'

export default function Footer() {
  return (
    <footer className="bg-background border-t border-white/10 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-xl font-bold gradient-text mb-4">FormuladoBolso</h3>
            <p className="text-sm text-muted-foreground">
              Gestão financeira inteligente para você e sua família.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-semibold mb-4">Produto</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/features" className="text-muted-foreground hover:text-indigo-400">
                  Funcionalidades
                </Link>
              </li>
              <li>
                <Link href="/diferenciais" className="text-muted-foreground hover:text-indigo-400">
                  Diferenciais
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-muted-foreground hover:text-indigo-400">
                  Preços
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold mb-4">Empresa</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/sobre" className="text-muted-foreground hover:text-indigo-400">
                  Sobre Nós
                </Link>
              </li>
              <li>
                <Link href="/contato" className="text-muted-foreground hover:text-indigo-400">
                  Contato
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-4">Contato</h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2 text-muted-foreground">
                <FiMail size={16} />
                contato@formuladobolso.com
              </li>
              <li className="flex items-center gap-2 text-muted-foreground">
                <FiPhone size={16} />
                (00) 0000-0000
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-white/10 text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} FormuladoBolso. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  )
}

