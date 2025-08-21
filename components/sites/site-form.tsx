'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Site, CreateSiteData, UpdateSiteData } from '@/lib/hooks/use-sites'
import { Globe, Loader2, Eye, Settings } from 'lucide-react'

interface SiteFormProps {
  site?: Site
  onSubmit: (data: CreateSiteData | UpdateSiteData) => Promise<void>
  onCancel: () => void
  loading?: boolean
  mode?: 'create' | 'edit'
}

const planOptions = [
  { value: 'basic', label: 'Básico', description: '1GB storage, 10GB bandwidth' },
  { value: 'pro', label: 'Pro', description: '5GB storage, 50GB bandwidth' },
  { value: 'enterprise', label: 'Enterprise', description: '10GB storage, 100GB bandwidth' },
]

const categoryOptions = [
  { value: 'e-commerce', label: 'E-commerce' },
  { value: 'blog', label: 'Blog' },
  { value: 'portfolio', label: 'Portfólio' },
  { value: 'corporate', label: 'Corporativo' },
  { value: 'landing-page', label: 'Landing Page' },
  { value: 'news', label: 'Notícias' },
]

const themeOptions = [
  { value: 'twentytwentyfour', label: 'Twenty Twenty-Four' },
  { value: 'astra', label: 'Astra' },
  { value: 'generatepress', label: 'GeneratePress' },
  { value: 'storefront', label: 'Storefront' },
  { value: 'kadence', label: 'Kadence' },
]

const statusOptions = [
  { value: 'active', label: 'Ativo', color: 'text-green-600' },
  { value: 'inactive', label: 'Inativo', color: 'text-red-600' },
  { value: 'maintenance', label: 'Manutenção', color: 'text-yellow-600' },
  { value: 'suspended', label: 'Suspenso', color: 'text-gray-600' },
]

export function SiteForm({ site, onSubmit, onCancel, loading = false, mode = 'create' }: SiteFormProps) {
  const [formData, setFormData] = useState({
    name: site?.name || '',
    domain: site?.domain || '',
    subdomain: site?.subdomain || '',
    plan: site?.plan || 'basic',
    category: site?.category || '',
    theme: site?.theme || 'twentytwentyfour',
    description: site?.description || '',
    ownerEmail: site?.ownerEmail || '',
    customDomain: site?.customDomain || '',
    status: site?.status || 'active',
    // Settings
    maintenanceMode: site?.settings?.maintenanceMode || false,
    seoEnabled: site?.settings?.seoEnabled || true,
    analyticsId: site?.settings?.analyticsId || '',
    cacheEnabled: site?.settings?.cacheEnabled || true,
    compressionEnabled: site?.settings?.compressionEnabled || true,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Nome do site é obrigatório'
    }

    if (!formData.domain.trim()) {
      newErrors.domain = 'Domínio é obrigatório'
    } else if (!formData.domain.includes('.')) {
      newErrors.domain = 'Formato de domínio inválido'
    }

    if (!formData.ownerEmail.trim()) {
      newErrors.ownerEmail = 'Email do proprietário é obrigatório'
    } else if (!/\S+@\S+\.\S+/.test(formData.ownerEmail)) {
      newErrors.ownerEmail = 'Email inválido'
    }

    if (!formData.category) {
      newErrors.category = 'Categoria é obrigatória'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      const submitData = mode === 'create' 
        ? {
            name: formData.name,
            domain: formData.domain,
            subdomain: formData.subdomain,
            plan: formData.plan as Site['plan'],
            category: formData.category,
            theme: formData.theme,
            description: formData.description,
            ownerEmail: formData.ownerEmail,
            customDomain: formData.customDomain,
          }
        : {
            id: site!.id,
            name: formData.name,
            domain: formData.domain,
            subdomain: formData.subdomain,
            plan: formData.plan as Site['plan'],
            category: formData.category,
            theme: formData.theme,
            description: formData.description,
            ownerEmail: formData.ownerEmail,
            customDomain: formData.customDomain,
            status: formData.status as Site['status'],
            settings: {
              maintenanceMode: formData.maintenanceMode,
              seoEnabled: formData.seoEnabled,
              analyticsId: formData.analyticsId,
              cacheEnabled: formData.cacheEnabled,
              compressionEnabled: formData.compressionEnabled,
            },
          }

      await onSubmit(submitData)
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }

  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Informações Básicas
          </CardTitle>
          <CardDescription>
            Configure os dados principais do site
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome do Site *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="Ex: Minha Loja Online"
                className={errors.name ? 'border-red-500' : ''}
              />
              {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="domain">Domínio *</Label>
              <Input
                id="domain"
                value={formData.domain}
                onChange={(e) => updateField('domain', e.target.value)}
                placeholder="exemplo.com"
                className={errors.domain ? 'border-red-500' : ''}
              />
              {errors.domain && <p className="text-sm text-red-500">{errors.domain}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="subdomain">Subdomínio</Label>
              <Input
                id="subdomain"
                value={formData.subdomain}
                onChange={(e) => updateField('subdomain', e.target.value)}
                placeholder="meusite"
              />
              <p className="text-xs text-muted-foreground">
                Será: {formData.subdomain || 'subdominio'}.wpaibuilder.com
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="customDomain">Domínio Personalizado</Label>
              <Input
                id="customDomain"
                value={formData.customDomain}
                onChange={(e) => updateField('customDomain', e.target.value)}
                placeholder="meudominio.com"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="ownerEmail">Email do Proprietário *</Label>
            <Input
              id="ownerEmail"
              type="email"
              value={formData.ownerEmail}
              onChange={(e) => updateField('ownerEmail', e.target.value)}
              placeholder="proprietario@email.com"
              className={errors.ownerEmail ? 'border-red-500' : ''}
            />
            {errors.ownerEmail && <p className="text-sm text-red-500">{errors.ownerEmail}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descrição</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Descreva o propósito do site..."
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Configuração
          </CardTitle>
          <CardDescription>
            Plano, categoria e configurações técnicas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="plan">Plano *</Label>
              <Select value={formData.plan} onValueChange={(value) => updateField('plan', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {planOptions.map((plan) => (
                    <SelectItem key={plan.value} value={plan.value}>
                      <div>
                        <div className="font-medium">{plan.label}</div>
                        <div className="text-xs text-muted-foreground">{plan.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Categoria *</Label>
              <Select value={formData.category} onValueChange={(value) => updateField('category', value)}>
                <SelectTrigger className={errors.category ? 'border-red-500' : ''}>
                  <SelectValue placeholder="Selecione a categoria" />
                </SelectTrigger>
                <SelectContent>
                  {categoryOptions.map((category) => (
                    <SelectItem key={category.value} value={category.value}>
                      {category.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.category && <p className="text-sm text-red-500">{errors.category}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="theme">Tema</Label>
              <Select value={formData.theme} onValueChange={(value) => updateField('theme', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {themeOptions.map((theme) => (
                    <SelectItem key={theme.value} value={theme.value}>
                      {theme.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {mode === 'edit' && (
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={formData.status} onValueChange={(value) => updateField('status', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((status) => (
                    <SelectItem key={status.value} value={status.value}>
                      <span className={status.color}>{status.label}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Settings */}
          {mode === 'edit' && (
            <div className="space-y-4">
              <div className="border-t pt-4">
                <h4 className="font-medium mb-3">Configurações do Site</h4>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="maintenanceMode"
                      checked={formData.maintenanceMode}
                      onCheckedChange={(checked) => updateField('maintenanceMode', !!checked)}
                    />
                    <Label htmlFor="maintenanceMode">Modo de manutenção</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="seoEnabled"
                      checked={formData.seoEnabled}
                      onCheckedChange={(checked) => updateField('seoEnabled', !!checked)}
                    />
                    <Label htmlFor="seoEnabled">SEO habilitado</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="cacheEnabled"
                      checked={formData.cacheEnabled}
                      onCheckedChange={(checked) => updateField('cacheEnabled', !!checked)}
                    />
                    <Label htmlFor="cacheEnabled">Cache habilitado</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="compressionEnabled"
                      checked={formData.compressionEnabled}
                      onCheckedChange={(checked) => updateField('compressionEnabled', !!checked)}
                    />
                    <Label htmlFor="compressionEnabled">Compressão habilitada</Label>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="analyticsId">Google Analytics ID</Label>
                    <Input
                      id="analyticsId"
                      value={formData.analyticsId}
                      onChange={(e) => updateField('analyticsId', e.target.value)}
                      placeholder="GA-XXXXXXXXX"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-3 justify-end">
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
          {mode === 'create' ? 'Criar Site' : 'Salvar Alterações'}
        </Button>
      </div>
    </form>
  )
}