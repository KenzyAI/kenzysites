'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { SitePreview } from '@/components/sites/site-preview'
import { useSites, Site } from '@/lib/hooks/use-sites'
import {
  Globe,
  ArrowLeft,
  Edit,
  Eye,
  Download,
  Upload,
  Activity,
  Users,
  TrendingUp,
  Shield,
  Database,
  Zap,
  AlertCircle,
  CheckCircle,
  Clock,
  ExternalLink,
  RefreshCw,
  Power,
} from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { useToast } from '@/lib/use-toast'
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  AreaChart,
  Area,
} from 'recharts'

// Mock analytics data
const generateAnalyticsData = () => {
  const data = []
  const now = new Date()

  for (let i = 29; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)

    data.push({
      date: format(date, 'dd/MM'),
      visitors: Math.floor(Math.random() * 500) + 100,
      pageViews: Math.floor(Math.random() * 1000) + 200,
      bounceRate: Math.floor(Math.random() * 20) + 30,
      avgSession: Math.floor(Math.random() * 180) + 120,
    })
  }

  return data
}

const mockAnalytics = generateAnalyticsData()

const statusColors = {
  active: 'bg-green-500',
  inactive: 'bg-red-500',
  maintenance: 'bg-yellow-500',
  suspended: 'bg-gray-500',
}

const statusLabels = {
  active: 'Ativo',
  inactive: 'Inativo',
  maintenance: 'Manutenção',
  suspended: 'Suspenso',
}

const planLabels = {
  basic: 'Básico',
  pro: 'Pro',
  enterprise: 'Enterprise',
}

export default function SiteDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const { getSite, updateSite } = useSites()
  const { toast } = useToast()

  const [site, setSite] = useState<Site | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  const siteId = parseInt(params.id as string)

  useEffect(() => {
    const loadSite = async () => {
      try {
        const siteData = await getSite(siteId)
        setSite(siteData)
      } catch {
        toast({
          title: 'Erro ao carregar site',
          description: 'Não foi possível carregar os dados do site.',
          variant: 'destructive',
        })
        router.push('/dashboard/sites')
      } finally {
        setLoading(false)
      }
    }

    if (siteId) {
      loadSite()
    }
  }, [siteId, getSite, router, toast])

  const handleStatusChange = async (newStatus: Site['status']) => {
    if (!site) return

    try {
      setActionLoading(true)
      const updatedSite = await updateSite({ id: site.id, status: newStatus })
      setSite(updatedSite)
      toast({
        title: 'Status atualizado',
        description: `Site alterado para "${statusLabels[newStatus]}".`,
      })
    } catch {
      toast({
        title: 'Erro ao atualizar status',
        description: 'Não foi possível alterar o status do site.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleCopyUrl = (url: string) => {
    navigator.clipboard.writeText(url)
    toast({
      title: 'URL copiada!',
      description: 'A URL foi copiada para sua área de transferência.',
    })
  }

  const calculateUsage = (used: number, limit: number) => {
    return Math.min((used / limit) * 100, 100)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 bg-muted rounded animate-pulse" />
          <div className="space-y-2">
            <div className="h-8 bg-muted rounded animate-pulse w-64" />
            <div className="h-4 bg-muted rounded animate-pulse w-48" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-20 bg-muted rounded animate-pulse" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (!site) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-medium">Site não encontrado</h3>
        <p className="text-muted-foreground mb-4">O site solicitado não existe ou foi removido.</p>
        <Button onClick={() => router.push('/dashboard/sites')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar para Sites
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/dashboard/sites')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>

          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold tracking-tight">{site.name}</h1>
              <Badge variant="secondary" className="flex items-center gap-1">
                <div className={`h-2 w-2 rounded-full ${statusColors[site.status]}`} />
                {statusLabels[site.status]}
              </Badge>
            </div>

            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Globe className="h-4 w-4" />
                <button
                  className="hover:text-primary transition-colors"
                  onClick={() => handleCopyUrl(`https://${site.domain}`)}
                >
                  {site.domain}
                </button>
              </div>

              {site.customDomain && (
                <div className="flex items-center gap-1">
                  <ExternalLink className="h-4 w-4" />
                  <button
                    className="hover:text-primary transition-colors"
                    onClick={() => handleCopyUrl(`https://${site.customDomain}`)}
                  >
                    {site.customDomain}
                  </button>
                </div>
              )}

              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                Criado em {format(site.createdAt, 'dd/MM/yyyy', { locale: ptBR })}
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <SitePreview site={site}>
            <Button variant="outline" size="sm">
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
          </SitePreview>

          <Button variant="outline" size="sm" asChild>
            <a href={`https://${site.domain}`} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="h-4 w-4 mr-2" />
              Abrir Site
            </a>
          </Button>

          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Editar
          </Button>

          <Button
            variant={site.status === 'active' ? 'destructive' : 'default'}
            size="sm"
            onClick={() => handleStatusChange(site.status === 'active' ? 'inactive' : 'active')}
            disabled={actionLoading}
          >
            <Power className="h-4 w-4 mr-2" />
            {site.status === 'active' ? 'Desativar' : 'Ativar'}
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Visitantes (30d)</p>
                <p className="text-2xl font-bold">{site.visitors.toLocaleString()}</p>
                <p className="text-xs text-green-600">+12% vs mês anterior</p>
              </div>
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Plano</p>
                <p className="text-2xl font-bold">{planLabels[site.plan]}</p>
                <p className="text-xs text-muted-foreground">
                  {site.plan === 'basic'
                    ? 'R$ 29/mês'
                    : site.plan === 'pro'
                      ? 'R$ 79/mês'
                      : 'R$ 199/mês'}
                </p>
              </div>
              <Zap className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Uptime</p>
                <p className="text-2xl font-bold">99.9%</p>
                <p className="text-xs text-green-600">Últimos 30 dias</p>
              </div>
              <Activity className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Backups</p>
                <p className="text-2xl font-bold">{site.backups}</p>
                <p className="text-xs text-muted-foreground">Último: hoje</p>
              </div>
              <Database className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="settings">Configurações</TabsTrigger>
          <TabsTrigger value="backup">Backup</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Site Info */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Informações do Site</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Categoria</p>
                    <p className="text-sm capitalize">{site.category.replace('-', ' ')}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Tema</p>
                    <p className="text-sm">{site.theme}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">WordPress</p>
                    <p className="text-sm">{site.wpVersion || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">PHP</p>
                    <p className="text-sm">{site.phpVersion}</p>
                  </div>
                </div>

                <Separator />

                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Proprietário</p>
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-xs text-primary-foreground">
                      {site.owner.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{site.owner}</p>
                      <p className="text-xs text-muted-foreground">{site.ownerEmail}</p>
                    </div>
                  </div>
                </div>

                {site.description && (
                  <>
                    <Separator />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-1">Descrição</p>
                      <p className="text-sm">{site.description}</p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Resource Usage */}
            <Card>
              <CardHeader>
                <CardTitle>Uso de Recursos</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Armazenamento</span>
                    <span>
                      {site.storage}MB /{' '}
                      {site.plan === 'basic' ? '1GB' : site.plan === 'pro' ? '5GB' : '10GB'}
                    </span>
                  </div>
                  <Progress
                    value={calculateUsage(
                      site.storage,
                      site.plan === 'basic' ? 1024 : site.plan === 'pro' ? 5120 : 10240
                    )}
                    className="h-2"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Tráfego (mês)</span>
                    <span>
                      {site.bandwidth}GB /{' '}
                      {site.plan === 'basic' ? '10GB' : site.plan === 'pro' ? '50GB' : '100GB'}
                    </span>
                  </div>
                  <Progress
                    value={calculateUsage(
                      site.bandwidth,
                      site.plan === 'basic' ? 10 : site.plan === 'pro' ? 50 : 100
                    )}
                    className="h-2"
                  />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span>SSL</span>
                  <div className="flex items-center gap-1">
                    {site.ssl ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-green-600">Ativo</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-600" />
                        <span className="text-red-600">Inativo</span>
                      </>
                    )}
                  </div>
                </div>

                <Separator />

                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Plugins Ativos</p>
                  <div className="flex flex-wrap gap-1">
                    {site.plugins.map((plugin) => (
                      <Badge key={plugin} variant="outline" className="text-xs">
                        {plugin}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Atividade Recente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  {
                    action: 'Plugin atualizado',
                    detail: 'Yoast SEO v21.8',
                    time: '2 horas atrás',
                    type: 'update',
                  },
                  {
                    action: 'Backup criado',
                    detail: 'Backup automático diário',
                    time: '6 horas atrás',
                    type: 'backup',
                  },
                  {
                    action: 'Tema personalizado',
                    detail: 'Cores alteradas no customizer',
                    time: '1 dia atrás',
                    type: 'customization',
                  },
                  {
                    action: 'Post publicado',
                    detail: 'Como melhorar seu SEO',
                    time: '2 dias atrás',
                    type: 'content',
                  },
                ].map((activity, index) => (
                  <div key={index} className="flex items-start gap-3 pb-3 last:pb-0">
                    <div
                      className={`h-2 w-2 rounded-full mt-2 ${
                        activity.type === 'update'
                          ? 'bg-blue-500'
                          : activity.type === 'backup'
                            ? 'bg-green-500'
                            : activity.type === 'customization'
                              ? 'bg-purple-500'
                              : 'bg-orange-500'
                      }`}
                    />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.detail}</p>
                      <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Visitantes Únicos</p>
                    <p className="text-2xl font-bold">12,847</p>
                    <p className="text-xs text-green-600">+15.2% vs mês anterior</p>
                  </div>
                  <Users className="h-8 w-8 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Visualizações</p>
                    <p className="text-2xl font-bold">28,430</p>
                    <p className="text-xs text-green-600">+8.7% vs mês anterior</p>
                  </div>
                  <Eye className="h-8 w-8 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Taxa de Rejeição</p>
                    <p className="text-2xl font-bold">42%</p>
                    <p className="text-xs text-red-600">+2.1% vs mês anterior</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Sessão Média</p>
                    <p className="text-2xl font-bold">3m 42s</p>
                    <p className="text-xs text-green-600">+5.4% vs mês anterior</p>
                  </div>
                  <Clock className="h-8 w-8 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Visitantes nos Últimos 30 Dias</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={mockAnalytics}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="date" className="text-xs fill-muted-foreground" />
                  <YAxis className="text-xs fill-muted-foreground" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '6px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="visitors"
                    stroke="hsl(var(--primary))"
                    fill="hsl(var(--primary))"
                    fillOpacity={0.1}
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Speed Score</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-green-600 mb-2">87</div>
                  <p className="text-sm text-muted-foreground">Performance Score</p>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">First Contentful Paint</span>
                    <span className="text-sm text-green-600">1.2s</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Largest Contentful Paint</span>
                    <span className="text-sm text-yellow-600">2.8s</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Time to Interactive</span>
                    <span className="text-sm text-green-600">3.1s</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Cumulative Layout Shift</span>
                    <span className="text-sm text-green-600">0.05</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Configurações de Cache</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Cache de Página</p>
                    <p className="text-sm text-muted-foreground">Acelera o carregamento</p>
                  </div>
                  <div className="flex items-center gap-1">
                    {site.settings.cacheEnabled ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-600">Ativo</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-600" />
                        <span className="text-sm text-red-600">Inativo</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Compressão GZIP</p>
                    <p className="text-sm text-muted-foreground">Reduz tamanho dos arquivos</p>
                  </div>
                  <div className="flex items-center gap-1">
                    {site.settings.compressionEnabled ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-600">Ativo</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-600" />
                        <span className="text-sm text-red-600">Inativo</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">CDN</p>
                    <p className="text-sm text-muted-foreground">Distribuição global</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600">Ativo</span>
                  </div>
                </div>

                <Button className="w-full mt-4">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Limpar Cache
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Configurações Gerais</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Modo de Manutenção</p>
                    <p className="text-sm text-muted-foreground">Desativa temporariamente o site</p>
                  </div>
                  <div className="flex items-center gap-1">
                    {site.settings.maintenanceMode ? (
                      <>
                        <AlertCircle className="h-4 w-4 text-yellow-600" />
                        <span className="text-sm text-yellow-600">Ativo</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-600">Inativo</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">SEO</p>
                    <p className="text-sm text-muted-foreground">
                      Otimização para mecanismos de busca
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    {site.settings.seoEnabled ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-600">Ativo</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-600" />
                        <span className="text-sm text-red-600">Inativo</span>
                      </>
                    )}
                  </div>
                </div>

                {site.settings.analyticsId && (
                  <div>
                    <p className="font-medium">Google Analytics</p>
                    <p className="text-sm text-muted-foreground">ID: {site.settings.analyticsId}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Segurança</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Certificado SSL</p>
                    <p className="text-sm text-muted-foreground">Criptografia HTTPS</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Shield className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600">Ativo</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Firewall</p>
                    <p className="text-sm text-muted-foreground">Proteção contra ataques</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Shield className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600">Ativo</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Backup Automático</p>
                    <p className="text-sm text-muted-foreground">Diário às 02:00</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600">Ativo</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Backup Tab */}
        <TabsContent value="backup" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Backups Disponíveis</CardTitle>
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Criar Backup
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { date: new Date(), type: 'Automático', size: '245 MB', status: 'success' },
                  {
                    date: new Date(Date.now() - 86400000),
                    type: 'Automático',
                    size: '238 MB',
                    status: 'success',
                  },
                  {
                    date: new Date(Date.now() - 172800000),
                    type: 'Manual',
                    size: '251 MB',
                    status: 'success',
                  },
                  {
                    date: new Date(Date.now() - 259200000),
                    type: 'Automático',
                    size: '247 MB',
                    status: 'success',
                  },
                ].map((backup, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-2 w-2 rounded-full ${backup.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}
                      />
                      <div>
                        <p className="font-medium">Backup {backup.type}</p>
                        <p className="text-sm text-muted-foreground">
                          {format(backup.date, "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })} •{' '}
                          {backup.size}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
