'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'

export interface PaginationState {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export interface PaginationOptions {
  initialPage?: number
  initialPageSize?: number
  onPageChange?: (page: number) => void
  onPageSizeChange?: (pageSize: number) => void
}

export interface PaginatedData<T> {
  data: T[]
  pagination: PaginationState
  loading: boolean
  error?: string
}

export function usePagination({
  initialPage = 1,
  initialPageSize = 10,
  onPageChange,
  onPageSizeChange,
}: PaginationOptions = {}) {
  const [page, setPage] = useState(initialPage)
  const [pageSize, setPageSize] = useState(initialPageSize)
  const [total, setTotal] = useState(0)

  const totalPages = useMemo(() => Math.ceil(total / pageSize), [total, pageSize])

  const handlePageChange = useCallback(
    (newPage: number) => {
      if (newPage >= 1 && newPage <= totalPages) {
        setPage(newPage)
        onPageChange?.(newPage)
      }
    },
    [totalPages, onPageChange]
  )

  const handlePageSizeChange = useCallback(
    (newPageSize: number) => {
      setPageSize(newPageSize)
      setPage(1) // Reset to first page when page size changes
      onPageSizeChange?.(newPageSize)
    },
    [onPageSizeChange]
  )

  const handleSetTotal = useCallback((newTotal: number) => {
    setTotal(newTotal)
  }, [])

  const canPreviousPage = page > 1
  const canNextPage = page < totalPages

  const nextPage = useCallback(() => {
    handlePageChange(page + 1)
  }, [page, handlePageChange])

  const previousPage = useCallback(() => {
    handlePageChange(page - 1)
  }, [page, handlePageChange])

  const goToPage = useCallback(
    (pageNumber: number) => {
      handlePageChange(pageNumber)
    },
    [handlePageChange]
  )

  // Generate page numbers for pagination component
  const getPageNumbers = useCallback(() => {
    const pages: (number | 'ellipsis')[] = []
    const showEllipsis = totalPages > 7

    if (!showEllipsis) {
      // Show all pages if total is 7 or less
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Show ellipsis for large page counts
      if (page <= 4) {
        // Show first 5 pages, ellipsis, and last page
        for (let i = 1; i <= 5; i++) {
          pages.push(i)
        }
        if (totalPages > 6) {
          pages.push('ellipsis')
          pages.push(totalPages)
        }
      } else if (page >= totalPages - 3) {
        // Show first page, ellipsis, and last 5 pages
        pages.push(1)
        if (totalPages > 6) {
          pages.push('ellipsis')
        }
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        // Show first page, ellipsis, current page ±2, ellipsis, last page
        pages.push(1)
        pages.push('ellipsis')
        for (let i = page - 2; i <= page + 2; i++) {
          pages.push(i)
        }
        pages.push('ellipsis')
        pages.push(totalPages)
      }
    }

    return pages
  }, [page, totalPages])

  const pagination: PaginationState = {
    page,
    pageSize,
    total,
    totalPages,
  }

  return {
    // State
    page,
    pageSize,
    total,
    totalPages,
    pagination,

    // Actions
    setPage: handlePageChange,
    setPageSize: handlePageSizeChange,
    setTotal: handleSetTotal,
    nextPage,
    previousPage,
    goToPage,

    // Computed
    canPreviousPage,
    canNextPage,
    getPageNumbers,

    // Helpers
    getOffset: () => (page - 1) * pageSize,
    getLimit: () => pageSize,
  }
}
