'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { OverviewStats } from '@/components/dashboard/overview-stats'
import { ActivityChart } from '@/components/dashboard/activity-chart'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { AdvancedFilters } from '@/components/dashboard/advanced-filters'
import { DataTable } from '@/components/dashboard/data-table'
import { Zap, Globe, TrendingUp, Clock } from 'lucide-react'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Bem-vindo ao seu painel de controle WordPress AI Builder
          </p>
        </div>
        <Button>
          <Zap className="mr-2 h-4 w-4" />
          Criar Site
        </Button>
      </div>

      {/* Advanced Filters */}
      <AdvancedFilters 
        onFiltersChange={(filters) => console.log('Filters changed:', filters)}
        onSearch={(query) => console.log('Search query:', query)}
        onClear={() => console.log('Filters cleared')}
      />

      {/* Stats Cards */}
      <OverviewStats />

      {/* Data Table with Pagination */}
      <DataTable />

      {/* Charts and Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <ActivityChart />
        <RecentActivity />
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Ação Rápida</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button className="w-full" variant="outline">
              <Zap className="mr-2 h-4 w-4" />
              Gerar Conteúdo com IA
            </Button>
            <Button className="w-full" variant="outline">
              <Globe className="mr-2 h-4 w-4" />
              Ver Todos os Sites
            </Button>
            <Button className="w-full" variant="outline">
              <TrendingUp className="mr-2 h-4 w-4" />
              Relatórios de Analytics
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Próximas Tarefas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Backup em 2 dias</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Renovação em 15 dias</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Update WordPress</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Suporte</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Precisa de ajuda? Nossa equipe está aqui para você.
            </p>
            <div className="space-y-2">
              <Button variant="outline" size="sm" className="w-full">
                Abrir Chamado
              </Button>
              <Button variant="ghost" size="sm" className="w-full">
                Ver Documentação
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
