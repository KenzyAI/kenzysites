'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/cn'
import { Button } from '@/components/ui/button'
import { GlobalSearch } from '@/components/dashboard/global-search'
import {
  LayoutDashboard,
  Globe,
  Zap,
  Settings,
  Users,
  BarChart3,
  Menu,
  X,
  Bell,
  CreditCard,
  Shield,
  Activity,
  Database,
  Plug,
  ChevronDown,
  ChevronRight,
  ExternalLink,
} from 'lucide-react'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { 
    name: 'Dashboard', 
    href: '/dashboard', 
    icon: LayoutDashboard,
    badge: null 
  },
  { 
    name: 'Sites WordPress', 
    href: '/dashboard/sites', 
    icon: Globe,
    badge: 'PRO',
    subItems: [
      { name: 'Todos os Sites', href: '/dashboard/sites' },
      { name: 'Criar Novo Site', href: '/dashboard/sites/new' },
      { name: 'Templates ACF', href: '/dashboard/templates' },
      { name: 'Provisionamento', href: '/dashboard/provisioning' }
    ]
  },
  { 
    name: 'Portal do Cliente', 
    href: '/portal', 
    icon: Users,
    badge: null,
    subItems: [
      { name: 'Meu Site', href: '/portal' },
      { name: 'Backups', href: '/portal/backups' },
      { name: 'Domínio', href: '/portal/domain' },
      { name: 'Métricas', href: '/portal/metrics' }
    ]
  },
  { 
    name: 'Faturamento', 
    href: '/dashboard/billing', 
    icon: CreditCard,
    badge: 'Asaas',
    subItems: [
      { name: 'Faturas', href: '/dashboard/billing/invoices' },
      { name: 'Assinaturas', href: '/dashboard/billing/subscriptions' },
      { name: 'Pagamentos PIX', href: '/dashboard/billing/pix' },
      { name: 'Inadimplentes', href: '/dashboard/billing/overdue' },
      { name: 'Suspensões', href: '/dashboard/suspensions' }
    ]
  },
  { 
    name: 'Admin Geral', 
    href: '/admin/dashboard', 
    icon: Shield,
    badge: 'ADMIN',
    subItems: [
      { name: 'Todos Clientes', href: '/admin/dashboard' },
      { name: 'Kubernetes', href: '/admin/kubernetes' },
      { name: 'DNS Manager', href: '/admin/dns' },
      { name: 'Recursos', href: '/admin/resources' }
    ]
  },
  {
    name: 'Monitoramento',
    href: '/dashboard/monitoring',
    icon: Activity,
    badge: null,
    subItems: [
      { name: 'Prometheus', href: 'https://prometheus.kenzysites.com.br', external: true },
      { name: 'Grafana', href: 'https://grafana.kenzysites.com.br', external: true },
      { name: 'Alertas', href: '/dashboard/alerts' },
      { name: 'Uptime', href: '/dashboard/uptime' }
    ]
  },
  {
    name: 'Backups',
    href: '/dashboard/backups',
    icon: Database,
    badge: 'S3',
    subItems: [
      { name: 'Todos Backups', href: '/dashboard/backups' },
      { name: 'Backup Manual', href: '/dashboard/backups/manual' },
      { name: 'Restaurar', href: '/dashboard/backups/restore' },
      { name: 'Configurações', href: '/dashboard/backups/settings' }
    ]
  },
  { 
    name: 'AI & Templates', 
    href: '/dashboard/ai', 
    icon: Zap,
    badge: 'GPT-4',
    subItems: [
      { name: 'Gerador com IA', href: '/dashboard/generator' },
      { name: 'Templates BR', href: '/dashboard/templates/brazilian' },
      { name: 'Personalização ACF', href: '/dashboard/acf' },
      { name: 'Créditos IA', href: '/dashboard/ai-credits' }
    ]
  },
  {
    name: 'Integrações',
    href: '/dashboard/integrations',
    icon: Plug,
    badge: null,
    subItems: [
      { name: 'Cloudflare', href: '/dashboard/integrations/cloudflare' },
      { name: 'Asaas', href: '/dashboard/integrations/asaas' },
      { name: 'SendGrid', href: '/dashboard/integrations/sendgrid' },
      { name: 'WhatsApp', href: '/dashboard/integrations/whatsapp' }
    ]
  },
  { 
    name: 'Configurações', 
    href: '/dashboard/settings', 
    icon: Settings,
    badge: null,
    subItems: [
      { name: 'Perfil', href: '/dashboard/settings/profile' },
      { name: 'Segurança', href: '/dashboard/settings/security' },
      { name: 'API Keys', href: '/dashboard/settings/api' },
      { name: 'Webhooks', href: '/dashboard/settings/webhooks' }
    ]
  },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [expandedItems, setExpandedItems] = useState<string[]>([])
  const pathname = usePathname()

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    )
  }

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setSidebarOpen(false)}>
          <div className="absolute inset-0 bg-gray-600 opacity-75" />
        </div>
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">WP AI Builder</h1>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              const isExpanded = expandedItems.includes(item.name)
              const hasSubItems = item.subItems && item.subItems.length > 0
              
              return (
                <div key={item.name}>
                  {hasSubItems ? (
                    <>
                      <button
                        onClick={() => toggleExpanded(item.name)}
                        className={cn(
                          'group flex items-center justify-between w-full px-3 py-2 text-sm font-medium rounded-md transition-colors',
                          isActive
                            ? 'bg-primary text-primary-foreground'
                            : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                        )}
                      >
                        <div className="flex items-center">
                          <item.icon
                            className={cn(
                              'mr-3 h-5 w-5 flex-shrink-0',
                              isActive
                                ? 'text-primary-foreground'
                                : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'
                            )}
                          />
                          <span>{item.name}</span>
                          {item.badge && (
                            <span className="ml-2 px-1.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                              {item.badge}
                            </span>
                          )}
                        </div>
                        {isExpanded ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </button>
                      
                      {isExpanded && (
                        <div className="mt-1 space-y-1">
                          {item.subItems.map((subItem) => (
                            <Link
                              key={subItem.name}
                              href={subItem.href}
                              target={'external' in subItem && subItem.external ? '_blank' : undefined}
                              rel={'external' in subItem && subItem.external ? 'noopener noreferrer' : undefined}
                              className={cn(
                                'group flex items-center pl-11 pr-3 py-2 text-sm rounded-md transition-colors',
                                pathname === subItem.href
                                  ? 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-white'
                                  : 'text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-700'
                              )}
                            >
                              {subItem.name}
                              {'external' in subItem && subItem.external && (
                                <ExternalLink className="ml-1 h-3 w-3" />
                              )}
                            </Link>
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <Link
                      href={item.href}
                      className={cn(
                        'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                        isActive
                          ? 'bg-primary text-primary-foreground'
                          : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                      )}
                    >
                      <item.icon
                        className={cn(
                          'mr-3 h-5 w-5 flex-shrink-0',
                          isActive
                            ? 'text-primary-foreground'
                            : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'
                        )}
                      />
                      <span>{item.name}</span>
                      {item.badge && (
                        <span className="ml-2 px-1.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  )}
                </div>
              )
            })}
          </div>
        </nav>

        {/* Sidebar footer */}
        <div className="absolute bottom-0 w-full p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <span className="text-sm font-medium text-primary-foreground">U</span>
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">Usuario</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">user@example.com</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center">
              <button className="lg:hidden mr-4" onClick={() => setSidebarOpen(true)}>
                <Menu className="h-6 w-6" />
              </button>

              {/* Global Search */}
              <div className="hidden sm:block">
                <GlobalSearch
                  onResultSelect={(result) => {
                    if (result.url) {
                      window.location.href = result.url
                    }
                  }}
                />
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <Button variant="ghost" size="icon">
                <Bell className="h-5 w-5" />
              </Button>

              {/* User menu */}
              <div className="relative">
                <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                  <div className="h-6 w-6 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-xs font-medium text-primary-foreground">U</span>
                  </div>
                  <span className="hidden sm:block text-sm font-medium">Usuario</span>
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
          <div className="py-6 px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>
    </div>
  )
}
