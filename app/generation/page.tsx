"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/lib/use-toast';
import ProgressTracker from '@/app/components/generation/progress-tracker';
import { 
  Building2, 
  Phone, 
  Mail, 
  MapPin, 
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Loader2,
  Check,
  Globe,
  Palette,
  MessageCircle
} from 'lucide-react';

// Types
interface BusinessData {
  business_name: string;
  industry: string;
  business_type: string;
  description: string;
  phone: string;
  whatsapp: string;
  email: string;
  address: string;
  city: string;
  services: string[];
  target_audience: string;
  keywords: string[];
  primary_color: string;
  accept_pix: boolean;
  pix_key: string;
  cnpj: string;
}

interface WizardStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

const industries = [
  { value: 'restaurant', label: '🍽️ Restaurante', description: 'Delivery, cardápio online, reservas' },
  { value: 'healthcare', label: '🏥 Saúde', description: 'Agendamento, prontuário, telemedicina' },
  { value: 'ecommerce', label: '🛒 E-commerce', description: 'Loja virtual, carrinho, pagamentos' },
  { value: 'services', label: '💼 Serviços', description: 'Consultoria, portfólio, orçamentos' },
  { value: 'education', label: '🎓 Educação', description: 'Cursos, matrículas, portal do aluno' },
];

const steps: WizardStep[] = [
  {
    id: 'business',
    title: 'Informações do Negócio',
    description: 'Conte-nos sobre sua empresa',
    icon: <Building2 className="w-5 h-5" />
  },
  {
    id: 'contact',
    title: 'Contato',
    description: 'Como seus clientes podem te encontrar',
    icon: <Phone className="w-5 h-5" />
  },
  {
    id: 'customization',
    title: 'Personalização',
    description: 'Deixe seu site com a sua cara',
    icon: <Palette className="w-5 h-5" />
  },
  {
    id: 'features',
    title: 'Recursos',
    description: 'Escolha as funcionalidades',
    icon: <Sparkles className="w-5 h-5" />
  }
];

export default function GenerationWizard() {
  const router = useRouter();
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [businessData, setBusinessData] = useState<BusinessData>({
    business_name: '',
    industry: '',
    business_type: 'general',
    description: '',
    phone: '',
    whatsapp: '',
    email: '',
    address: '',
    city: 'São Paulo',
    services: [],
    target_audience: '',
    keywords: [],
    primary_color: '#0066FF',
    accept_pix: true,
    pix_key: '',
    cnpj: ''
  });

  const updateBusinessData = (field: keyof BusinessData, value: any) => {
    setBusinessData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const nextStep = () => {
    if (validateStep()) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const validateStep = (): boolean => {
    switch (steps[currentStep].id) {
      case 'business':
        if (!businessData.business_name || !businessData.industry) {
          toast({
            title: "Campos obrigatórios",
            description: "Por favor, preencha o nome do negócio e selecione uma indústria.",
            variant: "destructive"
          });
          return false;
        }
        return true;
      case 'contact':
        if (!businessData.phone && !businessData.whatsapp) {
          toast({
            title: "Contato necessário",
            description: "Por favor, adicione pelo menos um número de contato.",
            variant: "destructive"
          });
          return false;
        }
        return true;
      default:
        return true;
    }
  };

  const handleGenerate = async () => {
    if (!validateStep()) return;

    setIsGenerating(true);

    try {
      const response = await fetch('http://localhost:8000/api/v2/generation/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...businessData,
          generate_variations: true,
          variation_count: 3,
          use_ai: true
        })
      });

      if (!response.ok) {
        throw new Error('Falha na geração do site');
      }

      const data = await response.json();
      
      toast({
        title: "Site gerado com sucesso! 🎉",
        description: `Tempo de geração: ${data.processing_time || '2.5s'}`,
      });

      // Redirect to variation selection page with the generated data
      if (data.variations && data.variations.length > 0) {
        // Store variations in sessionStorage for the next page
        sessionStorage.setItem('generatedVariations', JSON.stringify(data));
        router.push('/generation/variations');
      }
    } catch (error) {
      console.error('Generation error:', error);
      toast({
        title: "Erro na geração",
        description: "Ocorreu um erro ao gerar o site. Tente novamente.",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const renderStepContent = () => {
    switch (steps[currentStep].id) {
      case 'business':
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="business_name">Nome do Negócio *</Label>
              <Input
                id="business_name"
                value={businessData.business_name}
                onChange={(e) => updateBusinessData('business_name', e.target.value)}
                placeholder="Ex: Restaurante Sabor Brasileiro"
                className="mt-2"
              />
            </div>

            <div>
              <Label htmlFor="industry">Tipo de Negócio *</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                {industries.map((ind) => (
                  <Card
                    key={ind.value}
                    className={`p-4 cursor-pointer transition-all ${
                      businessData.industry === ind.value 
                        ? 'border-primary ring-2 ring-primary/20' 
                        : 'hover:border-primary/50'
                    }`}
                    onClick={() => updateBusinessData('industry', ind.value)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">{ind.label.split(' ')[0]}</div>
                      <div className="flex-1">
                        <h3 className="font-semibold">{ind.label.split(' ')[1]}</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          {ind.description}
                        </p>
                      </div>
                      {businessData.industry === ind.value && (
                        <Check className="w-5 h-5 text-primary" />
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="description">Descrição do Negócio</Label>
              <Textarea
                id="description"
                value={businessData.description}
                onChange={(e) => updateBusinessData('description', e.target.value)}
                placeholder="Descreva seu negócio em algumas palavras..."
                className="mt-2"
                rows={4}
              />
            </div>

            <div>
              <Label htmlFor="services">Principais Serviços</Label>
              <Input
                id="services"
                value={businessData.services.join(', ')}
                onChange={(e) => updateBusinessData('services', e.target.value.split(',').map(s => s.trim()))}
                placeholder="Ex: Delivery, Reservas, Eventos"
                className="mt-2"
              />
              <p className="text-sm text-muted-foreground mt-1">
                Separe por vírgulas
              </p>
            </div>
          </div>
        );

      case 'contact':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="phone">Telefone</Label>
                <div className="relative mt-2">
                  <Phone className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="phone"
                    value={businessData.phone}
                    onChange={(e) => updateBusinessData('phone', e.target.value)}
                    placeholder="(11) 3333-3333"
                    className="pl-10"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="whatsapp">WhatsApp</Label>
                <div className="relative mt-2">
                  <MessageCircle className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="whatsapp"
                    value={businessData.whatsapp}
                    onChange={(e) => updateBusinessData('whatsapp', e.target.value)}
                    placeholder="(11) 99999-9999"
                    className="pl-10"
                  />
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="email">E-mail</Label>
              <div className="relative mt-2">
                <Mail className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  value={businessData.email}
                  onChange={(e) => updateBusinessData('email', e.target.value)}
                  placeholder="contato@exemplo.com.br"
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="address">Endereço</Label>
              <div className="relative mt-2">
                <MapPin className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                <Input
                  id="address"
                  value={businessData.address}
                  onChange={(e) => updateBusinessData('address', e.target.value)}
                  placeholder="Rua Exemplo, 123 - Bairro"
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="city">Cidade</Label>
              <Input
                id="city"
                value={businessData.city}
                onChange={(e) => updateBusinessData('city', e.target.value)}
                placeholder="São Paulo"
                className="mt-2"
              />
            </div>

            <div>
              <Label htmlFor="cnpj">CNPJ (opcional)</Label>
              <Input
                id="cnpj"
                value={businessData.cnpj}
                onChange={(e) => updateBusinessData('cnpj', e.target.value)}
                placeholder="00.000.000/0001-00"
                className="mt-2"
              />
            </div>
          </div>
        );

      case 'customization':
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="primary_color">Cor Principal</Label>
              <div className="flex items-center gap-4 mt-2">
                <Input
                  id="primary_color"
                  type="color"
                  value={businessData.primary_color}
                  onChange={(e) => updateBusinessData('primary_color', e.target.value)}
                  className="w-20 h-10"
                />
                <Input
                  value={businessData.primary_color}
                  onChange={(e) => updateBusinessData('primary_color', e.target.value)}
                  placeholder="#0066FF"
                  className="flex-1"
                />
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Esta cor será usada nos elementos principais do site
              </p>
            </div>

            <div>
              <Label htmlFor="target_audience">Público-alvo</Label>
              <Input
                id="target_audience"
                value={businessData.target_audience}
                onChange={(e) => updateBusinessData('target_audience', e.target.value)}
                placeholder="Ex: Famílias, jovens profissionais, empresas"
                className="mt-2"
              />
            </div>

            <div>
              <Label htmlFor="keywords">Palavras-chave para SEO</Label>
              <Input
                id="keywords"
                value={businessData.keywords.join(', ')}
                onChange={(e) => updateBusinessData('keywords', e.target.value.split(',').map(s => s.trim()))}
                placeholder="Ex: restaurante italiano, delivery, São Paulo"
                className="mt-2"
              />
              <p className="text-sm text-muted-foreground mt-1">
                Palavras que seus clientes usam para encontrar seu negócio
              </p>
            </div>
          </div>
        );

      case 'features':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <h3 className="font-semibold">Recursos Brasileiros</h3>
              
              <div className="space-y-3">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={businessData.accept_pix}
                    onChange={(e) => updateBusinessData('accept_pix', e.target.checked)}
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <div className="font-medium">Pagamento via PIX</div>
                    <div className="text-sm text-muted-foreground">
                      Aceite pagamentos instantâneos via PIX
                    </div>
                  </div>
                </label>

                {businessData.accept_pix && (
                  <div className="ml-7">
                    <Label htmlFor="pix_key">Chave PIX</Label>
                    <Input
                      id="pix_key"
                      value={businessData.pix_key}
                      onChange={(e) => updateBusinessData('pix_key', e.target.value)}
                      placeholder="seu@email.com ou CNPJ"
                      className="mt-2"
                    />
                  </div>
                )}

                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={!!businessData.whatsapp}
                    disabled
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <div className="font-medium">WhatsApp Business</div>
                    <div className="text-sm text-muted-foreground">
                      Botão flutuante do WhatsApp {businessData.whatsapp && '✓'}
                    </div>
                  </div>
                </label>

                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={true}
                    disabled
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <div className="font-medium">LGPD Compliance</div>
                    <div className="text-sm text-muted-foreground">
                      Banner de cookies e política de privacidade
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {businessData.industry === 'restaurant' && (
              <div className="space-y-4">
                <h3 className="font-semibold">Recursos Específicos</h3>
                <div className="space-y-3">
                  {['Delivery iFood/Uber Eats', 'Cardápio Online', 'Sistema de Reservas'].map((feature) => (
                    <label key={feature} className="flex items-center space-x-3 cursor-pointer">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 text-primary"
                      />
                      <span>{feature}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {businessData.industry === 'healthcare' && (
              <div className="space-y-4">
                <h3 className="font-semibold">Recursos Específicos</h3>
                <div className="space-y-3">
                  {['Agendamento Online', 'Portal do Paciente', 'Telemedicina'].map((feature) => (
                    <label key={feature} className="flex items-center space-x-3 cursor-pointer">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 text-primary"
                      />
                      <span>{feature}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {businessData.industry === 'ecommerce' && (
              <div className="space-y-4">
                <h3 className="font-semibold">Recursos Específicos</h3>
                <div className="space-y-3">
                  {['Carrinho de Compras', 'Integração Correios', 'Cupons de Desconto'].map((feature) => (
                    <label key={feature} className="flex items-center space-x-3 cursor-pointer">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 text-primary"
                      />
                      <span>{feature}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-secondary/5">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Crie seu Site com IA 🚀
          </h1>
          <p className="text-muted-foreground">
            Preencha as informações e gere um site profissional em segundos
          </p>
        </div>

        {/* Progress */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`flex items-center ${
                  index < steps.length - 1 ? 'flex-1' : ''
                }`}
              >
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    index <= currentStep
                      ? 'bg-primary border-primary text-primary-foreground'
                      : 'border-muted-foreground/30 text-muted-foreground'
                  }`}
                >
                  {index < currentStep ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-4 ${
                      index < currentStep ? 'bg-primary' : 'bg-muted-foreground/30'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-4">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`text-center ${
                  index <= currentStep ? 'text-foreground' : 'text-muted-foreground'
                }`}
              >
                <p className="text-sm font-medium hidden md:block">{step.title}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <Card className="max-w-4xl mx-auto">
          <div className="p-6 md:p-8">
            <div className="mb-6">
              <div className="flex items-center space-x-3 mb-2">
                {steps[currentStep].icon}
                <h2 className="text-2xl font-semibold">
                  {steps[currentStep].title}
                </h2>
              </div>
              <p className="text-muted-foreground">
                {steps[currentStep].description}
              </p>
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderStepContent()}
              </motion.div>
            </AnimatePresence>

            {/* Actions */}
            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 0}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Anterior
              </Button>

              {currentStep < steps.length - 1 ? (
                <Button onClick={nextStep}>
                  Próximo
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="min-w-[150px]"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Gerando...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Gerar Site
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* Help */}
        <div className="max-w-4xl mx-auto mt-8 text-center">
          <p className="text-sm text-muted-foreground">
            Precisa de ajuda? {' '}
            <a href="#" className="text-primary hover:underline">
              Fale com nosso suporte
            </a>
          </p>
        </div>
      </div>

      {/* Progress Tracker */}
      <ProgressTracker 
        isGenerating={isGenerating}
        businessInfo={{
          name: businessData.business_name,
          industry: businessData.industry,
          description: businessData.description
        }}
        onComplete={() => {
          // The handleGenerate function already handles completion
          // This is just for additional UI effects if needed
        }}
      />
    </div>
  );
}