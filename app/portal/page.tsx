'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Globe, 
  Settings, 
  CreditCard, 
  BarChart3, 
  FileText,
  Shield,
  HardDrive,
  Users,
  Mail,
  Phone,
  MessageSquare,
  ExternalLink,
  Download,
  RefreshCw,
  Power,
  AlertCircle,
  CheckCircle2,
  Clock,
  DollarSign,
  Activity,
  Zap,
  Database,
  Lock
} from 'lucide-react'

interface SiteData {
  domain: string
  status: 'active' | 'suspended' | 'provisioning' | 'error'
  plan: string
  storage_used: number
  storage_limit: number
  bandwidth_used: number
  bandwidth_limit: number
  visitors_month: number
  uptime_percentage: number
  ssl_status: 'active' | 'pending' | 'expired'
  last_backup: string
  wp_version: string
  php_version: string
  created_at: string
}

interface BillingData {
  current_plan: string
  price: number
  next_billing: string
  payment_method: string
  status: 'active' | 'overdue' | 'cancelled'
  invoices: Array<{
    id: string
    date: string
    amount: number
    status: 'paid' | 'pending'
  }>
}

export default function ClientPortal() {
  const [siteData, setSiteData] = useState<SiteData>({
    domain: 'meurestaurante.kenzysites.com.br',
    status: 'active',
    plan: 'Professional',
    storage_used: 2.3,
    storage_limit: 10,
    bandwidth_used: 45,
    bandwidth_limit: 100,
    visitors_month: 3542,
    uptime_percentage: 99.9,
    ssl_status: 'active',
    last_backup: '2024-01-20 02:00',
    wp_version: '6.4.2',
    php_version: '8.2',
    created_at: '2024-01-01'
  })

  const [billingData, setBillingData] = useState<BillingData>({
    current_plan: 'Professional',
    price: 297,
    next_billing: '2024-02-01',
    payment_method: 'Cartão **** 1234',
    status: 'active',
    invoices: [
      { id: 'INV-001', date: '2024-01-01', amount: 297, status: 'paid' },
      { id: 'INV-002', date: '2023-12-01', amount: 297, status: 'paid' }
    ]
  })

  const [activeTab, setActiveTab] = useState('overview')

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'suspended': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle2 className="w-4 h-4" />
      case 'suspended': return <AlertCircle className="w-4 h-4" />
      case 'error': return <AlertCircle className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Portal do Cliente
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gerencie seu site WordPress com facilidade
          </p>
        </div>

        {/* Site Status Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Globe className="w-8 h-8 text-blue-500" />
                <div>
                  <CardTitle className="text-xl">{siteData.domain}</CardTitle>
                  <CardDescription>Criado em {new Date(siteData.created_at).toLocaleDateString('pt-BR')}</CardDescription>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Badge className={`${getStatusColor(siteData.status)} text-white`}>
                  <span className="flex items-center gap-1">
                    {getStatusIcon(siteData.status)}
                    {siteData.status === 'active' ? 'Ativo' : 
                     siteData.status === 'suspended' ? 'Suspenso' : 
                     siteData.status === 'provisioning' ? 'Provisionando' : 'Erro'}
                  </span>
                </Badge>
                <Button variant="outline" size="sm">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Visitar Site
                </Button>
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4 mr-2" />
                  WP Admin
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5 mb-6">
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="billing">Faturamento</TabsTrigger>
            <TabsTrigger value="backups">Backups</TabsTrigger>
            <TabsTrigger value="settings">Configurações</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Storage Card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center">
                    <HardDrive className="w-4 h-4 mr-2" />
                    Armazenamento
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{siteData.storage_used} GB</div>
                  <Progress 
                    value={(siteData.storage_used / siteData.storage_limit) * 100} 
                    className="mt-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    de {siteData.storage_limit} GB
                  </p>
                </CardContent>
              </Card>

              {/* Bandwidth Card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center">
                    <Activity className="w-4 h-4 mr-2" />
                    Banda
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{siteData.bandwidth_used} GB</div>
                  <Progress 
                    value={(siteData.bandwidth_used / siteData.bandwidth_limit) * 100} 
                    className="mt-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    de {siteData.bandwidth_limit} GB
                  </p>
                </CardContent>
              </Card>

              {/* Visitors Card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center">
                    <Users className="w-4 h-4 mr-2" />
                    Visitantes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{siteData.visitors_month.toLocaleString()}</div>
                  <p className="text-xs text-gray-500 mt-1">
                    neste mês
                  </p>
                </CardContent>
              </Card>

              {/* Uptime Card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center">
                    <Zap className="w-4 h-4 mr-2" />
                    Uptime
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{siteData.uptime_percentage}%</div>
                  <p className="text-xs text-gray-500 mt-1">
                    últimos 30 dias
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Ações Rápidas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button variant="outline" className="justify-start">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Limpar Cache
                  </Button>
                  <Button variant="outline" className="justify-start">
                    <Database className="w-4 h-4 mr-2" />
                    Backup Manual
                  </Button>
                  <Button variant="outline" className="justify-start">
                    <Shield className="w-4 h-4 mr-2" />
                    Scan Segurança
                  </Button>
                  <Button variant="outline" className="justify-start">
                    <FileText className="w-4 h-4 mr-2" />
                    Logs do Site
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* System Info */}
            <Card>
              <CardHeader>
                <CardTitle>Informações do Sistema</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">WordPress</p>
                    <p className="font-medium">{siteData.wp_version}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">PHP</p>
                    <p className="font-medium">{siteData.php_version}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">SSL</p>
                    <Badge variant={siteData.ssl_status === 'active' ? 'default' : 'destructive'}>
                      {siteData.ssl_status === 'active' ? 'Ativo' : 'Expirado'}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Plano</p>
                    <p className="font-medium">{siteData.plan}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Último Backup</p>
                    <p className="font-medium">{siteData.last_backup}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <Badge className={`${getStatusColor(siteData.status)} text-white`}>
                      {siteData.status === 'active' ? 'Ativo' : 'Suspenso'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Métricas de Performance</CardTitle>
                <CardDescription>Dados dos últimos 30 dias</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">PageSpeed Score</span>
                    <Badge className="bg-green-500 text-white">92/100</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Tempo de Carregamento</span>
                    <span className="text-sm">1.2s</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Taxa de Rejeição</span>
                    <span className="text-sm">32%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Cache Hit Rate</span>
                    <span className="text-sm">94%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Billing Tab */}
          <TabsContent value="billing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Informações de Faturamento</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div>
                    <p className="text-sm text-gray-500">Plano Atual</p>
                    <p className="font-medium">{billingData.current_plan}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Valor Mensal</p>
                    <p className="font-medium">R$ {billingData.price}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Próximo Vencimento</p>
                    <p className="font-medium">{new Date(billingData.next_billing).toLocaleDateString('pt-BR')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Forma de Pagamento</p>
                    <p className="font-medium">{billingData.payment_method}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="font-medium mb-2">Faturas Recentes</h3>
                  {billingData.invoices.map((invoice) => (
                    <div key={invoice.id} className="flex items-center justify-between p-3 border rounded">
                      <div>
                        <p className="font-medium">{invoice.id}</p>
                        <p className="text-sm text-gray-500">{new Date(invoice.date).toLocaleDateString('pt-BR')}</p>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="font-medium">R$ {invoice.amount}</span>
                        <Badge variant={invoice.status === 'paid' ? 'default' : 'destructive'}>
                          {invoice.status === 'paid' ? 'Pago' : 'Pendente'}
                        </Badge>
                        <Button variant="ghost" size="sm">
                          <Download className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex space-x-4 mt-6">
                  <Button>
                    <CreditCard className="w-4 h-4 mr-2" />
                    Atualizar Cartão
                  </Button>
                  <Button variant="outline">
                    Alterar Plano
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Backups Tab */}
          <TabsContent value="backups" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Gerenciamento de Backups</CardTitle>
                <CardDescription>Backups automáticos diários às 02:00</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded">
                    <div>
                      <p className="font-medium">Backup Completo</p>
                      <p className="text-sm text-gray-500">20/01/2024 02:00</p>
                    </div>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                      <Button variant="outline" size="sm">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Restaurar
                      </Button>
                    </div>
                  </div>
                </div>

                <Button className="mt-4">
                  <Database className="w-4 h-4 mr-2" />
                  Criar Backup Manual
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Configurações do Site</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-2">Domínio Personalizado</h3>
                    <div className="flex space-x-2">
                      <input 
                        type="text" 
                        className="flex-1 px-3 py-2 border rounded-md"
                        placeholder="www.seudominio.com.br"
                      />
                      <Button>Configurar</Button>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Integração WhatsApp</h3>
                    <div className="flex space-x-2">
                      <input 
                        type="text" 
                        className="flex-1 px-3 py-2 border rounded-md"
                        placeholder="11999999999"
                      />
                      <Button>Salvar</Button>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Zona de Perigo</h3>
                    <div className="p-4 border border-red-200 rounded-md bg-red-50">
                      <p className="text-sm text-red-600 mb-3">
                        Ações irreversíveis. Use com cuidado.
                      </p>
                      <div className="space-x-2">
                        <Button variant="outline" className="text-red-600 border-red-600">
                          <Power className="w-4 h-4 mr-2" />
                          Suspender Site
                        </Button>
                        <Button variant="destructive">
                          <AlertCircle className="w-4 h-4 mr-2" />
                          Excluir Site
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Support Section */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Precisa de Ajuda?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="outline" className="justify-start">
                <MessageSquare className="w-4 h-4 mr-2" />
                Chat ao Vivo
              </Button>
              <Button variant="outline" className="justify-start">
                <Mail className="w-4 h-4 mr-2" />
                suporte@kenzysites.com.br
              </Button>
              <Button variant="outline" className="justify-start">
                <Phone className="w-4 h-4 mr-2" />
                WhatsApp: (11) 99999-9999
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}