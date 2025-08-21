'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Filter, X, Calendar as CalendarIcon, Search, SlidersHorizontal } from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { cn } from '@/lib/cn'

export interface FilterValue {
  id: string
  label: string
  value: string | number | Date
  type: 'text' | 'select' | 'date' | 'number'
}

export interface FilterDefinition {
  id: string
  label: string
  type: 'text' | 'select' | 'date' | 'number' | 'daterange'
  options?: Array<{ label: string; value: string }>
  placeholder?: string
}

interface AdvancedFiltersProps {
  filters?: FilterDefinition[]
  values?: FilterValue[]
  onFiltersChange?: (filters: FilterValue[]) => void
  onSearch?: (query: string) => void
  onClear?: () => void
  className?: string
}

const defaultFilters: FilterDefinition[] = [
  {
    id: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Ativo', value: 'active' },
      { label: 'Inativo', value: 'inactive' },
      { label: 'Suspenso', value: 'suspended' },
      { label: 'Em Manutenção', value: 'maintenance' },
    ],
  },
  {
    id: 'plan',
    label: 'Plano',
    type: 'select',
    options: [
      { label: 'Básico', value: 'basic' },
      { label: 'Pro', value: 'pro' },
      { label: 'Enterprise', value: 'enterprise' },
    ],
  },
  {
    id: 'created_date',
    label: 'Data de Criação',
    type: 'daterange',
  },
  {
    id: 'min_visitors',
    label: 'Visitantes Mínimos',
    type: 'number',
    placeholder: '0',
  },
]

export function AdvancedFilters({
  filters = defaultFilters,
  values = [],
  onFiltersChange,
  onSearch,
  onClear,
  className,
}: AdvancedFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedFilters, setSelectedFilters] = useState<FilterValue[]>(values)
  const [dateFrom, setDateFrom] = useState<Date>()
  const [dateTo, setDateTo] = useState<Date>()

  const handleFilterAdd = (filterId: string, value: string | number | Date) => {
    const filterDef = filters.find((f) => f.id === filterId)
    if (!filterDef) return

    const newFilter: FilterValue = {
      id: filterId,
      label: filterDef.label,
      value,
      type: filterDef.type as FilterValue['type'],
    }

    const updatedFilters = [...selectedFilters.filter((f) => f.id !== filterId), newFilter]
    setSelectedFilters(updatedFilters)
    onFiltersChange?.(updatedFilters)
  }

  const handleFilterRemove = (filterId: string) => {
    const updatedFilters = selectedFilters.filter((f) => f.id !== filterId)
    setSelectedFilters(updatedFilters)
    onFiltersChange?.(updatedFilters)
  }

  const handleClearAll = () => {
    setSelectedFilters([])
    setSearchQuery('')
    setDateFrom(undefined)
    setDateTo(undefined)
    onClear?.()
    onFiltersChange?.([])
  }

  const handleSearch = () => {
    onSearch?.(searchQuery)
  }

  const renderFilterControl = (filter: FilterDefinition) => {
    switch (filter.type) {
      case 'select':
        return (
          <Select
            onValueChange={(value) => handleFilterAdd(filter.id, value)}
            value={selectedFilters.find((f) => f.id === filter.id)?.value as string}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder={`Selecionar ${filter.label}`} />
            </SelectTrigger>
            <SelectContent>
              {filter.options?.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )

      case 'number':
        return (
          <Input
            type="number"
            placeholder={filter.placeholder}
            className="w-[180px]"
            value={selectedFilters.find((f) => f.id === filter.id)?.value as string}
            onChange={(e) => {
              const value = parseInt(e.target.value)
              if (!isNaN(value)) {
                handleFilterAdd(filter.id, value)
              }
            }}
          />
        )

      case 'text':
        return (
          <Input
            placeholder={filter.placeholder}
            className="w-[180px]"
            value={selectedFilters.find((f) => f.id === filter.id)?.value as string}
            onChange={(e) => handleFilterAdd(filter.id, e.target.value)}
          />
        )

      case 'daterange':
        return (
          <div className="flex items-center gap-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    'w-[140px] justify-start text-left font-normal',
                    !dateFrom && 'text-muted-foreground'
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateFrom ? format(dateFrom, 'dd/MM/yyyy', { locale: ptBR }) : 'Data inicial'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={dateFrom}
                  onSelect={(date) => {
                    setDateFrom(date)
                    if (date) {
                      handleFilterAdd(`${filter.id}_from`, date)
                    }
                  }}
                  initialFocus
                />
              </PopoverContent>
            </Popover>

            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    'w-[140px] justify-start text-left font-normal',
                    !dateTo && 'text-muted-foreground'
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateTo ? format(dateTo, 'dd/MM/yyyy', { locale: ptBR }) : 'Data final'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={dateTo}
                  onSelect={(date) => {
                    setDateTo(date)
                    if (date) {
                      handleFilterAdd(`${filter.id}_to`, date)
                    }
                  }}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros Avançados
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={() => setIsExpanded(!isExpanded)}>
            <SlidersHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Search Bar */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Buscar por nome, email, domínio..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10"
            />
          </div>
          <Button onClick={handleSearch}>Buscar</Button>
        </div>

        {/* Active Filters */}
        {selectedFilters.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedFilters.map((filter) => (
              <Badge
                key={`${filter.id}-${filter.value}`}
                variant="secondary"
                className="flex items-center gap-1"
              >
                {filter.label}:{' '}
                {filter.value instanceof Date
                  ? format(filter.value, 'dd/MM/yyyy', { locale: ptBR })
                  : String(filter.value)}
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-auto p-0 ml-1"
                  onClick={() => handleFilterRemove(filter.id)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </Badge>
            ))}
            <Button variant="ghost" size="sm" onClick={handleClearAll} className="h-6 px-2">
              Limpar todos
            </Button>
          </div>
        )}

        {/* Filter Controls */}
        {isExpanded && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filters.map((filter) => (
                <div key={filter.id} className="space-y-2">
                  <label className="text-sm font-medium">{filter.label}</label>
                  {renderFilterControl(filter)}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
