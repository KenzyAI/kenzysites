"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { SiteCard } from "@/components/dashboard/site-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
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
  ChevronRight
} from "lucide-react"
import Link from "next/link"
import toast from "react-hot-toast"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/cn"

// Mock data expandido
const allSites = [
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
  {
    id: '4',
    name: 'Loja Virtual Express',
    url: 'https://loja-express.demo.com',
    status: 'active' as const,
    template: 'E-commerce Modern',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-14'),
    updatedAt: new Date('2025-01-14'),
    industry: 'ecommerce',
    variations: 6,
    pageSpeed: 91
  },
  {
    id: '5',
    name: 'Academia FitLife',
    url: 'https://fitlife.demo.com',
    status: 'paused' as const,
    template: 'Fitness Center',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-12'),
    updatedAt: new Date('2025-01-13'),
    industry: 'services',
    variations: 3,
    pageSpeed: 89
  },
  {
    id: '6',
    name: 'Escola Aprender Mais',
    url: 'https://aprender-mais.demo.com',
    status: 'active' as const,
    template: 'Education Institute',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-10'),
    updatedAt: new Date('2025-01-11'),
    industry: 'education',
    variations: 4,
    pageSpeed: 93
  },
  {
    id: '7',
    name: 'Pizzaria Bella Italia',
    url: 'https://bella-italia.demo.com',
    status: 'active' as const,
    template: 'Restaurant Pizza',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-08'),
    updatedAt: new Date('2025-01-08'),
    industry: 'restaurant',
    variations: 3,
    pageSpeed: 95
  },
  {
    id: '8',
    name: 'Consultoria Empresarial',
    url: 'https://consultoria.demo.com',
    status: 'building' as const,
    template: 'Business Consulting',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-06'),
    updatedAt: new Date('2025-01-07'),
    industry: 'services',
    variations: 5,
    pageSpeed: 90
  },
  {
    id: '9',
    name: 'Pet Shop Amigos',
    url: 'https://petshop-amigos.demo.com',
    status: 'error' as const,
    template: 'Pet Services',
    thumbnail: '/api/placeholder/400/300',
    createdAt: new Date('2025-01-05'),
    updatedAt: new Date('2025-01-05'),
    industry: 'ecommerce',
    variations: 2,
    pageSpeed: 85
  }
]

const industries = ['all', 'restaurant', 'healthcare', 'services', 'ecommerce', 'education']
const statuses = ['all', 'active', 'building', 'paused', 'error']

export default function MySitesPage() {
  const [sites, setSites] = useState(allSites)
  const [filteredSites, setFilteredSites] = useState(allSites)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'pageSpeed'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [currentPage, setCurrentPage] = useState(1)
  const [loading, setLoading] = useState(false)
  
  const itemsPerPage = 6
  const totalPages = Math.ceil(filteredSites.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const paginatedSites = filteredSites.slice(startIndex, startIndex + itemsPerPage)

  useEffect(() => {
    filterAndSortSites()
  }, [searchQuery, selectedIndustry, selectedStatus, sortBy, sortOrder])

  const filterAndSortSites = () => {
    let filtered = [...sites]

    // Filter by search
    if (searchQuery) {
      filtered = filtered.filter(site => 
        site.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        site.template.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Filter by industry
    if (selectedIndustry !== 'all') {
      filtered = filtered.filter(site => site.industry === selectedIndustry)
    }

    // Filter by status
    if (selectedStatus !== 'all') {
      filtered = filtered.filter(site => site.status === selectedStatus)
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'date':
          comparison = a.createdAt.getTime() - b.createdAt.getTime()
          break
        case 'pageSpeed':
          comparison = (a.pageSpeed || 0) - (b.pageSpeed || 0)
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    setFilteredSites(filtered)
    setCurrentPage(1)
  }

  const handleSiteAction = (action: string, siteId: string) => {
    toast.success(`${action} site ${siteId}`)
  }

  const handleBulkExport = () => {
    toast.success('Exportando todos os sites...')
  }

  const handleImport = () => {
    toast.success('Importar sites')
  }

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedIndustry('all')
    setSelectedStatus('all')
    setSortBy('date')
    setSortOrder('desc')
  }

  const statsCards = [
    { label: 'Total', value: sites.length, color: 'bg-blue-100 text-blue-800' },
    { label: 'Ativos', value: sites.filter(s => s.status === 'active').length, color: 'bg-green-100 text-green-800' },
    { label: 'Em construção', value: sites.filter(s => s.status === 'building').length, color: 'bg-yellow-100 text-yellow-800' },
    { label: 'Pausados', value: sites.filter(s => s.status === 'paused').length, color: 'bg-gray-100 text-gray-800' },
    { label: 'Com erro', value: sites.filter(s => s.status === 'error').length, color: 'bg-red-100 text-red-800' },
  ]

  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Meus Sites</h1>
          <p className="text-muted-foreground mt-1">
            Gerencie todos os seus sites WordPress criados
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={handleImport}>
            <Upload className="w-4 h-4 mr-2" />
            Importar
          </Button>
          <Button variant="outline" onClick={handleBulkExport}>
            <Download className="w-4 h-4 mr-2" />
            Exportar Todos
          </Button>
          <Button asChild>
            <Link href="/generation">
              <Plus className="w-4 h-4 mr-2" />
              Criar Novo Site
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {statsCards.map((stat) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card rounded-lg border p-4"
          >
            <p className="text-sm text-muted-foreground">{stat.label}</p>
            <p className="text-2xl font-bold mt-1">{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Filters Bar */}
      <div className="bg-card rounded-lg border p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Buscar por nome ou template..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <Select value={selectedIndustry} onValueChange={setSelectedIndustry}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Indústria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="restaurant">Restaurante</SelectItem>
                <SelectItem value="healthcare">Saúde</SelectItem>
                <SelectItem value="services">Serviços</SelectItem>
                <SelectItem value="ecommerce">E-commerce</SelectItem>
                <SelectItem value="education">Educação</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="active">Ativo</SelectItem>
                <SelectItem value="building">Em construção</SelectItem>
                <SelectItem value="paused">Pausado</SelectItem>
                <SelectItem value="error">Com erro</SelectItem>
              </SelectContent>
            </Select>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  {sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Ordenar por</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem
                  checked={sortBy === 'name'}
                  onCheckedChange={() => setSortBy('name')}
                >
                  Nome
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={sortBy === 'date'}
                  onCheckedChange={() => setSortBy('date')}
                >
                  Data de criação
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={sortBy === 'pageSpeed'}
                  onCheckedChange={() => setSortBy('pageSpeed')}
                >
                  PageSpeed
                </DropdownMenuCheckboxItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}>
                  {sortOrder === 'asc' ? 'Decrescente' : 'Crescente'}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <div className="flex rounded-md shadow-sm">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="icon"
                onClick={() => setViewMode('grid')}
                className="rounded-r-none"
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="icon"
                onClick={() => setViewMode('list')}
                className="rounded-l-none"
              >
                <List className="w-4 h-4" />
              </Button>
            </div>

            {(searchQuery || selectedIndustry !== 'all' || selectedStatus !== 'all') && (
              <Button variant="ghost" onClick={clearFilters}>
                Limpar filtros
              </Button>
            )}
          </div>
        </div>

        {/* Active filters badges */}
        {(searchQuery || selectedIndustry !== 'all' || selectedStatus !== 'all') && (
          <div className="flex flex-wrap gap-2 mt-3">
            {searchQuery && (
              <Badge variant="secondary">
                Busca: {searchQuery}
              </Badge>
            )}
            {selectedIndustry !== 'all' && (
              <Badge variant="secondary">
                Indústria: {selectedIndustry}
              </Badge>
            )}
            {selectedStatus !== 'all' && (
              <Badge variant="secondary">
                Status: {selectedStatus}
              </Badge>
            )}
            <Badge variant="outline">
              {filteredSites.length} resultado{filteredSites.length !== 1 ? 's' : ''}
            </Badge>
          </div>
        )}
      </div>

      {/* Sites Grid/List */}
      <AnimatePresence mode="wait">
        {viewMode === 'grid' ? (
          <motion.div
            key="grid"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
          >
            {paginatedSites.map((site) => (
              <SiteCard
                key={site.id}
                {...site}
                onEdit={() => handleSiteAction('Edit', site.id)}
                onClone={() => handleSiteAction('Clone', site.id)}
                onDelete={() => handleSiteAction('Delete', site.id)}
                onExport={() => handleSiteAction('Export', site.id)}
              />
            ))}
          </motion.div>
        ) : (
          <motion.div
            key="list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-3"
          >
            {paginatedSites.map((site) => (
              <div
                key={site.id}
                className="flex items-center justify-between p-4 bg-card rounded-lg border hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
                    <LayoutGrid className="w-8 h-8 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{site.name}</h3>
                    <p className="text-sm text-muted-foreground">{site.template}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge
                        className={cn(
                          site.status === 'active' && 'bg-green-100 text-green-800',
                          site.status === 'building' && 'bg-yellow-100 text-yellow-800',
                          site.status === 'paused' && 'bg-gray-100 text-gray-800',
                          site.status === 'error' && 'bg-red-100 text-red-800'
                        )}
                      >
                        {site.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {site.createdAt.toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSiteAction('Edit', site.id)}
                  >
                    Editar
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSiteAction('Clone', site.id)}
                  >
                    Clonar
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    asChild
                  >
                    <Link href={`/preview/${site.id}`}>
                      Ver
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Mostrando {startIndex + 1} a {Math.min(startIndex + itemsPerPage, filteredSites.length)} de {filteredSites.length} sites
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <Button
                key={page}
                variant={page === currentPage ? 'default' : 'outline'}
                size="icon"
                onClick={() => setCurrentPage(page)}
                className={cn(
                  page === currentPage && 'pointer-events-none'
                )}
              >
                {page}
              </Button>
            ))}
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Empty state */}
      {filteredSites.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12">
          <LayoutGrid className="w-12 h-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Nenhum site encontrado</h3>
          <p className="text-muted-foreground text-center max-w-sm">
            Tente ajustar os filtros ou criar seu primeiro site.
          </p>
          <Button asChild className="mt-4">
            <Link href="/generation">
              <Plus className="w-4 h-4 mr-2" />
              Criar Novo Site
            </Link>
          </Button>
        </div>
      )}
    </div>
  )
}