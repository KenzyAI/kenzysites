'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/cn'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { Menu, X } from 'lucide-react'
import { useState } from 'react'

interface PublicLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Início', href: '/' },
  { name: 'Recursos', href: '/features' },
  { name: 'Preços', href: '/pricing' },
  { name: 'Blog', href: '/blog' },
  { name: 'Contato', href: '/contact' },
]

export function PublicLayout({ children }: PublicLayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex-shrink-0">
              <Link href="/" className="flex items-center space-x-2">
                <div className="h-8 w-8 rounded bg-primary flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-sm">WP</span>
                </div>
                <span className="font-bold text-xl text-foreground">AI Builder</span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'text-sm font-medium transition-colors hover:text-primary',
                      isActive ? 'text-primary' : 'text-muted-foreground'
                    )}
                  >
                    {item.name}
                  </Link>
                )
              })}
            </nav>

            {/* Right side buttons */}
            <div className="flex items-center space-x-4">
              <ThemeToggle />

              <div className="hidden md:flex items-center space-x-2">
                <Button variant="ghost" asChild>
                  <Link href="/login">Entrar</Link>
                </Button>
                <Button asChild>
                  <Link href="/register">Começar Grátis</Link>
                </Button>
              </div>

              {/* Mobile menu button */}
              <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden">
              <div className="px-2 pt-2 pb-3 space-y-1 border-t">
                {navigation.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        'block px-3 py-2 rounded-md text-base font-medium transition-colors',
                        isActive
                          ? 'text-primary bg-primary/10'
                          : 'text-muted-foreground hover:text-primary hover:bg-primary/5'
                      )}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  )
                })}
                <div className="pt-4 flex flex-col space-y-2">
                  <Button variant="ghost" size="sm" asChild>
                    <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                      Entrar
                    </Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                      Começar Grátis
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="border-t bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-12 md:py-16">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {/* Company info */}
              <div className="col-span-1 md:col-span-2">
                <Link href="/" className="flex items-center space-x-2 mb-4">
                  <div className="h-8 w-8 rounded bg-primary flex items-center justify-center">
                    <span className="text-primary-foreground font-bold text-sm">WP</span>
                  </div>
                  <span className="font-bold text-xl">AI Builder</span>
                </Link>
                <p className="text-muted-foreground mb-4 max-w-md">
                  Crie sites WordPress profissionais em minutos com o poder da Inteligência
                  Artificial. A plataforma mais fácil e rápida do Brasil.
                </p>
                <div className="flex space-x-4">
                  <Button variant="outline" size="sm">
                    Facebook
                  </Button>
                  <Button variant="outline" size="sm">
                    Twitter
                  </Button>
                  <Button variant="outline" size="sm">
                    LinkedIn
                  </Button>
                </div>
              </div>

              {/* Product */}
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-4">Produto</h3>
                <ul className="space-y-2">
                  <li>
                    <Link href="/features" className="text-muted-foreground hover:text-primary">
                      Recursos
                    </Link>
                  </li>
                  <li>
                    <Link href="/pricing" className="text-muted-foreground hover:text-primary">
                      Preços
                    </Link>
                  </li>
                  <li>
                    <Link href="/templates" className="text-muted-foreground hover:text-primary">
                      Templates
                    </Link>
                  </li>
                  <li>
                    <Link href="/integrations" className="text-muted-foreground hover:text-primary">
                      Integrações
                    </Link>
                  </li>
                </ul>
              </div>

              {/* Support */}
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-4">Suporte</h3>
                <ul className="space-y-2">
                  <li>
                    <Link href="/help" className="text-muted-foreground hover:text-primary">
                      Central de Ajuda
                    </Link>
                  </li>
                  <li>
                    <Link href="/contact" className="text-muted-foreground hover:text-primary">
                      Contato
                    </Link>
                  </li>
                  <li>
                    <Link href="/docs" className="text-muted-foreground hover:text-primary">
                      Documentação
                    </Link>
                  </li>
                  <li>
                    <Link href="/status" className="text-muted-foreground hover:text-primary">
                      Status
                    </Link>
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t flex flex-col md:flex-row justify-between items-center">
              <p className="text-muted-foreground text-sm">
                © 2025 WordPress AI Builder. Todos os direitos reservados.
              </p>
              <div className="mt-4 md:mt-0 flex space-x-6">
                <Link href="/privacy" className="text-muted-foreground hover:text-primary text-sm">
                  Privacidade
                </Link>
                <Link href="/terms" className="text-muted-foreground hover:text-primary text-sm">
                  Termos
                </Link>
                <Link href="/cookies" className="text-muted-foreground hover:text-primary text-sm">
                  Cookies
                </Link>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
