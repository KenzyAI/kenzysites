'use client'

import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export interface ExportData {
  [key: string]: any
}

export interface ExportColumn {
  key: string
  label: string
  format?: (value: any) => string
}

export interface ExportOptions {
  filename?: string
  columns?: ExportColumn[]
  includeHeaders?: boolean
  dateFormat?: string
}

// CSV Export functionality
export function exportToCSV(data: ExportData[], options: ExportOptions = {}) {
  const {
    filename = 'export',
    columns,
    includeHeaders = true,
    dateFormat = 'dd/MM/yyyy HH:mm',
  } = options

  if (data.length === 0) {
    throw new Error('No data to export')
  }

  // Determine columns
  const exportColumns = columns || Object.keys(data[0]).map((key) => ({ key, label: key }))

  // Format data
  const formatValue = (value: any, column: ExportColumn): string => {
    if (value === null || value === undefined) return ''

    if (column.format) {
      return column.format(value)
    }

    if (value instanceof Date) {
      return format(value, dateFormat, { locale: ptBR })
    }

    if (typeof value === 'boolean') {
      return value ? 'Sim' : 'Não'
    }

    if (typeof value === 'object') {
      return JSON.stringify(value)
    }

    return String(value)
  }

  // Escape CSV values
  const escapeCSV = (value: string): string => {
    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
      return `"${value.replace(/"/g, '""')}"`
    }
    return value
  }

  // Build CSV content
  let csvContent = ''

  // Add headers
  if (includeHeaders) {
    const headers = exportColumns.map((col) => escapeCSV(col.label))
    csvContent += headers.join(',') + '\n'
  }

  // Add data rows
  data.forEach((row) => {
    const values = exportColumns.map((col) => {
      const value = formatValue(row[col.key], col)
      return escapeCSV(value)
    })
    csvContent += values.join(',') + '\n'
  })

  // Create and download file
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')

  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `${filename}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}

// PDF Export functionality (using jsPDF)
export async function exportToPDF(
  data: ExportData[],
  options: ExportOptions & {
    title?: string
    orientation?: 'portrait' | 'landscape'
    pageSize?: 'a4' | 'letter'
    fontSize?: number
  } = {}
) {
  const {
    filename = 'export',
    columns,
    title = 'Relatório de Exportação',
    orientation = 'landscape',
    pageSize = 'a4',
    fontSize = 10,
    dateFormat = 'dd/MM/yyyy HH:mm',
  } = options

  if (data.length === 0) {
    throw new Error('No data to export')
  }

  // Dynamic import for client-side only
  const { default: jsPDF } = await import('jspdf')
  require('jspdf-autotable')

  // Determine columns
  const exportColumns = columns || Object.keys(data[0]).map((key) => ({ key, label: key }))

  // Format data
  const formatValue = (value: any, column: ExportColumn): string => {
    if (value === null || value === undefined) return ''

    if (column.format) {
      return column.format(value)
    }

    if (value instanceof Date) {
      return format(value, dateFormat, { locale: ptBR })
    }

    if (typeof value === 'boolean') {
      return value ? 'Sim' : 'Não'
    }

    if (typeof value === 'object') {
      return JSON.stringify(value)
    }

    return String(value)
  }

  // Create PDF document
  const doc = new jsPDF({
    orientation,
    unit: 'mm',
    format: pageSize,
  })

  // Add title
  doc.setFontSize(16)
  doc.text(title, 14, 20)

  // Add generation date
  doc.setFontSize(10)
  doc.text(`Gerado em: ${format(new Date(), 'dd/MM/yyyy HH:mm', { locale: ptBR })}`, 14, 30)

  // Prepare table data
  const headers = exportColumns.map((col) => col.label)
  const rows = data.map((row) =>
    exportColumns.map((col) => formatValue(row[col.key], col))
  )

  // Add table
  ;(doc as any).autoTable({
    head: [headers],
    body: rows,
    startY: 40,
    styles: {
      fontSize,
      cellPadding: 3,
    },
    headStyles: {
      fillColor: [59, 130, 246], // Blue color
      textColor: 255,
      fontSize: fontSize + 1,
    },
    alternateRowStyles: {
      fillColor: [249, 250, 251], // Light gray
    },
    margin: { top: 40, left: 14, right: 14 },
    tableWidth: 'auto',
    columnStyles: {
      // Auto-adjust column widths
    },
  })

  // Add page numbers
  const pageCount = doc.internal.getNumberOfPages()
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i)
    doc.setFontSize(8)
    doc.text(`Página ${i} de ${pageCount}`, doc.internal.pageSize.width - 30, doc.internal.pageSize.height - 10)
  }

  // Save the PDF
  doc.save(`${filename}.pdf`)
}

// Excel Export functionality (using SheetJS)
export async function exportToExcel(data: ExportData[], options: ExportOptions & {
  sheetName?: string
} = {}) {
  const {
    filename = 'export',
    columns,
    sheetName = 'Dados',
    dateFormat = 'dd/MM/yyyy HH:mm',
  } = options

  if (data.length === 0) {
    throw new Error('No data to export')
  }

  // Dynamic import for client-side only
  const XLSX = await import('xlsx')

  // Determine columns
  const exportColumns = columns || Object.keys(data[0]).map((key) => ({ key, label: key }))

  // Format data
  const formatValue = (value: any, column: ExportColumn): any => {
    if (value === null || value === undefined) return ''

    if (column.format) {
      return column.format(value)
    }

    if (value instanceof Date) {
      return format(value, dateFormat, { locale: ptBR })
    }

    if (typeof value === 'boolean') {
      return value ? 'Sim' : 'Não'
    }

    if (typeof value === 'object') {
      return JSON.stringify(value)
    }

    return value
  }

  // Prepare data for Excel
  const formattedData = data.map((row) => {
    const formattedRow: { [key: string]: any } = {}
    exportColumns.forEach((col) => {
      formattedRow[col.label] = formatValue(row[col.key], col)
    })
    return formattedRow
  })

  // Create workbook and worksheet
  const workbook = XLSX.utils.book_new()
  const worksheet = XLSX.utils.json_to_sheet(formattedData)

  // Set column widths
  const colWidths = exportColumns.map((col) => ({
    wch: Math.max(col.label.length, 15)
  }))
  worksheet['!cols'] = colWidths

  // Add worksheet to workbook
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

  // Save the file
  XLSX.writeFile(workbook, `${filename}.xlsx`)
}

// Export status tracking
export interface ExportProgress {
  status: 'idle' | 'preparing' | 'generating' | 'downloading' | 'completed' | 'error'
  progress: number
  message: string
  error?: string
}

export class ExportManager {
  private listeners: ((progress: ExportProgress) => void)[] = []

  subscribe(callback: (progress: ExportProgress) => void) {
    this.listeners.push(callback)
    return () => {
      const index = this.listeners.indexOf(callback)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  private notify(progress: ExportProgress) {
    this.listeners.forEach((callback) => callback(progress))
  }

  async export(
    type: 'csv' | 'pdf' | 'excel',
    data: ExportData[],
    options: ExportOptions = {}
  ) {
    try {
      this.notify({
        status: 'preparing',
        progress: 0,
        message: 'Preparando dados para exportação...',
      })

      await new Promise((resolve) => setTimeout(resolve, 500)) // Simulate preparation

      this.notify({
        status: 'generating',
        progress: 50,
        message: 'Gerando arquivo...',
      })

      switch (type) {
        case 'csv':
          exportToCSV(data, options)
          break
        case 'pdf':
          await exportToPDF(data, options)
          break
        case 'excel':
          await exportToExcel(data, options)
          break
        default:
          throw new Error(`Unsupported export type: ${type}`)
      }

      this.notify({
        status: 'downloading',
        progress: 90,
        message: 'Iniciando download...',
      })

      await new Promise((resolve) => setTimeout(resolve, 500))

      this.notify({
        status: 'completed',
        progress: 100,
        message: 'Export concluído com sucesso!',
      })
    } catch (error) {
      this.notify({
        status: 'error',
        progress: 0,
        message: 'Erro durante a exportação',
        error: error instanceof Error ? error.message : 'Unknown error',
      })
    }
  }
}