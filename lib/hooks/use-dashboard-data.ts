import { useState, useEffect } from 'react'

export interface DashboardStats {
  totalSites: number
  activeSites: number
  totalVisitors: number
  aiCreditsUsed: number
  aiCreditsTotal: number
  monthlyRevenue: number
  trendsData: {
    sites: { value: number; positive: boolean }
    visitors: { value: number; positive: boolean }
    revenue: { value: number; positive: boolean }
    credits: { value: number; positive: boolean }
  }
}

export interface ChartData {
  name: string
  visitors: number
  sites: number
  revenue: number
}

// Mock data - será substituído por API real
const mockStats: DashboardStats = {
  totalSites: 24,
  activeSites: 22,
  totalVisitors: 5847,
  aiCreditsUsed: 2340,
  aiCreditsTotal: 5000,
  monthlyRevenue: 12450,
  trendsData: {
    sites: { value: 12.5, positive: true },
    visitors: { value: 8.2, positive: true },
    revenue: { value: 15.3, positive: true },
    credits: { value: 5.1, positive: false },
  },
}

const mockChartData: ChartData[] = [
  { name: 'Jan', visitors: 400, sites: 2400, revenue: 2400 },
  { name: 'Fev', visitors: 300, sites: 1398, revenue: 2210 },
  { name: 'Mar', visitors: 200, sites: 9800, revenue: 2290 },
  { name: 'Abr', visitors: 278, sites: 3908, revenue: 2000 },
  { name: 'Mai', visitors: 189, sites: 4800, revenue: 2181 },
  { name: 'Jun', visitors: 239, sites: 3800, revenue: 2500 },
  { name: 'Jul', visitors: 349, sites: 4300, revenue: 2100 },
]

export function useDashboardData() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Simular chamada de API
        await new Promise((resolve) => setTimeout(resolve, 1000))

        setStats(mockStats)
        setChartData(mockChartData)
      } catch (err) {
        setError('Erro ao carregar dados do dashboard')
        console.error('Dashboard data fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  return {
    stats,
    chartData,
    loading,
    error,
    refresh: () => {
      setLoading(true)
      // Re-fetch data
    },
  }
}
