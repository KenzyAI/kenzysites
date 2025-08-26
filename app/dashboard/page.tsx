"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { StatsCard } from "@/components/dashboard/stats-card"
import { SiteCard } from "@/components/dashboard/site-card"
import { UsageChart } from "@/components/dashboard/usage-chart"
import { 
  Globe, 
  Layers, 
  Sparkles, 
  TrendingUp, 
  Users,
  Clock,
  Zap,
  DollarSign,
  Activity,
  Eye,
  MousePointer,
  Target
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"

// Dados mockados para demonstração
const mockStats = {
  totalSites: 12,
  totalVariations: 36,
  aiCreditsUsed: 2450,
  aiCreditsTotal: 5000,
  activeVisitors: 234,
  monthlyViews: 15420,
  averagePageSpeed: 92,
  conversionRate: 3.4
}

const mockChartData = {
  sitesCreated: [
    { date: '01 Jan', sites: 2 },
    { date: '05 Jan', sites: 3 },
    { date: '10 Jan', sites: 1 },
    { date: '15 Jan', sites: 4 },
    { date: '20 Jan', sites: 2 },
    { date: '25 Jan', sites: 3 },
    { date: '30 Jan', sites: 5 },
  ],
  aiUsage: [
    { date: '01 Jan', credits: 120, generations: 4 },
    { date: '05 Jan', credits: 340, generations: 8 },
    { date: '10 Jan', credits: 210, generations: 5 },
    { date: '15 Jan', credits: 480, generations: 12 },
    { date: '20 Jan', credits: 290, generations: 7 },
    { date: '25 Jan', credits: 380, generations: 9 },
    { date: '30 Jan', credits: 630, generations: 15 },
  ],
  templateUsage: [
    { name: 'Restaurant', value: 35, count: 7 },
    { name: 'Healthcare', value: 25, count: 5 },
    { name: 'E-commerce', value: 20, count: 4 },
    { name: 'Services', value: 15, count: 3 },
    { name: 'Education', value: 5, count: 1 },
  ],
  performance: [
    { metric: 'PageSpeed', desktop: 92, mobile: 85 },
    { metric: 'SEO', desktop: 98, mobile: 96 },
    { metric: 'Accessibility', desktop: 100, mobile: 98 },
    { metric: 'Best Practices', desktop: 95, mobile: 93 },
  ]
}

const mockRecentSites = [
  {
    id: '1',
    name: 'Restaurante Sabor Brasileiro',
    url: 'https://sabor-brasileiro.demo.com',
    status: 'active' as const,
    template: 'Restaurant Modern',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-20'),
    updatedAt: new Date('2025-01-20'),
    industry: 'restaurant',
    variations: 3,
    pageSpeed: 94
  },
  {
    id: '2',
    name: 'Clínica Saúde Total',
    url: 'https://saude-total.demo.com',
    status: 'building' as const,
    template: 'Healthcare Professional',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-18'),
    updatedAt: new Date('2025-01-19'),
    industry: 'healthcare',
    variations: 4,
    pageSpeed: 88
  },
  {
    id: '3',
    name: 'TechSolutions Pro',
    url: 'https://techsolutions.demo.com',
    status: 'active' as const,
    template: 'Services Corporate',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-15'),
    updatedAt: new Date('2025-01-16'),
    industry: 'services',
    variations: 5,
    pageSpeed: 96
  },
]

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d')
  
  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => setLoading(false), 1000)
  }, [])

  const handleSiteAction = (action: string, siteId: string) => {
    toast.success(`${action} site ${siteId}`)
  }

  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Bem-vindo de volta! Aqui está um resumo da sua conta.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm">
            <Clock className="w-4 h-4 mr-2" />
            Últimos {timeRange === '7d' ? '7 dias' : timeRange === '30d' ? '30 dias' : '3 meses'}
          </Button>
          <Button asChild>
            <Link href="/generation">
              <Sparkles className="w-4 h-4 mr-2" />
              Criar Novo Site
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Sites Criados"
          value={mockStats.totalSites}
          icon={<Globe className="w-5 h-5 text-primary" />}
          description="Total de sites ativos"
          change={25}
          changeType="increase"
          loading={loading}
        />
        <StatsCard
          title="Variações Geradas"
          value={mockStats.totalVariations}
          icon={<Layers className="w-5 h-5 text-primary" />}
          description="Total de variações"
          change={15}
          changeType="increase"
          loading={loading}
        />
        <StatsCard
          title="Créditos de IA"
          value={`${mockStats.aiCreditsUsed} / ${mockStats.aiCreditsTotal}`}
          icon={<Sparkles className="w-5 h-5 text-primary" />}
          description="Créditos utilizados este mês"
          change={-12}
          changeType="decrease"
          loading={loading}
        />
        <StatsCard
          title="PageSpeed Médio"
          value={mockStats.averagePageSpeed}
          icon={<Zap className="w-5 h-5 text-primary" />}
          description="Score médio dos sites"
          change={8}
          changeType="increase"
          loading={loading}
        />
      </div>

      {/* Charts Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            <div className="col-span-4">
              <UsageChart
                data={mockChartData.sitesCreated}
                type="area"
                dataKey="sites"
                xAxisKey="date"
                title="Sites Criados ao Longo do Tempo"
                loading={loading}
              />
            </div>
            <div className="col-span-3">
              <UsageChart
                data={mockChartData.templateUsage}
                type="pie"
                dataKey="value"
                title="Templates Mais Usados"
                loading={loading}
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <UsageChart
              data={mockChartData.aiUsage}
              type="line"
              dataKey={['credits', 'generations']}
              xAxisKey="date"
              title="Uso de IA"
              loading={loading}
            />
            <UsageChart
              data={mockChartData.performance}
              type="bar"
              dataKey={['desktop', 'mobile']}
              xAxisKey="metric"
              title="Métricas de Performance"
              loading={loading}
            />
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Visitantes Ativos"
              value={mockStats.activeVisitors}
              icon={<Users className="w-5 h-5 text-primary" />}
              description="Últimas 24 horas"
              change={18}
              changeType="increase"
            />
            <StatsCard
              title="Visualizações"
              value={mockStats.monthlyViews.toLocaleString()}
              icon={<Eye className="w-5 h-5 text-primary" />}
              description="Este mês"
              change={32}
              changeType="increase"
            />
            <StatsCard
              title="Taxa de Cliques"
              value="5.2%"
              icon={<MousePointer className="w-5 h-5 text-primary" />}
              description="CTR médio"
              change={8}
              changeType="increase"
            />
            <StatsCard
              title="Taxa de Conversão"
              value={`${mockStats.conversionRate}%`}
              icon={<Target className="w-5 h-5 text-primary" />}
              description="Média geral"
              change={12}
              changeType="increase"
            />
          </div>

          <UsageChart
            data={[
              { date: '01 Jan', visitantes: 120, pageviews: 450, conversões: 12 },
              { date: '05 Jan', visitantes: 180, pageviews: 620, conversões: 18 },
              { date: '10 Jan', visitantes: 140, pageviews: 480, conversões: 14 },
              { date: '15 Jan', visitantes: 220, pageviews: 780, conversões: 24 },
              { date: '20 Jan', visitantes: 190, pageviews: 650, conversões: 20 },
              { date: '25 Jan', visitantes: 240, pageviews: 820, conversões: 28 },
              { date: '30 Jan', visitantes: 280, pageviews: 920, conversões: 32 },
            ]}
            type="area"
            dataKey={['visitantes', 'pageviews', 'conversões']}
            xAxisKey="date"
            title="Métricas de Tráfego"
            height={400}
            loading={loading}
          />
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid gap-4">
            <UsageChart
              data={[
                { hora: '00:00', cpu: 45, memoria: 62, rede: 28 },
                { hora: '04:00', cpu: 38, memoria: 58, rede: 22 },
                { hora: '08:00', cpu: 65, memoria: 72, rede: 45 },
                { hora: '12:00', cpu: 78, memoria: 85, rede: 68 },
                { hora: '16:00', cpu: 72, memoria: 78, rede: 58 },
                { hora: '20:00', cpu: 58, memoria: 68, rede: 42 },
                { hora: '24:00', cpu: 42, memoria: 60, rede: 25 },
              ]}
              type="area"
              dataKey={['cpu', 'memoria', 'rede']}
              xAxisKey="hora"
              title="Uso de Recursos do Sistema (%)"
              height={400}
              loading={loading}
            />
          </div>
        </TabsContent>
      </Tabs>

      {/* Recent Sites */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Sites Recentes</h2>
          <Button variant="outline" asChild>
            <Link href="/dashboard/sites">
              Ver Todos
            </Link>
          </Button>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {mockRecentSites.map((site) => (
            <SiteCard
              key={site.id}
              {...site}
              onEdit={() => handleSiteAction('Edit', site.id)}
              onClone={() => handleSiteAction('Clone', site.id)}
              onDelete={() => handleSiteAction('Delete', site.id)}
              onExport={() => handleSiteAction('Export', site.id)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
