"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { SiteCard } from "@/components/dashboard/site-card"
import { SitePreview } from "@/components/sites/site-preview"
import { DataPagination } from "@/components/dashboard/data-pagination"
import { SiteForm } from "@/components/sites/site-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { 
  Search, 
  Filter, 
  Plus, 
  Grid, 
  List, 
  Download,
  Upload,
  SortAsc,
  SortDesc,
  LayoutGrid,
  ChevronLeft,
  ChevronRight,
  Power,
  Settings as SettingsIcon,
  Calendar,
  Users,
  Loader2,
  Zap,
  ExternalLink,
  Globe,
  Trash2,
  MoreHorizontal,
  Eye,
  Edit,
} from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { useToast } from '@/lib/use-toast'
import { useSites, Site, CreateSiteData, UpdateSiteData } from '@/lib/hooks/use-sites'
import Link from 'next/link'

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

export default function SitesPage() {
  const { sites, loading, createSite, updateSite, deleteSite, bulkUpdateStatus, bulkDelete, refetch } = useSites()
  const { toast } = useToast()
  
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [planFilter, setPlanFilter] = useState<string>('all')
  const [selectedSites, setSelectedSites] = useState<number[]>([])
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [editingSite, setEditingSite] = useState<Site | null>(null)
  const [actionLoading, setActionLoading] = useState(false)

  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const totalPages = Math.ceil(sites.length / pageSize)
  const pagination = {
    page,
    pageSize,
    total: sites.length,
    totalItems: sites.length,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
  }

  // Filter sites
  const filteredSites = sites.filter((site) => {
    const matchesSearch = !searchQuery || 
      site.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      site.domain.toLowerCase().includes(searchQuery.toLowerCase()) ||
      site.owner.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStatus = statusFilter === 'all' || site.status === statusFilter
    const matchesPlan = planFilter === 'all' || site.plan === planFilter

    return matchesSearch && matchesStatus && matchesPlan
  })

  // Paginate results
  const startIndex = (page - 1) * pageSize
  const endIndex = startIndex + pageSize
  const paginatedSites = filteredSites.slice(startIndex, endIndex)

  // Update total when filtered sites change - removed for simplicity

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedSites(paginatedSites.map(site => site.id))
    } else {
      setSelectedSites([])
    }
  }

  const handleSelectSite = (siteId: number, checked: boolean) => {
    if (checked) {
      setSelectedSites(prev => [...prev, siteId])
    } else {
      setSelectedSites(prev => prev.filter(id => id !== siteId))
    }
  }

  const handleCreateSite = async (data: CreateSiteData) => {
    try {
      setActionLoading(true)
      await createSite(data)
      setShowCreateDialog(false)
      toast({
        title: 'Site criado com sucesso!',
        description: `O site "${data.name}" foi criado e está sendo configurado.`,
      })
    } catch (error) {
      toast({
        title: 'Erro ao criar site',
        description: 'Ocorreu um erro inesperado. Tente novamente.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleEditSite = async (data: UpdateSiteData) => {
    try {
      setActionLoading(true)
      await updateSite(data)
      setEditingSite(null)
      toast({
        title: 'Site atualizado!',
        description: 'As alterações foram salvas com sucesso.',
      })
    } catch (error) {
      toast({
        title: 'Erro ao atualizar site',
        description: 'Ocorreu um erro inesperado. Tente novamente.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleDeleteSite = async (siteId: number) => {
    try {
      setActionLoading(true)
      await deleteSite(siteId)
      toast({
        title: 'Site excluído',
        description: 'O site foi excluído permanentemente.',
      })
    } catch (error) {
      toast({
        title: 'Erro ao excluir site',
        description: 'Ocorreu um erro inesperado. Tente novamente.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleBulkStatusUpdate = async (status: Site['status']) => {
    if (selectedSites.length === 0) return

    try {
      setActionLoading(true)
      await bulkUpdateStatus(selectedSites, status)
      setSelectedSites([])
      toast({
        title: 'Status atualizado',
        description: `${selectedSites.length} sites foram atualizados para "${statusLabels[status]}".`,
      })
    } catch (error) {
      toast({
        title: 'Erro ao atualizar status',
        description: 'Ocorreu um erro inesperado. Tente novamente.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleBulkDelete = async () => {
    if (selectedSites.length === 0) return

    try {
      setActionLoading(true)
      await bulkDelete(selectedSites)
      setSelectedSites([])
      toast({
        title: 'Sites excluídos',
        description: `${selectedSites.length} sites foram excluídos permanentemente.`,
      })
    } catch (error) {
      toast({
        title: 'Erro ao excluir sites',
        description: 'Ocorreu um erro inesperado. Tente novamente.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  // Export configuration
  const exportColumns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Nome do Site' },
    { key: 'domain', label: 'Domínio' },
    { key: 'status', label: 'Status', format: (value: Site['status']) => statusLabels[value] },
    { key: 'plan', label: 'Plano', format: (value: Site['plan']) => planLabels[value] },
    { key: 'visitors', label: 'Visitantes', format: (value: number) => value.toLocaleString() },
    { key: 'category', label: 'Categoria' },
    { key: 'owner', label: 'Proprietário' },
    { key: 'ownerEmail', label: 'Email do Proprietário' },
    { key: 'createdAt', label: 'Data de Criação' },
    { key: 'lastUpdate', label: 'Última Atualização' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sites</h1>
          <p className="text-muted-foreground">
            Gerencie todos os sites da sua plataforma
          </p>
        </div>
        
        <div className="flex gap-2">
          {/* <QuickCreateModal onCreateSite={handleCreateSite} loading={actionLoading}> */}
            <Button onClick={() => handleCreateSite}>
              <Zap className="h-4 w-4 mr-2" />
              Criação Rápida
            </Button>
          {/* </QuickCreateModal> */}

          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Novo Site
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Criar Novo Site</DialogTitle>
                <DialogDescription>
                  Configure um novo site WordPress com as informações abaixo
                </DialogDescription>
              </DialogHeader>
              {/* <SiteForm
                mode="create"
                onSubmit={handleCreateSite}
                onCancel={() => setShowCreateDialog(false)}
                loading={actionLoading}
              /> */}
              <div className="p-4">
                <p>Formulário de criação de site em desenvolvimento...</p>
                <Button onClick={() => setShowCreateDialog(false)} className="mt-4">
                  Fechar
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros e Busca
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Buscar por nome, domínio ou proprietário..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os Status</SelectItem>
                <SelectItem value="active">Ativo</SelectItem>
                <SelectItem value="inactive">Inativo</SelectItem>
                <SelectItem value="maintenance">Manutenção</SelectItem>
                <SelectItem value="suspended">Suspenso</SelectItem>
              </SelectContent>
            </Select>

            {/* Plan Filter */}
            <Select value={planFilter} onValueChange={setPlanFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os Planos</SelectItem>
                <SelectItem value="basic">Básico</SelectItem>
                <SelectItem value="pro">Pro</SelectItem>
                <SelectItem value="enterprise">Enterprise</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Bulk Actions */}
          {selectedSites.length > 0 && (
            <div className="flex items-center gap-2 p-3 bg-muted rounded-md">
              <span className="text-sm font-medium">
                {selectedSites.length} site(s) selecionado(s)
              </span>
              
              <div className="flex gap-2 ml-auto">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleBulkStatusUpdate('active')}
                  disabled={actionLoading}
                >
                  <Power className="h-3 w-3 mr-1" />
                  Ativar
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleBulkStatusUpdate('inactive')}
                  disabled={actionLoading}
                >
                  <Power className="h-3 w-3 mr-1" />
                  Desativar
                </Button>

                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" size="sm" disabled={actionLoading}>
                      <Trash2 className="h-3 w-3 mr-1" />
                      Excluir
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Excluir Sites</AlertDialogTitle>
                      <AlertDialogDescription>
                        Tem certeza que deseja excluir {selectedSites.length} site(s)? 
                        Esta ação não pode ser desfeita.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancelar</AlertDialogCancel>
                      <AlertDialogAction onClick={handleBulkDelete}>
                        Excluir
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sites Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Sites ({filteredSites.length})
            </CardTitle>
            
            {/* ExportDialog temporarily disabled
            <ExportDialog
              data={filteredSites}
              availableColumns={exportColumns}
              defaultFilename={`sites-${format(new Date(), 'yyyy-MM-dd')}`}
            >
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </ExportDialog> */}
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b bg-muted/50">
                <tr>
                  <th className="text-left p-4 w-12">
                    <Checkbox
                      checked={selectedSites.length === paginatedSites.length && paginatedSites.length > 0}
                      onCheckedChange={handleSelectAll}
                    />
                  </th>
                  <th className="text-left p-4 font-medium">Site</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Plano</th>
                  <th className="text-left p-4 font-medium">Categoria</th>
                  <th className="text-left p-4 font-medium">Visitantes</th>
                  <th className="text-left p-4 font-medium">Proprietário</th>
                  <th className="text-left p-4 font-medium">Criado em</th>
                  <th className="text-right p-4 font-medium">Ações</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  // Loading skeleton
                  Array.from({ length: pageSize }, (_, i) => (
                    <tr key={i} className="border-b">
                      <td className="p-4">
                        <div className="h-4 w-4 bg-muted rounded animate-pulse" />
                      </td>
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
                        <div className="h-4 bg-muted rounded animate-pulse w-24" />
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
                ) : paginatedSites.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="text-center py-12">
                      <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-medium">Nenhum site encontrado</h3>
                      <p className="text-muted-foreground">
                        {searchQuery || statusFilter !== 'all' || planFilter !== 'all'
                          ? 'Tente ajustar os filtros de busca.'
                          : 'Comece criando seu primeiro site.'}
                      </p>
                    </td>
                  </tr>
                ) : (
                  paginatedSites.map((site) => (
                    <tr key={site.id} className="border-b hover:bg-muted/25 transition-colors">
                      <td className="p-4">
                        <Checkbox
                          checked={selectedSites.includes(site.id)}
                          onCheckedChange={(checked) => handleSelectSite(site.id, !!checked)}
                        />
                      </td>
                      <td className="p-4">
                        <div>
                          <div className="font-medium">{site.name}</div>
                          <div className="text-sm text-muted-foreground">{site.domain}</div>
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge variant="secondary" className="flex items-center gap-1 w-fit">
                          <div className={`h-2 w-2 rounded-full ${statusColors[site.status]}`} />
                          {statusLabels[site.status]}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{planLabels[site.plan]}</span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm capitalize">{site.category.replace('-', ' ')}</span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{site.visitors.toLocaleString()}</span>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <div className="text-sm font-medium">{site.owner}</div>
                            <div className="text-xs text-muted-foreground">{site.ownerEmail}</div>
                          </div>
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
                            <DropdownMenuItem asChild>
                              <Link href={`/dashboard/sites/${site.id}`}>
                                <Eye className="h-4 w-4 mr-2" />
                                Ver Detalhes
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => setEditingSite(site)}>
                              <Edit className="h-4 w-4 mr-2" />
                              Editar
                            </DropdownMenuItem>
                            <SitePreview site={site}>
                              <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                                <Eye className="h-4 w-4 mr-2" />
                                Preview
                              </DropdownMenuItem>
                            </SitePreview>
                            
                            <DropdownMenuItem asChild>
                              <a href={`https://${site.domain}`} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="h-4 w-4 mr-2" />
                                Abrir Site
                              </a>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <DropdownMenuItem
                                  onSelect={(e) => e.preventDefault()}
                                  className="text-red-600"
                                >
                                  <Trash2 className="h-4 w-4 mr-2" />
                                  Excluir
                                </DropdownMenuItem>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Excluir Site</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Tem certeza que deseja excluir o site "{site.name}"? 
                                    Esta ação não pode ser desfeita e todos os dados serão perdidos.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                                  <AlertDialogAction 
                                    onClick={() => handleDeleteSite(site.id)}
                                    className="bg-red-600 hover:bg-red-700"
                                  >
                                    Excluir
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!loading && paginatedSites.length > 0 && (
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

      {/* Edit Dialog */}
      {editingSite && (
        <Dialog open={!!editingSite} onOpenChange={() => setEditingSite(null)}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Editar Site</DialogTitle>
              <DialogDescription>
                Atualize as configurações do site "{editingSite.name}"
              </DialogDescription>
            </DialogHeader>
            <SiteForm
              mode="edit"
              site={editingSite}
              onSubmit={handleEditSite}
              onCancel={() => setEditingSite(null)}
              loading={actionLoading}
            />
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}