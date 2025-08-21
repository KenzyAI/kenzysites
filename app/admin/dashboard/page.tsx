'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { 
  Users, 
  Globe, 
  DollarSign, 
  TrendingUp,
  Server,
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Search,
  Filter,
  Download,
  RefreshCw,
  Power,
  Trash2,
  Edit,
  Eye,
  MoreVertical,
  PlusCircle,
  CreditCard,
  Package,
  BarChart3,
  Settings,
  Shield,
  Database,
  Cpu,
  HardDrive,
  Zap,
  AlertTriangle
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface SiteInfo {
  id: string
  client_name: string
  domain: string
  status: 'active' | 'suspended' | 'provisioning' | 'error'
  plan: string
  created_at: string
  last_payment: string
  next_billing: string
  storage_used: number
  bandwidth_used: number
  cpu_usage: number
  memory_usage: number
}

interface SystemMetrics {
  total_sites: number
  active_sites: number
  suspended_sites: number
  total_revenue: number
  mrr: number
  churn_rate: number
  new_sites_month: number
  cpu_usage_avg: number
  memory_usage_avg: number
  storage_total: number
  bandwidth_total: number
}

export default function AdminDashboard() {
  const [sites, setSites] = useState<SiteInfo[]>([
    {
      id: 'wp_rest_001',
      client_name: 'Restaurante do João',
      domain: 'restaurantedojoao.kenzysites.com.br',
      status: 'active',
      plan: 'Professional',
      created_at: '2024-01-15',
      last_payment: '2024-01-15',
      next_billing: '2024-02-15',
      storage_used: 2.3,
      bandwidth_used: 45,
      cpu_usage: 15,
      memory_usage: 512
    },
    {
      id: 'wp_adv_002',
      client_name: 'Advocacia Silva',
      domain: 'advocaciasilva.kenzysites.com.br',
      status: 'active',
      plan: 'Business',
      created_at: '2024-01-10',
      last_payment: '2024-01-10',
      next_billing: '2024-02-10',
      storage_used: 1.8,
      bandwidth_used: 23,
      cpu_usage: 10,
      memory_usage: 256
    },
    {
      id: 'wp_fit_003',
      client_name: 'Academia PowerFit',
      domain: 'powerfit.kenzysites.com.br',
      status: 'suspended',
      plan: 'Starter',
      created_at: '2023-12-20',
      last_payment: '2023-12-20',
      next_billing: '2024-01-20',
      storage_used: 3.1,
      bandwidth_used: 67,
      cpu_usage: 0,
      memory_usage: 0
    },
    {
      id: 'wp_med_004',
      client_name: 'Clínica Saúde+',
      domain: 'clinicasaudemais.kenzysites.com.br',
      status: 'provisioning',
      plan: 'Professional',
      created_at: '2024-01-20',
      last_payment: '2024-01-20',
      next_billing: '2024-02-20',
      storage_used: 0,
      bandwidth_used: 0,
      cpu_usage: 0,
      memory_usage: 0
    }
  ])

  const [metrics, setMetrics] = useState<SystemMetrics>({
    total_sites: 156,
    active_sites: 142,
    suspended_sites: 14,
    total_revenue: 42350,
    mrr: 42350,
    churn_rate: 3.2,
    new_sites_month: 23,
    cpu_usage_avg: 35,
    memory_usage_avg: 62,
    storage_total: 324,
    bandwidth_total: 8940
  })

  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [selectedSite, setSelectedSite] = useState<SiteInfo | null>(null)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'suspended': return 'bg-yellow-500'
      case 'provisioning': return 'bg-blue-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Ativo'
      case 'suspended': return 'Suspenso'
      case 'provisioning': return 'Provisionando'
      case 'error': return 'Erro'
      default: return status
    }
  }

  const handleSuspendSite = async (siteId: string) => {
    console.log(`Suspending site: ${siteId}`)
    // Call API to suspend site
  }

  const handleResumeSite = async (siteId: string) => {
    console.log(`Resuming site: ${siteId}`)
    // Call API to resume site
  }

  const handleDeleteSite = async (siteId: string) => {
    if (confirm('Tem certeza que deseja excluir este site permanentemente?')) {
      console.log(`Deleting site: ${siteId}`)
      // Call API to delete site
    }
  }

  const filteredSites = sites.filter(site => {
    const matchesSearch = site.client_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         site.domain.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterStatus === 'all' || site.status === filterStatus
    return matchesSearch && matchesFilter
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Dashboard Administrativo
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Gerencie todos os sites e clientes da plataforma
            </p>
          </div>
          <div className="flex space-x-4">
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Exportar Relatório
            </Button>
            <Button>
              <PlusCircle className="w-4 h-4 mr-2" />
              Novo Site
            </Button>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center">
                <Globe className="w-4 h-4 mr-2 text-blue-500" />
                Sites Totais
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.total_sites}</div>
              <div className="flex items-center text-xs text-gray-500 mt-1">
                <span className="text-green-500 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  {metrics.new_sites_month} novos este mês
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center">
                <DollarSign className="w-4 h-4 mr-2 text-green-500" />
                MRR
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R$ {metrics.mrr.toLocaleString('pt-BR')}</div>
              <div className="flex items-center text-xs text-gray-500 mt-1">
                <span className="text-red-500 flex items-center">
                  Churn: {metrics.churn_rate}%
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center">
                <Activity className="w-4 h-4 mr-2 text-purple-500" />
                Sites Ativos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.active_sites}</div>
              <div className="flex items-center text-xs text-gray-500 mt-1">
                <span className="text-yellow-500 flex items-center">
                  {metrics.suspended_sites} suspensos
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center">
                <Server className="w-4 h-4 mr-2 text-orange-500" />
                Uso de Recursos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span>CPU</span>
                  <span className="font-medium">{metrics.cpu_usage_avg}%</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span>RAM</span>
                  <span className="font-medium">{metrics.memory_usage_avg}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="sites" className="space-y-4">
          <TabsList>
            <TabsTrigger value="sites">Sites</TabsTrigger>
            <TabsTrigger value="billing">Faturamento</TabsTrigger>
            <TabsTrigger value="resources">Recursos</TabsTrigger>
            <TabsTrigger value="alerts">Alertas</TabsTrigger>
            <TabsTrigger value="settings">Configurações</TabsTrigger>
          </TabsList>

          {/* Sites Tab */}
          <TabsContent value="sites" className="space-y-4">
            {/* Search and Filter */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Buscar por cliente ou domínio..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border rounded-md"
                >
                  <option value="all">Todos os Status</option>
                  <option value="active">Ativos</option>
                  <option value="suspended">Suspensos</option>
                  <option value="provisioning">Provisionando</option>
                  <option value="error">Com Erro</option>
                </select>
              </div>
              <Button variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Atualizar
              </Button>
            </div>

            {/* Sites Table */}
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Domínio</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Plano</TableHead>
                    <TableHead>Recursos</TableHead>
                    <TableHead>Próx. Cobrança</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSites.map((site) => (
                    <TableRow key={site.id}>
                      <TableCell className="font-medium">{site.client_name}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <span className="text-sm">{site.domain}</span>
                          <Button variant="ghost" size="sm" className="ml-2">
                            <Eye className="w-3 h-3" />
                          </Button>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={`${getStatusColor(site.status)} text-white`}>
                          {getStatusText(site.status)}
                        </Badge>
                      </TableCell>
                      <TableCell>{site.plan}</TableCell>
                      <TableCell>
                        <div className="text-xs space-y-1">
                          <div className="flex items-center">
                            <Cpu className="w-3 h-3 mr-1" />
                            CPU: {site.cpu_usage}%
                          </div>
                          <div className="flex items-center">
                            <HardDrive className="w-3 h-3 mr-1" />
                            {site.storage_used} GB
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{new Date(site.next_billing).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Ações</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Eye className="w-4 h-4 mr-2" />
                              Ver Detalhes
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Edit className="w-4 h-4 mr-2" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Settings className="w-4 h-4 mr-2" />
                              Configurações
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {site.status === 'active' ? (
                              <DropdownMenuItem 
                                className="text-yellow-600"
                                onClick={() => handleSuspendSite(site.id)}
                              >
                                <Power className="w-4 h-4 mr-2" />
                                Suspender
                              </DropdownMenuItem>
                            ) : (
                              <DropdownMenuItem 
                                className="text-green-600"
                                onClick={() => handleResumeSite(site.id)}
                              >
                                <CheckCircle2 className="w-4 h-4 mr-2" />
                                Reativar
                              </DropdownMenuItem>
                            )}
                            <DropdownMenuItem 
                              className="text-red-600"
                              onClick={() => handleDeleteSite(site.id)}
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Excluir
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>

          {/* Billing Tab */}
          <TabsContent value="billing" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Receita do Mês</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">R$ {metrics.total_revenue.toLocaleString('pt-BR')}</div>
                  <div className="text-sm text-gray-500 mt-2">
                    <div>Novos clientes: R$ 6.890</div>
                    <div>Renovações: R$ 35.460</div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Inadimplência</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-red-500">R$ 2.340</div>
                  <div className="text-sm text-gray-500 mt-2">
                    <div>14 clientes em atraso</div>
                    <div>Suspensão automática em 7 dias</div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Próximas Cobranças</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">R$ 18.420</div>
                  <div className="text-sm text-gray-500 mt-2">
                    <div>Próximos 7 dias</div>
                    <div>62 renovações previstas</div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Transactions */}
            <Card>
              <CardHeader>
                <CardTitle>Transações Recentes</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Data</TableHead>
                      <TableHead>Cliente</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Valor</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>20/01/2024</TableCell>
                      <TableCell>Restaurante do João</TableCell>
                      <TableCell>PIX</TableCell>
                      <TableCell>R$ 297,00</TableCell>
                      <TableCell>
                        <Badge className="bg-green-500 text-white">Pago</Badge>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>19/01/2024</TableCell>
                      <TableCell>Advocacia Silva</TableCell>
                      <TableCell>Cartão</TableCell>
                      <TableCell>R$ 597,00</TableCell>
                      <TableCell>
                        <Badge className="bg-green-500 text-white">Pago</Badge>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>18/01/2024</TableCell>
                      <TableCell>Academia PowerFit</TableCell>
                      <TableCell>Boleto</TableCell>
                      <TableCell>R$ 97,00</TableCell>
                      <TableCell>
                        <Badge className="bg-yellow-500 text-white">Pendente</Badge>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Resources Tab */}
          <TabsContent value="resources" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Uso de CPU por Node</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Node 1 (k8s-master)</span>
                        <span>42%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '42%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Node 2 (k8s-worker-1)</span>
                        <span>68%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '68%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Node 3 (k8s-worker-2)</span>
                        <span>35%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '35%' }}></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Armazenamento</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>WordPress Files</span>
                        <span>324 GB / 1 TB</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '32%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>MySQL Databases</span>
                        <span>156 GB / 500 GB</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '31%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Backups</span>
                        <span>489 GB / 2 TB</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{ width: '24%' }}></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Kubernetes Pods Status */}
            <Card>
              <CardHeader>
                <CardTitle>Status dos Pods</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-500">142</div>
                    <div className="text-sm text-gray-500">Running</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-yellow-500">3</div>
                    <div className="text-sm text-gray-500">Pending</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-500">1</div>
                    <div className="text-sm text-gray-500">Failed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-gray-500">10</div>
                    <div className="text-sm text-gray-500">Terminated</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Alerts Tab */}
          <TabsContent value="alerts" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Alertas do Sistema</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3 p-3 border rounded-md border-red-200 bg-red-50">
                    <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-medium text-red-900">Pagamento Falhado</div>
                      <div className="text-sm text-red-700">Academia PowerFit - Cartão recusado</div>
                      <div className="text-xs text-red-600 mt-1">Há 2 horas</div>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3 p-3 border rounded-md border-yellow-200 bg-yellow-50">
                    <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-medium text-yellow-900">Alto Uso de CPU</div>
                      <div className="text-sm text-yellow-700">Node k8s-worker-1 está com 89% de uso</div>
                      <div className="text-xs text-yellow-600 mt-1">Há 30 minutos</div>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3 p-3 border rounded-md border-blue-200 bg-blue-50">
                    <Zap className="w-5 h-5 text-blue-500 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-medium text-blue-900">Backup Concluído</div>
                      <div className="text-sm text-blue-700">Backup automático de todos os sites completado</div>
                      <div className="text-xs text-blue-600 mt-1">Há 1 hora</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Configurações Gerais</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Limite de Sites por Node</label>
                    <Input type="number" defaultValue="50" className="mt-1" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Dias de Tolerância para Suspensão</label>
                    <Input type="number" defaultValue="7" className="mt-1" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Backup Automático</label>
                    <select className="w-full px-3 py-2 border rounded-md mt-1">
                      <option>Diário às 02:00</option>
                      <option>Semanal</option>
                      <option>Mensal</option>
                    </select>
                  </div>
                  <Button className="w-full">Salvar Configurações</Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Integrações</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <div className="font-medium">Asaas</div>
                      <div className="text-sm text-gray-500">Gateway de Pagamento</div>
                    </div>
                    <Badge className="bg-green-500 text-white">Conectado</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <div className="font-medium">Cloudflare</div>
                      <div className="text-sm text-gray-500">CDN e DNS</div>
                    </div>
                    <Badge className="bg-green-500 text-white">Conectado</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <div className="font-medium">SendGrid</div>
                      <div className="text-sm text-gray-500">Email Transacional</div>
                    </div>
                    <Badge className="bg-gray-500 text-white">Desconectado</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}