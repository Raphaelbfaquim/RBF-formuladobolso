'use client'

import Link from 'next/link'
import { useState } from 'react'
import { FiMenu, FiX } from 'react-icons/fi'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="fixed top-0 w-full z-50 glass border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold gradient-text">💰 FormuladoBolso</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/features" className="text-sm font-medium hover:text-indigo-400 transition-colors">
              Funcionalidades
            </Link>
            <Link href="/diferenciais" className="text-sm font-medium hover:text-indigo-400 transition-colors">
              Diferenciais
            </Link>
            <Link href="/pricing" className="text-sm font-medium hover:text-indigo-400 transition-colors">
              Preços
            </Link>
            <Link href="/sobre" className="text-sm font-medium hover:text-indigo-400 transition-colors">
              Sobre
            </Link>
            <Link href="/contato" className="text-sm font-medium hover:text-indigo-400 transition-colors">
              Contato
            </Link>
            <a
              href="/app/login"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Acessar Sistema
            </a>
          </nav>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-4">
            <Link href="/features" className="block text-sm font-medium hover:text-indigo-400">
              Funcionalidades
            </Link>
            <Link href="/diferenciais" className="block text-sm font-medium hover:text-indigo-400">
              Diferenciais
            </Link>
            <Link href="/pricing" className="block text-sm font-medium hover:text-indigo-400">
              Preços
            </Link>
            <Link href="/sobre" className="block text-sm font-medium hover:text-indigo-400">
              Sobre
            </Link>
            <Link href="/contato" className="block text-sm font-medium hover:text-indigo-400">
              Contato
            </Link>
            <a
              href="/app/login"
              className="block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-center"
            >
              Acessar Sistema
            </a>
          </div>
        )}
      </div>
    </header>
  )
}

