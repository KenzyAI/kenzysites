'use client'

import { useState, useRef, useEffect } from 'react'
import { Search, FileText, Globe, Users, Zap, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/cn'

interface SearchResult {
  id: string
  title: string
  description: string
  type: 'site' | 'user' | 'page' | 'ai_content'
  url?: string
  metadata?: Record<string, unknown>
}

const mockResults: SearchResult[] = [
  {
    id: '1',
    title: 'E-commerce Fashion',
    description: 'Site de loja online com 1,234 visitantes este mês',
    type: 'site',
    url: '/dashboard/sites/1',
  },
  {
    id: '2',
    title: 'Maria Silva',
    description: 'maria.silva@email.com - Cliente Premium',
    type: 'user',
    url: '/dashboard/users/2',
  },
  {
    id: '3',
    title: 'Página Sobre Nós',
    description: 'Página institucional - E-commerce Fashion',
    type: 'page',
    url: '/dashboard/sites/1/pages/about',
  },
  {
    id: '4',
    title: '10 Dicas de SEO',
    description: 'Post gerado com IA - 1,450 visualizações',
    type: 'ai_content',
    url: '/dashboard/sites/1/posts/seo-tips',
  },
]

const getResultIcon = (type: SearchResult['type']) => {
  switch (type) {
    case 'site':
      return Globe
    case 'user':
      return Users
    case 'page':
      return FileText
    case 'ai_content':
      return Zap
    default:
      return FileText
  }
}

const getResultTypeLabel = (type: SearchResult['type']) => {
  switch (type) {
    case 'site':
      return 'Site'
    case 'user':
      return 'Usuário'
    case 'page':
      return 'Página'
    case 'ai_content':
      return 'Conteúdo IA'
    default:
      return 'Item'
  }
}

interface GlobalSearchProps {
  onResultSelect?: (result: SearchResult) => void
}

export function GlobalSearch({ onResultSelect }: GlobalSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const searchRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Simular busca
  const performSearch = async (searchQuery: string) => {
    if (searchQuery.trim().length < 2) {
      setResults([])
      return
    }

    setLoading(true)

    // Simular delay de API
    await new Promise((resolve) => setTimeout(resolve, 300))

    const filtered = mockResults.filter(
      (result) =>
        result.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.description.toLowerCase().includes(searchQuery.toLowerCase())
    )

    setResults(filtered)
    setLoading(false)
  }

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(query)
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex((prev) => (prev < results.length - 1 ? prev + 1 : prev))
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1))
          break
        case 'Enter':
          e.preventDefault()
          if (selectedIndex >= 0 && results[selectedIndex]) {
            handleResultSelect(results[selectedIndex])
          }
          break
        case 'Escape':
          setIsOpen(false)
          setSelectedIndex(-1)
          inputRef.current?.blur()
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, results, selectedIndex])

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSelectedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleResultSelect = (result: SearchResult) => {
    onResultSelect?.(result)
    setIsOpen(false)
    setQuery('')
    setSelectedIndex(-1)
    inputRef.current?.blur()
  }

  const handleClear = () => {
    setQuery('')
    setResults([])
    setSelectedIndex(-1)
    inputRef.current?.focus()
  }

  return (
    <div ref={searchRef} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
        <Input
          ref={inputRef}
          type="text"
          placeholder="Buscar sites, usuários, páginas..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
          className="pl-10 pr-10"
        />
        {query && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
            onClick={handleClear}
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>

      {/* Results Dropdown */}
      {isOpen && (query.length >= 2 || results.length > 0) && (
        <Card className="absolute top-full mt-1 w-full z-50 shadow-lg">
          <CardContent className="p-2">
            {loading && <div className="py-2 px-3 text-sm text-muted-foreground">Buscando...</div>}

            {!loading && results.length === 0 && query.length >= 2 && (
              <div className="py-2 px-3 text-sm text-muted-foreground">
                Nenhum resultado encontrado
              </div>
            )}

            {!loading && results.length > 0 && (
              <div className="space-y-1">
                {results.map((result, index) => {
                  const Icon = getResultIcon(result.type)
                  return (
                    <button
                      key={result.id}
                      className={cn(
                        'w-full text-left p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors',
                        selectedIndex === index && 'bg-accent text-accent-foreground'
                      )}
                      onClick={() => handleResultSelect(result)}
                      onMouseEnter={() => setSelectedIndex(index)}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className="h-4 w-4 mt-0.5 text-muted-foreground" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-sm truncate">{result.title}</span>
                            <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                              {getResultTypeLabel(result.type)}
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {result.description}
                          </p>
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}

            {!loading && results.length > 0 && (
              <div className="border-t mt-2 pt-2 px-1">
                <div className="text-xs text-muted-foreground">
                  Use ↑↓ para navegar, Enter para selecionar, Esc para fechar
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
