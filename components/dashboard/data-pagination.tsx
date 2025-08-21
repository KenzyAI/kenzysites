'use client'

import { usePagination, PaginationState } from '@/lib/hooks/use-pagination'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useState } from 'react'

interface DataPaginationProps {
  pagination: PaginationState
  onPageChange: (page: number) => void
  onPageSizeChange: (pageSize: number) => void
  showPageSizeSelector?: boolean
  showPageJump?: boolean
  showInfo?: boolean
  className?: string
  pageSizeOptions?: number[]
}

const defaultPageSizeOptions = [5, 10, 20, 50, 100]

export function DataPagination({
  pagination,
  onPageChange,
  onPageSizeChange,
  showPageSizeSelector = true,
  showPageJump = true,
  showInfo = true,
  className,
  pageSizeOptions = defaultPageSizeOptions,
}: DataPaginationProps) {
  const [jumpToPage, setJumpToPage] = useState('')

  const { getPageNumbers } = usePagination({
    initialPage: pagination.page,
    initialPageSize: pagination.pageSize,
  })

  const pageNumbers = getPageNumbers()

  const handleJumpToPage = () => {
    const pageNum = parseInt(jumpToPage)
    if (pageNum >= 1 && pageNum <= pagination.totalPages) {
      onPageChange(pageNum)
      setJumpToPage('')
    }
  }

  const startItem = (pagination.page - 1) * pagination.pageSize + 1
  const endItem = Math.min(pagination.page * pagination.pageSize, pagination.total)

  if (pagination.totalPages <= 1) {
    return null
  }

  return (
    <div className={`flex flex-col gap-4 ${className}`}>
      {/* Main Pagination */}
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              href="#"
              onClick={(e) => {
                e.preventDefault()
                if (pagination.page > 1) {
                  onPageChange(pagination.page - 1)
                }
              }}
              className={pagination.page <= 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
            />
          </PaginationItem>

          {pageNumbers.map((pageNum, index) => (
            <PaginationItem key={index}>
              {pageNum === 'ellipsis' ? (
                <PaginationEllipsis />
              ) : (
                <PaginationLink
                  href="#"
                  onClick={(e) => {
                    e.preventDefault()
                    onPageChange(pageNum)
                  }}
                  isActive={pageNum === pagination.page}
                  className="cursor-pointer"
                >
                  {pageNum}
                </PaginationLink>
              )}
            </PaginationItem>
          ))}

          <PaginationItem>
            <PaginationNext
              href="#"
              onClick={(e) => {
                e.preventDefault()
                if (pagination.page < pagination.totalPages) {
                  onPageChange(pagination.page + 1)
                }
              }}
              className={
                pagination.page >= pagination.totalPages
                  ? 'pointer-events-none opacity-50'
                  : 'cursor-pointer'
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>

      {/* Additional Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-sm">
        {/* Info */}
        {showInfo && (
          <div className="text-muted-foreground">
            Mostrando {startItem} a {endItem} de {pagination.total} resultados
          </div>
        )}

        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          {/* Page Size Selector */}
          {showPageSizeSelector && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Itens por página:</span>
              <Select
                value={pagination.pageSize.toString()}
                onValueChange={(value) => onPageSizeChange(parseInt(value))}
              >
                <SelectTrigger className="w-[70px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {pageSizeOptions.map((size) => (
                    <SelectItem key={size} value={size.toString()}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Jump to Page */}
          {showPageJump && pagination.totalPages > 5 && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Ir para página:</span>
              <Input
                type="number"
                min="1"
                max={pagination.totalPages}
                value={jumpToPage}
                onChange={(e) => setJumpToPage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleJumpToPage()}
                className="w-[70px]"
                placeholder="1"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={handleJumpToPage}
                disabled={
                  !jumpToPage ||
                  parseInt(jumpToPage) < 1 ||
                  parseInt(jumpToPage) > pagination.totalPages
                }
              >
                Ir
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
