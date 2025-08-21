'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import { Download, FileText, Table, Sheet, CheckCircle, AlertCircle } from 'lucide-react'
import { ExportData, ExportColumn, ExportManager, ExportProgress } from '@/lib/export-utils'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface ExportDialogProps {
  data: ExportData[]
  availableColumns: ExportColumn[]
  defaultFilename?: string
  children?: React.ReactNode
}

const exportManager = new ExportManager()

export function ExportDialog({
  data,
  availableColumns,
  defaultFilename = 'export',
  children,
}: ExportDialogProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [exportType, setExportType] = useState<'csv' | 'pdf' | 'excel'>('csv')
  const [filename, setFilename] = useState(defaultFilename)
  const [selectedColumns, setSelectedColumns] = useState<string[]>(
    availableColumns.map((col) => col.key)
  )
  const [includeHeaders, setIncludeHeaders] = useState(true)
  const [progress, setProgress] = useState<ExportProgress>({
    status: 'idle',
    progress: 0,
    message: '',
  })

  useEffect(() => {
    const unsubscribe = exportManager.subscribe(setProgress)
    return unsubscribe
  }, [])

  const handleColumnToggle = (columnKey: string, checked: boolean) => {
    if (checked) {
      setSelectedColumns([...selectedColumns, columnKey])
    } else {
      setSelectedColumns(selectedColumns.filter((key) => key !== columnKey))
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedColumns(availableColumns.map((col) => col.key))
    } else {
      setSelectedColumns([])
    }
  }

  const handleExport = async () => {
    if (selectedColumns.length === 0) {
      alert('Selecione ao menos uma coluna para exportar')
      return
    }

    const columnsToExport = availableColumns.filter((col) =>
      selectedColumns.includes(col.key)
    )

    const exportOptions = {
      filename: filename || defaultFilename,
      columns: columnsToExport,
      includeHeaders,
    }

    await exportManager.export(exportType, data, exportOptions)
  }

  const getExportIcon = (type: string) => {
    switch (type) {
      case 'csv':
        return <Table className="h-4 w-4" />
      case 'pdf':
        return <FileText className="h-4 w-4" />
      case 'excel':
        return <Sheet className="h-4 w-4" />
      default:
        return <Download className="h-4 w-4" />
    }
  }

  const isExporting = progress.status !== 'idle' && progress.status !== 'completed' && progress.status !== 'error'

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        )}
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Exportar Dados</DialogTitle>
          <DialogDescription>
            Configure as opções de exportação e baixe seus dados no formato desejado.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Export Type */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Formato do arquivo</label>
            <Select
              value={exportType}
              onValueChange={(value: 'csv' | 'pdf' | 'excel') => setExportType(value)}
              disabled={isExporting}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="csv">
                  <div className="flex items-center gap-2">
                    <Table className="h-4 w-4" />
                    CSV - Comma Separated Values
                  </div>
                </SelectItem>
                <SelectItem value="pdf">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    PDF - Portable Document Format
                  </div>
                </SelectItem>
                <SelectItem value="excel">
                  <div className="flex items-center gap-2">
                    <Sheet className="h-4 w-4" />
                    Excel - Microsoft Excel
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Filename */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Nome do arquivo</label>
            <Input
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="nome-do-arquivo"
              disabled={isExporting}
            />
            <p className="text-xs text-muted-foreground">
              Arquivo será salvo como: {filename}.{exportType}
            </p>
          </div>

          {/* Column Selection */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Colunas para exportar</label>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="select-all"
                  checked={selectedColumns.length === availableColumns.length}
                  onCheckedChange={handleSelectAll}
                  disabled={isExporting}
                />
                <label htmlFor="select-all" className="text-sm">
                  Selecionar todas
                </label>
              </div>
            </div>

            <div className="max-h-32 overflow-y-auto border rounded p-2 space-y-2">
              {availableColumns.map((column) => (
                <div key={column.key} className="flex items-center space-x-2">
                  <Checkbox
                    id={column.key}
                    checked={selectedColumns.includes(column.key)}
                    onCheckedChange={(checked) => handleColumnToggle(column.key, !!checked)}
                    disabled={isExporting}
                  />
                  <label htmlFor={column.key} className="text-sm">
                    {column.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Options */}
          {(exportType === 'csv' || exportType === 'excel') && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="include-headers"
                  checked={includeHeaders}
                  onCheckedChange={(checked) => setIncludeHeaders(!!checked)}
                  disabled={isExporting}
                />
                <label htmlFor="include-headers" className="text-sm">
                  Incluir cabeçalhos
                </label>
              </div>
            </div>
          )}

          {/* Progress */}
          {(isExporting || progress.status === 'completed' || progress.status === 'error') && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Progresso</span>
                {progress.status === 'completed' && (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                )}
                {progress.status === 'error' && (
                  <AlertCircle className="h-4 w-4 text-red-600" />
                )}
              </div>
              
              <Progress value={progress.progress} className="h-2" />
              
              <p className="text-xs text-muted-foreground">
                {progress.message}
                {progress.error && ` - ${progress.error}`}
              </p>
            </div>
          )}

          {/* Info */}
          <div className="bg-muted p-3 rounded text-xs text-muted-foreground">
            <p>📊 <strong>{data.length}</strong> registros serão exportados</p>
            <p>📅 Exportação gerada em: {format(new Date(), 'dd/MM/yyyy HH:mm', { locale: ptBR })}</p>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setIsOpen(false)}
            disabled={isExporting}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleExport}
            disabled={isExporting || selectedColumns.length === 0}
          >
            {isExporting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Exportando...
              </>
            ) : (
              <>
                {getExportIcon(exportType)}
                <span className="ml-2">Exportar {exportType.toUpperCase()}</span>
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}