'use client'

import { StatCard } from '@/components/ui/stat-card'
import { useDashboardData } from '@/lib/hooks/use-dashboard-data'
import { Globe, Users, Zap, DollarSign, Activity, TrendingUp } from 'lucide-react'

export function OverviewStats() {
  const { stats, loading, error } = useDashboardData()

  if (error) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="col-span-full text-center p-8 text-muted-foreground">
          Erro ao carregar estatísticas: {error}
        </div>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Sites Ativos"
        value={loading ? 0 : stats?.activeSites || 0}
        description={`de ${loading ? 0 : stats?.totalSites || 0} total`}
        icon={Globe}
        trend={
          stats && !loading
            ? {
                value: stats.trendsData.sites.value,
                label: 'desde o mês passado',
                positive: stats.trendsData.sites.positive,
              }
            : undefined
        }
        loading={loading}
      />

      <StatCard
        title="Visitantes Totais"
        value={loading ? 0 : stats?.totalVisitors.toLocaleString() || 0}
        icon={Users}
        trend={
          stats && !loading
            ? {
                value: stats.trendsData.visitors.value,
                label: 'desde a semana passada',
                positive: stats.trendsData.visitors.positive,
              }
            : undefined
        }
        loading={loading}
      />

      <StatCard
        title="Créditos IA"
        value={loading ? '0/0' : `${stats?.aiCreditsUsed || 0}/${stats?.aiCreditsTotal || 0}`}
        description={`${loading ? 0 : Math.round(((stats?.aiCreditsUsed || 0) / (stats?.aiCreditsTotal || 1)) * 100)}% utilizados`}
        icon={Zap}
        trend={
          stats && !loading
            ? {
                value: stats.trendsData.credits.value,
                label: 'uso neste mês',
                positive: stats.trendsData.credits.positive,
              }
            : undefined
        }
        loading={loading}
      />

      <StatCard
        title="Receita Mensal"
        value={loading ? 'R$ 0' : `R$ ${(stats?.monthlyRevenue || 0).toLocaleString()}`}
        icon={DollarSign}
        trend={
          stats && !loading
            ? {
                value: stats.trendsData.revenue.value,
                label: 'desde o mês passado',
                positive: stats.trendsData.revenue.positive,
              }
            : undefined
        }
        loading={loading}
      />
    </div>
  )
}
