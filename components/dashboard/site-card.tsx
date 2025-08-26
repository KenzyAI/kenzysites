"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/cn"
import Image from "next/image"
import Link from "next/link"
import { 
  MoreVertical, 
  Eye, 
  Edit, 
  Copy, 
  Download, 
  Trash,
  ExternalLink,
  Globe,
  Calendar,
  Layers
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

interface SiteCardProps {
  id: string
  name: string
  url?: string
  status: 'active' | 'building' | 'paused' | 'error'
  template: string
  thumbnail?: string
  createdAt: Date
  updatedAt: Date
  industry?: string
  variations?: number
  pageSpeed?: number
  onEdit?: () => void
  onClone?: () => void
  onDelete?: () => void
  onExport?: () => void
  className?: string
}

export function SiteCard({
  id,
  name,
  url,
  status,
  template,
  thumbnail,
  createdAt,
  updatedAt,
  industry,
  variations = 0,
  pageSpeed,
  onEdit,
  onClone,
  onDelete,
  onExport,
  className
}: SiteCardProps) {
  const getStatusBadge = () => {
    const statusConfig = {
      active: { label: 'Ativo', className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' },
      building: { label: 'Em construção', className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' },
      paused: { label: 'Pausado', className: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300' },
      error: { label: 'Erro', className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' }
    }
    
    const config = statusConfig[status]
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const getPageSpeedColor = (score?: number) => {
    if (!score) return 'text-gray-500'
    if (score >= 90) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
      className={cn(
        "group relative rounded-xl border bg-card overflow-hidden hover:shadow-xl transition-all duration-300",
        className
      )}
    >
      {/* Thumbnail */}
      <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        {thumbnail ? (
          <Image
            src={thumbnail}
            alt={name}
            fill
            className="object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <Globe className="w-16 h-16 text-gray-400" />
          </div>
        )}
        
        {/* Overlay with actions on hover */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            className="opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0"
            asChild
          >
            <Link href={`/preview/${id}`}>
              <Eye className="w-4 h-4 mr-1" />
              Preview
            </Link>
          </Button>
          {url && (
            <Button
              size="sm"
              variant="secondary"
              className="opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 delay-75"
              asChild
            >
              <a href={url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4 mr-1" />
                Visitar
              </a>
            </Button>
          )}
        </div>

        {/* Status badge */}
        <div className="absolute top-3 left-3">
          {getStatusBadge()}
        </div>

        {/* Actions menu */}
        <div className="absolute top-3 right-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="secondary"
                size="icon"
                className="h-8 w-8 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm"
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Ações</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onEdit}>
                <Edit className="mr-2 h-4 w-4" />
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onClone}>
                <Copy className="mr-2 h-4 w-4" />
                Clonar
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onExport}>
                <Download className="mr-2 h-4 w-4" />
                Exportar
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onDelete} className="text-red-600">
                <Trash className="mr-2 h-4 w-4" />
                Deletar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 line-clamp-1">{name}</h3>
        
        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4" />
            <span>{template}</span>
            {industry && (
              <>
                <span className="text-xs">•</span>
                <span className="capitalize">{industry}</span>
              </>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <span>Criado {format(new Date(createdAt), 'dd MMM yyyy', { locale: ptBR })}</span>
          </div>
        </div>

        {/* Metrics */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t">
          <div className="flex items-center gap-4">
            {variations > 0 && (
              <div className="text-sm">
                <span className="font-medium">{variations}</span>
                <span className="text-muted-foreground ml-1">variações</span>
              </div>
            )}
            {pageSpeed && (
              <div className="text-sm">
                <span className={cn("font-medium", getPageSpeedColor(pageSpeed))}>
                  {pageSpeed}
                </span>
                <span className="text-muted-foreground ml-1">PageSpeed</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}