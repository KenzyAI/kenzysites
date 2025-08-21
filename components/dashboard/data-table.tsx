'use client'

import { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataPagination } from './data-pagination'
import { ExportDialog } from './export-dialog'
import { usePagination } from '@/lib/hooks/use-pagination'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Globe, Users, Calendar, MoreHorizontal, Eye, Edit, Trash2, Download } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface Site {
  id: number
  name: string
  domain: string
  status: 'active' | 'inactive' | 'maintenance'
  plan: 'basic' | 'pro' | 'enterprise'
  visitors: number
  createdAt: Date
  lastUpdate: Date
  owner: string
}

// Mock data generator
const generateMockSites = (count: number): Site[] => {
  const statuses: Site['status'][] = ['active', 'inactive', 'maintenance']
  const plans: Site['plan'][] = ['basic', 'pro', 'enterprise']
  const domains = ['exemplo.com', 'meusite.org', 'loja.net', 'blog.io', 'empresa.com.br']
  const owners = ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Lima']

  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Site ${i + 1}`,
    domain: `site-${i + 1}.${domains[i % domains.length]}`,
    status: statuses[Math.floor(Math.random() * statuses.length)],
    plan: plans[Math.floor(Math.random() * plans.length)],
    visitors: Math.floor(Math.random() * 10000) + 100,
    createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
    lastUpdate: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
    owner: owners[Math.floor(Math.random() * owners.length)],
  }))
}

const mockSites = generateMockSites(247) // Total mock data

// Simulate server-side pagination
const fetchSites = async (
  page: number,
  pageSize: number,
  delay = 500
): Promise<{ data: Site[]; total: number }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      const data = mockSites.slice(startIndex, endIndex)

      resolve({
        data,
        total: mockSites.length,
      })
    }, delay)
  })
}

const getStatusColor = (status: Site['status']) => {
  switch (status) {
    case 'active':
      return 'bg-green-500'
    case 'inactive':
      return 'bg-red-500'
    case 'maintenance':
      return 'bg-yellow-500'
    default:
      return 'bg-gray-500'
  }
}

const getStatusLabel = (status: Site['status']) => {
  switch (status) {
    case 'active':
      return 'Ativo'
    case 'inactive':
      return 'Inativo'
    case 'maintenance':
      return 'Manutenção'
    default:
      return status
  }
}

const getPlanLabel = (plan: Site['plan']) => {
  switch (plan) {
    case 'basic':
      return 'Básico'
    case 'pro':
      return 'Pro'
    case 'enterprise':
      return 'Enterprise'
    default:
      return plan
  }
}

export function DataTable() {
  const [sites, setSites] = useState<Site[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>()

  const { page, pageSize, total, totalPages, pagination, setPage, setPageSize, setTotal } =
    usePagination({
      initialPage: 1,
      initialPageSize: 10,
    })

  // Fetch data when page or pageSize changes
  useEffect(() => {
    const loadSites = async () => {
      setLoading(true)
      setError(undefined)

      try {
        const result = await fetchSites(page, pageSize)
        setSites(result.data)
        setTotal(result.total)
      } catch (err) {
        setError('Erro ao carregar sites')
        console.error('Failed to fetch sites:', err)
      } finally {
        setLoading(false)
      }
    }

    loadSites()
  }, [page, pageSize, setTotal])

  const handleAction = (action: string, site: Site) => {
    console.log(`${action} action for site:`, site.name)
    // In a real app, you would make API calls here
  }

  // Export configuration
  const exportColumns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Nome do Site' },
    { key: 'domain', label: 'Domínio' },
    { key: 'status', label: 'Status', format: (value: Site['status']) => getStatusLabel(value) },
    { key: 'plan', label: 'Plano', format: (value: Site['plan']) => getPlanLabel(value) },
    { key: 'visitors', label: 'Visitantes', format: (value: number) => value.toLocaleString() },
    { key: 'owner', label: 'Proprietário' },
    { key: 'createdAt', label: 'Data de Criação' },
    { key: 'lastUpdate', label: 'Última Atualização' },
  ]

  // Get all data for export (not just current page)
  const getAllSitesForExport = () => {
    return mockSites // Return all data for export
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-red-500">{error}</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Sites Gerenciados
          </CardTitle>
          
          <ExportDialog
            data={getAllSitesForExport()}
            availableColumns={exportColumns}
            defaultFilename={`sites-${format(new Date(), 'yyyy-MM-dd')}`}
          >
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </ExportDialog>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="text-left p-4 font-medium">Site</th>
                <th className="text-left p-4 font-medium">Status</th>
                <th className="text-left p-4 font-medium">Plano</th>
                <th className="text-left p-4 font-medium">Visitantes</th>
                <th className="text-left p-4 font-medium">Proprietário</th>
                <th className="text-left p-4 font-medium">Criado em</th>
                <th className="text-right p-4 font-medium">Ações</th>
              </tr>
            </thead>
            <tbody>
              {loading
                ? // Loading skeleton
                  Array.from({ length: pageSize }, (_, i) => (
                    <tr key={i} className="border-b">
                      <td className="p-4">
                        <div className="space-y-2">
                          <div className="h-4 bg-muted rounded animate-pulse w-32" />
                          <div className="h-3 bg-muted rounded animate-pulse w-48" />
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="h-6 bg-muted rounded animate-pulse w-16" />
                      </td>
                      <td className="p-4">
                        <div className="h-4 bg-muted rounded animate-pulse w-20" />
                      </td>
                      <td className="p-4">
                        <div className="h-4 bg-muted rounded animate-pulse w-16" />
                      </td>
                      <td className="p-4">
                        <div className="h-4 bg-muted rounded animate-pulse w-24" />
                      </td>
                      <td className="p-4">
                        <div className="h-4 bg-muted rounded animate-pulse w-20" />
                      </td>
                      <td className="p-4">
                        <div className="h-8 bg-muted rounded animate-pulse w-8 ml-auto" />
                      </td>
                    </tr>
                  ))
                : sites.map((site) => (
                    <tr key={site.id} className="border-b hover:bg-muted/25 transition-colors">
                      <td className="p-4">
                        <div>
                          <div className="font-medium">{site.name}</div>
                          <div className="text-sm text-muted-foreground">{site.domain}</div>
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge variant="secondary" className="flex items-center gap-1 w-fit">
                          <div className={`h-2 w-2 rounded-full ${getStatusColor(site.status)}`} />
                          {getStatusLabel(site.status)}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{getPlanLabel(site.plan)}</span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{site.visitors.toLocaleString()}</span>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{site.owner}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="h-4 w-4" />
                          {format(site.createdAt, 'dd/MM/yyyy', { locale: ptBR })}
                        </div>
                      </td>
                      <td className="p-4 text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleAction('view', site)}>
                              <Eye className="h-4 w-4 mr-2" />
                              Visualizar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleAction('edit', site)}>
                              <Edit className="h-4 w-4 mr-2" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => handleAction('delete', site)}
                              className="text-red-600"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Excluir
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>

        {/* Empty State */}
        {!loading && sites.length === 0 && (
          <div className="text-center py-12">
            <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium">Nenhum site encontrado</h3>
            <p className="text-muted-foreground">Comece criando seu primeiro site.</p>
          </div>
        )}

        {/* Pagination */}
        {!loading && sites.length > 0 && (
          <div className="p-4 border-t">
            <DataPagination
              pagination={pagination}
              onPageChange={setPage}
              onPageSizeChange={setPageSize}
              showPageSizeSelector={true}
              showPageJump={true}
              showInfo={true}
            />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
