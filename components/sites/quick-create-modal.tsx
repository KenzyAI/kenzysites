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
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CreateSiteData, Site } from '@/lib/hooks/use-sites'
import { Zap, Loader2, Sparkles, Globe, Rocket } from 'lucide-react'

interface QuickCreateModalProps {
  onCreateSite: (data: CreateSiteData) => Promise<void>
  loading?: boolean
  children?: React.ReactNode
}

// Quick templates with predefined configurations
const quickTemplates = [
  {
    id: 'blog',
    name: 'Blog Pessoal',
    description: 'Perfeito para bloggers e criadores de conteúdo',
    icon: '📝',
    category: 'blog',
    theme: 'twentytwentyfour',
    plan: 'basic' as Site['plan'],
    color: 'bg-blue-500',
    features: ['SEO otimizado', 'Comentários', 'Compartilhamento social'],
  },
  {
    id: 'ecommerce',
    name: 'Loja Online',
    description: 'Venda produtos online com facilidade',
    icon: '🛒',
    category: 'e-commerce',
    theme: 'storefront',
    plan: 'pro' as Site['plan'],
    color: 'bg-green-500',
    features: ['Carrinho de compras', 'Pagamento integrado', 'Gestão de estoque'],
  },
  {
    id: 'portfolio',
    name: 'Portfólio',
    description: 'Mostre seu trabalho de forma profissional',
    icon: '🎨',
    category: 'portfolio',
    theme: 'astra',
    plan: 'basic' as Site['plan'],
    color: 'bg-purple-500',
    features: ['Galeria de projetos', 'Formulário de contato', 'Design responsivo'],
  },
  {
    id: 'corporate',
    name: 'Site Corporativo',
    description: 'Presença digital profissional para sua empresa',
    icon: '🏢',
    category: 'corporate',
    theme: 'generatepress',
    plan: 'pro' as Site['plan'],
    color: 'bg-indigo-500',
    features: ['Múltiplas páginas', 'Formulários avançados', 'Integração CRM'],
  },
  {
    id: 'landing',
    name: 'Landing Page',
    description: 'Converta visitantes em clientes',
    icon: '🚀',
    category: 'landing-page',
    theme: 'kadence',
    plan: 'basic' as Site['plan'],
    color: 'bg-orange-500',
    features: ['Alta conversão', 'Integração analytics', 'A/B testing'],
  },
]

const planFeatures = {
  basic: {
    label: 'Plano Básico',
    price: 'R$ 29/mês',
    features: ['1GB armazenamento', '10GB tráfego', 'SSL grátis', '1 domínio'],
  },
  pro: {
    label: 'Plano Pro',
    price: 'R$ 79/mês', 
    features: ['5GB armazenamento', '50GB tráfego', 'SSL grátis', '5 domínios', 'Backup automático'],
  },
  enterprise: {
    label: 'Plano Enterprise',
    price: 'R$ 199/mês',
    features: ['10GB armazenamento', '100GB tráfego', 'SSL grátis', 'Domínios ilimitados', 'Suporte prioritário'],
  },
}

export function QuickCreateModal({ onCreateSite, loading = false, children }: QuickCreateModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<typeof quickTemplates[0] | null>(null)
  const [step, setStep] = useState<'template' | 'details' | 'review'>('template')
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    subdomain: '',
    ownerEmail: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const resetForm = () => {
    setStep('template')
    setSelectedTemplate(null)
    setFormData({ name: '', domain: '', subdomain: '', ownerEmail: '' })
    setErrors({})
  }

  const handleClose = () => {
    setIsOpen(false)
    setTimeout(resetForm, 300) // Reset after modal closes
  }

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
      newErrors.ownerEmail = 'Email é obrigatório'
    } else if (!/\S+@\S+\.\S+/.test(formData.ownerEmail)) {
      newErrors.ownerEmail = 'Email inválido'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSelectTemplate = (template: typeof quickTemplates[0]) => {
    setSelectedTemplate(template)
    setFormData(prev => ({
      ...prev,
      name: prev.name || `Meu ${template.name}`,
      subdomain: prev.subdomain || template.id,
    }))
    setStep('details')
  }

  const handleNext = () => {
    if (step === 'details') {
      if (validateForm()) {
        setStep('review')
      }
    }
  }

  const handleBack = () => {
    if (step === 'review') {
      setStep('details')
    } else if (step === 'details') {
      setStep('template')
    }
  }

  const handleCreate = async () => {
    if (!selectedTemplate || !validateForm()) return

    try {
      const createData: CreateSiteData = {
        name: formData.name,
        domain: formData.domain,
        subdomain: formData.subdomain,
        plan: selectedTemplate.plan,
        category: selectedTemplate.category,
        theme: selectedTemplate.theme,
        description: `Site criado usando o template "${selectedTemplate.name}"`,
        ownerEmail: formData.ownerEmail,
      }

      await onCreateSite(createData)
      handleClose()
    } catch (error) {
      console.error('Error creating site:', error)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button className="gap-2">
            <Zap className="h-4 w-4" />
            Criação Rápida
          </Button>
        )}
      </DialogTrigger>

      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Criação Rápida de Site
          </DialogTitle>
          <DialogDescription>
            {step === 'template' && 'Escolha um template otimizado para seu tipo de site'}
            {step === 'details' && 'Preencha os dados básicos do seu site'}
            {step === 'review' && 'Revise as configurações antes de criar'}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto">
          {/* Step 1: Template Selection */}
          {step === 'template' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {quickTemplates.map((template) => (
                  <Card
                    key={template.id}
                    className={`cursor-pointer transition-all hover:shadow-lg ${
                      selectedTemplate?.id === template.id
                        ? 'ring-2 ring-primary border-primary'
                        : 'hover:border-primary/50'
                    }`}
                    onClick={() => handleSelectTemplate(template)}
                  >
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        {/* Header */}
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${template.color} text-white text-lg`}>
                            {template.icon}
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold">{template.name}</h3>
                            <p className="text-sm text-muted-foreground">
                              {template.description}
                            </p>
                          </div>
                        </div>

                        {/* Plan Badge */}
                        <div className="flex justify-between items-center">
                          <Badge variant={template.plan === 'basic' ? 'secondary' : 'default'}>
                            {planFeatures[template.plan].label}
                          </Badge>
                          <span className="text-sm font-medium text-primary">
                            {planFeatures[template.plan].price}
                          </span>
                        </div>

                        {/* Features */}
                        <div className="space-y-1">
                          {template.features.slice(0, 3).map((feature, index) => (
                            <div key={index} className="flex items-center gap-2 text-xs text-muted-foreground">
                              <div className="h-1 w-1 rounded-full bg-primary" />
                              {feature}
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Site Details */}
          {step === 'details' && selectedTemplate && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                <div className={`p-2 rounded-lg ${selectedTemplate.color} text-white`}>
                  {selectedTemplate.icon}
                </div>
                <div>
                  <h3 className="font-medium">{selectedTemplate.name}</h3>
                  <p className="text-sm text-muted-foreground">{selectedTemplate.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome do Site *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
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
                      onChange={(e) => setFormData(prev => ({ ...prev, domain: e.target.value }))}
                      placeholder="meusite.com"
                      className={errors.domain ? 'border-red-500' : ''}
                    />
                    {errors.domain && <p className="text-sm text-red-500">{errors.domain}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="subdomain">Subdomínio</Label>
                    <Input
                      id="subdomain"
                      value={formData.subdomain}
                      onChange={(e) => setFormData(prev => ({ ...prev, subdomain: e.target.value }))}
                      placeholder="meusite"
                    />
                    <p className="text-xs text-muted-foreground">
                      Será: {formData.subdomain || 'subdominio'}.wpaibuilder.com
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="ownerEmail">Email do Proprietário *</Label>
                    <Input
                      id="ownerEmail"
                      type="email"
                      value={formData.ownerEmail}
                      onChange={(e) => setFormData(prev => ({ ...prev, ownerEmail: e.target.value }))}
                      placeholder="seu@email.com"
                      className={errors.ownerEmail ? 'border-red-500' : ''}
                    />
                    {errors.ownerEmail && <p className="text-sm text-red-500">{errors.ownerEmail}</p>}
                  </div>
                </div>

                <div className="space-y-4">
                  <Card>
                    <CardContent className="p-4">
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        Configurações do Template
                      </h4>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Categoria:</span>
                          <span className="capitalize">{selectedTemplate.category.replace('-', ' ')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Tema:</span>
                          <span>{selectedTemplate.theme}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Plano:</span>
                          <Badge variant={selectedTemplate.plan === 'basic' ? 'secondary' : 'default'}>
                            {planFeatures[selectedTemplate.plan].label}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-4">
                      <h4 className="font-medium mb-3">Recursos Incluídos</h4>
                      <div className="space-y-2">
                        {selectedTemplate.features.map((feature, index) => (
                          <div key={index} className="flex items-center gap-2 text-sm">
                            <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
                            {feature}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Review */}
          {step === 'review' && selectedTemplate && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full">
                  <Rocket className="h-4 w-4" />
                  <span className="font-medium">Quase pronto para decolar!</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                      <Globe className="h-5 w-5" />
                      Informações do Site
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm text-muted-foreground">Nome:</span>
                        <p className="font-medium">{formData.name}</p>
                      </div>
                      <div>
                        <span className="text-sm text-muted-foreground">Domínio principal:</span>
                        <p className="font-medium">{formData.domain}</p>
                      </div>
                      {formData.subdomain && (
                        <div>
                          <span className="text-sm text-muted-foreground">Subdomínio:</span>
                          <p className="font-medium">{formData.subdomain}.wpaibuilder.com</p>
                        </div>
                      )}
                      <div>
                        <span className="text-sm text-muted-foreground">Proprietário:</span>
                        <p className="font-medium">{formData.ownerEmail}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                      <div className={`p-1 rounded ${selectedTemplate.color} text-white text-xs`}>
                        {selectedTemplate.icon}
                      </div>
                      {selectedTemplate.name}
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm text-muted-foreground">Plano:</span>
                        <div className="flex items-center gap-2">
                          <Badge variant={selectedTemplate.plan === 'basic' ? 'secondary' : 'default'}>
                            {planFeatures[selectedTemplate.plan].label}
                          </Badge>
                          <span className="text-sm font-medium">
                            {planFeatures[selectedTemplate.plan].price}
                          </span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-muted-foreground">Recursos:</span>
                        <div className="mt-1 space-y-1">
                          {planFeatures[selectedTemplate.plan].features.slice(0, 3).map((feature, index) => (
                            <div key={index} className="flex items-center gap-2 text-sm">
                              <div className="h-1 w-1 rounded-full bg-green-500" />
                              {feature}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex gap-3">
                  <div className="text-blue-600">ℹ️</div>
                  <div className="text-sm">
                    <p className="font-medium text-blue-900 mb-1">O que acontece depois?</p>
                    <ul className="space-y-1 text-blue-700">
                      <li>• Seu site será criado automaticamente com o template selecionado</li>
                      <li>• Configurações de segurança SSL serão ativadas</li>
                      <li>• Você receberá um email com instruções de acesso</li>
                      <li>• O site estará online em poucos minutos</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          {step !== 'template' && (
            <Button variant="outline" onClick={handleBack} disabled={loading}>
              Voltar
            </Button>
          )}
          
          {step === 'template' && (
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancelar
            </Button>
          )}

          {step === 'details' && (
            <Button onClick={handleNext} disabled={!selectedTemplate}>
              Continuar
            </Button>
          )}

          {step === 'review' && (
            <Button onClick={handleCreate} disabled={loading}>
              {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Criar Site Agora
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}