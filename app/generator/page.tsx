"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Sparkles, Check, ArrowRight, Eye, Download, Edit } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface SiteData {
  businessName: string;
  businessType: string;
  industry: string;
  description: string;
  email: string;
  phone: string;
  address: string;
  whatsapp: string;
}

interface Variation {
  id: string;
  name: string;
  preview_url: string;
  style: {
    spacing: string;
    corners: string;
    shadows: string;
  };
}

export default function SiteGeneratorPage() {
  const [step, setStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [siteData, setSiteData] = useState<SiteData>({
    businessName: '',
    businessType: '',
    industry: '',
    description: '',
    email: '',
    phone: '',
    address: '',
    whatsapp: ''
  });
  const [variations, setVariations] = useState<Variation[]>([]);
  const [selectedVariation, setSelectedVariation] = useState<string>('');
  const [generatedSite, setGeneratedSite] = useState<any>(null);

  const industries = [
    { value: 'restaurante', label: 'Restaurante / Alimentação' },
    { value: 'saude', label: 'Saúde / Clínica' },
    { value: 'educacao', label: 'Educação / Escola' },
    { value: 'servicos', label: 'Serviços Profissionais' },
    { value: 'comercio', label: 'Comércio / E-commerce' },
    { value: 'fitness', label: 'Fitness / Academia' },
    { value: 'beleza', label: 'Beleza / Estética' },
    { value: 'tecnologia', label: 'Tecnologia / Software' },
    { value: 'consultoria', label: 'Consultoria' },
    { value: 'imobiliaria', label: 'Imobiliária' }
  ];

  const handleGenerateSite = async () => {
    setIsGenerating(true);
    setProgress(0);
    
    // Simular etapas de geração
    const steps = [
      { progress: 10, message: '🔍 Analisando seu negócio...' },
      { progress: 20, message: '🤖 Gerando conteúdo com IA...' },
      { progress: 35, message: '🎨 Selecionando templates ideais...' },
      { progress: 50, message: '📐 Criando 3 variações de layout...' },
      { progress: 65, message: '🖼️ Otimizando imagens...' },
      { progress: 80, message: '⚡ Configurando WordPress...' },
      { progress: 95, message: '✨ Finalizando site...' },
      { progress: 100, message: '✅ Site pronto!' }
    ];

    for (const step of steps) {
      setProgress(step.progress);
      setProgressMessage(step.message);
      await new Promise(resolve => setTimeout(resolve, 800));
    }

    // Gerar variações mockadas
    const mockVariations: Variation[] = [
      {
        id: 'variation_1',
        name: 'Layout Moderno',
        preview_url: 'http://localhost:8080/preview/1',
        style: { spacing: 'normal', corners: 'rounded', shadows: 'subtle' }
      },
      {
        id: 'variation_2',
        name: 'Layout Elegante',
        preview_url: 'http://localhost:8080/preview/2',
        style: { spacing: 'relaxed', corners: 'soft', shadows: 'strong' }
      },
      {
        id: 'variation_3',
        name: 'Layout Minimalista',
        preview_url: 'http://localhost:8080/preview/3',
        style: { spacing: 'compact', corners: 'sharp', shadows: 'none' }
      }
    ];

    setVariations(mockVariations);
    setIsGenerating(false);
    setStep(3);
  };

  const handleSelectVariation = (variationId: string) => {
    setSelectedVariation(variationId);
  };

  const handleConfirmSite = async () => {
    setIsGenerating(true);
    setProgressMessage('🚀 Criando seu site WordPress...');
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setGeneratedSite({
      url: `http://localhost:8080/${siteData.businessName.toLowerCase().replace(/\s+/g, '-')}`,
      admin_url: `http://localhost:8080/${siteData.businessName.toLowerCase().replace(/\s+/g, '-')}/wp-admin`,
      username: 'admin',
      password: 'TempPass123!',
      processing_time: '47 segundos'
    });
    
    setIsGenerating(false);
    setStep(4);
  };

  return (
    <div className="container max-w-6xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center justify-center gap-2">
          <Sparkles className="h-8 w-8 text-blue-600" />
          Gerador de Sites com IA
        </h1>
        <p className="text-lg text-muted-foreground">
          Crie um site WordPress completo em 60 segundos
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex justify-center mb-8">
        <div className="flex items-center space-x-4">
          <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              {step > 1 ? <Check className="h-4 w-4" /> : '1'}
            </div>
            <span className="ml-2 font-medium">Informações</span>
          </div>
          <ArrowRight className="h-4 w-4 text-gray-400" />
          <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              {step > 2 ? <Check className="h-4 w-4" /> : '2'}
            </div>
            <span className="ml-2 font-medium">Geração</span>
          </div>
          <ArrowRight className="h-4 w-4 text-gray-400" />
          <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              {step > 3 ? <Check className="h-4 w-4" /> : '3'}
            </div>
            <span className="ml-2 font-medium">Escolha</span>
          </div>
          <ArrowRight className="h-4 w-4 text-gray-400" />
          <div className={`flex items-center ${step >= 4 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 4 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              {step > 4 ? <Check className="h-4 w-4" /> : '4'}
            </div>
            <span className="ml-2 font-medium">Pronto!</span>
          </div>
        </div>
      </div>

      {/* Step 1: Informações */}
      {step === 1 && (
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Informações do Negócio</CardTitle>
            <CardDescription>
              Preencha os dados para personalizar seu site
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="businessName">Nome do Negócio *</Label>
                <Input
                  id="businessName"
                  placeholder="Ex: Restaurante Sabor Brasileiro"
                  value={siteData.businessName}
                  onChange={(e) => setSiteData({...siteData, businessName: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="industry">Tipo de Negócio *</Label>
                <Select
                  value={siteData.industry}
                  onValueChange={(value) => setSiteData({...siteData, industry: value})}
                >
                  <SelectTrigger id="industry">
                    <SelectValue placeholder="Selecione..." />
                  </SelectTrigger>
                  <SelectContent>
                    {industries.map(ind => (
                      <SelectItem key={ind.value} value={ind.value}>
                        {ind.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descrição do Negócio *</Label>
              <Textarea
                id="description"
                placeholder="Descreva seu negócio, produtos ou serviços principais..."
                value={siteData.description}
                onChange={(e) => setSiteData({...siteData, description: e.target.value})}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="contato@exemplo.com"
                  value={siteData.email}
                  onChange={(e) => setSiteData({...siteData, email: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Telefone</Label>
                <Input
                  id="phone"
                  placeholder="(11) 98765-4321"
                  value={siteData.phone}
                  onChange={(e) => setSiteData({...siteData, phone: e.target.value})}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Endereço</Label>
              <Input
                id="address"
                placeholder="Rua Exemplo, 123 - São Paulo, SP"
                value={siteData.address}
                onChange={(e) => setSiteData({...siteData, address: e.target.value})}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="whatsapp">WhatsApp (opcional)</Label>
              <Input
                id="whatsapp"
                placeholder="(11) 98765-4321"
                value={siteData.whatsapp}
                onChange={(e) => setSiteData({...siteData, whatsapp: e.target.value})}
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              className="w-full" 
              size="lg"
              onClick={() => setStep(2)}
              disabled={!siteData.businessName || !siteData.industry || !siteData.description}
            >
              Continuar <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Step 2: Geração */}
      {step === 2 && (
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Gerar Site com IA</CardTitle>
            <CardDescription>
              Vamos criar 3 variações de site para você escolher
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">O que será criado:</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span>Site completo com 4-6 páginas</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span>Conteúdo personalizado com IA</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span>3 variações de design para escolher</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span>Otimizado para SEO e mobile</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span>Integração com WhatsApp</span>
                </li>
              </ul>
            </div>

            {isGenerating && (
              <div className="space-y-4">
                <div className="flex items-center justify-center">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                </div>
                <Progress value={progress} className="w-full" />
                <p className="text-center text-sm text-muted-foreground">
                  {progressMessage}
                </p>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={() => setStep(1)}
              disabled={isGenerating}
            >
              Voltar
            </Button>
            <Button 
              className="flex-1" 
              size="lg"
              onClick={handleGenerateSite}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Gerando...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Gerar Site com IA
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Step 3: Escolha de Variação */}
      {step === 3 && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Escolha seu Design Preferido</CardTitle>
              <CardDescription>
                Selecione uma das 3 variações geradas pela IA
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {variations.map((variation, index) => (
                  <Card 
                    key={variation.id}
                    className={`cursor-pointer transition-all ${
                      selectedVariation === variation.id 
                        ? 'ring-2 ring-blue-600 bg-blue-50 dark:bg-blue-950' 
                        : 'hover:shadow-lg'
                    }`}
                    onClick={() => handleSelectVariation(variation.id)}
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{variation.name}</CardTitle>
                        {index === 1 && (
                          <Badge className="bg-green-600">Recomendado</Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Preview Mockado */}
                      <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-lg flex items-center justify-center">
                        <Eye className="h-8 w-8 text-gray-400" />
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Espaçamento:</span>
                          <span className="font-medium">{variation.style.spacing}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Cantos:</span>
                          <span className="font-medium">{variation.style.corners}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Sombras:</span>
                          <span className="font-medium">{variation.style.shadows}</span>
                        </div>
                      </div>
                      
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(variation.preview_url, '_blank');
                        }}
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        Ver Preview
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
            <CardFooter className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={() => setStep(2)}
              >
                Gerar Novas Variações
              </Button>
              <Button 
                className="flex-1" 
                size="lg"
                onClick={handleConfirmSite}
                disabled={!selectedVariation || isGenerating}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Criando Site...
                  </>
                ) : (
                  <>
                    Criar Este Site
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* Step 4: Site Pronto */}
      {step === 4 && generatedSite && (
        <Card className="max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
              <Check className="h-8 w-8 text-green-600" />
            </div>
            <CardTitle className="text-2xl">Site Criado com Sucesso!</CardTitle>
            <CardDescription>
              Seu site WordPress está pronto em {generatedSite.processing_time}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg space-y-3">
              <h3 className="font-semibold">Informações de Acesso:</h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">URL do Site:</span>
                  <a 
                    href={generatedSite.url} 
                    target="_blank" 
                    className="text-blue-600 hover:underline font-mono"
                  >
                    {generatedSite.url}
                  </a>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Painel Admin:</span>
                  <a 
                    href={generatedSite.admin_url} 
                    target="_blank" 
                    className="text-blue-600 hover:underline font-mono"
                  >
                    {generatedSite.admin_url}
                  </a>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Usuário:</span>
                  <code className="bg-gray-200 dark:bg-gray-800 px-2 py-1 rounded">
                    {generatedSite.username}
                  </code>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Senha:</span>
                  <code className="bg-gray-200 dark:bg-gray-800 px-2 py-1 rounded">
                    {generatedSite.password}
                  </code>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button 
                variant="outline"
                onClick={() => window.open(generatedSite.url, '_blank')}
              >
                <Eye className="mr-2 h-4 w-4" />
                Ver Site
              </Button>
              <Button 
                onClick={() => window.open(generatedSite.admin_url, '_blank')}
              >
                <Edit className="mr-2 h-4 w-4" />
                Editar no WordPress
              </Button>
            </div>
            
            <div className="pt-4 border-t">
              <Button 
                variant="default" 
                className="w-full"
                onClick={() => {
                  setStep(1);
                  setSiteData({
                    businessName: '',
                    businessType: '',
                    industry: '',
                    description: '',
                    email: '',
                    phone: '',
                    address: '',
                    whatsapp: ''
                  });
                  setVariations([]);
                  setSelectedVariation('');
                  setGeneratedSite(null);
                }}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Criar Outro Site
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}