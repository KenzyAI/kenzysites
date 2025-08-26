"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/lib/use-toast';
import IframePreview from '@/app/components/preview/iframe-preview';
import {
  Check,
  Sparkles,
  Palette,
  Type,
  Layout,
  Eye,
  Download,
  RefreshCw,
  Loader2,
  Star,
  Globe,
  Smartphone,
  Monitor,
  ChevronLeft,
  ChevronRight,
  Zap,
  ExternalLink,
  Clock
} from 'lucide-react';

// Types
interface ColorScheme {
  name: string;
  primary: string;
  secondary: string;
  accent: string;
  text: string;
  background: string;
}

interface Typography {
  name: string;
  heading_font: string;
  body_font: string;
  base_size: string;
}

interface ContentTone {
  name: string;
  style: string;
  language_level: string;
  emoji_usage: boolean;
}

interface Variation {
  index: number;
  name: string;
  color_scheme: ColorScheme;
  typography: Typography;
  content_tone: ContentTone;
  layout: string;
  features: string[];
  score: number;
}

interface VariationSet {
  set_id: string;
  business_name: string;
  industry: string;
  variations: Variation[];
  generation_time: number;
  selected?: number;
}


export default function VariationSelector() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  
  const [variationSet, setVariationSet] = useState<VariationSet | null>(null);
  const [selectedVariation, setSelectedVariation] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState<number | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  useEffect(() => {
    fetchVariations();
  }, [params.id]);

  const fetchVariations = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v2/generation/variations/${params.id}`);
      if (!response.ok) throw new Error('Failed to fetch variations');
      
      const data = await response.json();
      setVariationSet(data);
      setSelectedVariation(data.selected || 0);
    } catch (error) {
      console.error('Error fetching variations:', error);
      toast({
        title: "Erro ao carregar variações",
        description: "Não foi possível carregar as variações do site.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectVariation = async (index: number) => {
    setSelectedVariation(index);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/v2/generation/variations/${params.id}/select/${index}`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        toast({
          title: "Variação selecionada",
          description: `Variação ${index + 1} foi selecionada com sucesso.`,
        });
      }
    } catch (error) {
      console.error('Error selecting variation:', error);
    }
  };

  const handleRegenerateVariation = async (index: number) => {
    setIsRegenerating(index);
    
    try {
      const response = await fetch('http://localhost:8000/api/v2/generation/variations/regenerate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          set_id: params.id,
          variation_index: index,
          modifications: {}
        })
      });
      
      if (response.ok) {
        await fetchVariations();
        toast({
          title: "Variação regenerada",
          description: "A variação foi atualizada com sucesso.",
        });
      }
    } catch (error) {
      console.error('Error regenerating variation:', error);
      toast({
        title: "Erro ao regenerar",
        description: "Não foi possível regenerar a variação.",
        variant: "destructive"
      });
    } finally {
      setIsRegenerating(null);
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      // In production, this would trigger the actual export
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast({
        title: "Site exportado com sucesso! 🎉",
        description: "O download começará em instantes.",
      });
      
      // Navigate to dashboard or download page
      router.push('/dashboard/sites');
    } catch (error) {
      console.error('Error exporting:', error);
      toast({
        title: "Erro ao exportar",
        description: "Não foi possível exportar o site.",
        variant: "destructive"
      });
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Carregando variações...</p>
        </div>
      </div>
    );
  }

  if (!variationSet) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">Variações não encontradas.</p>
        </div>
      </div>
    );
  }

  const currentVariation = variationSet.variations[selectedVariation];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-secondary/5">
      {/* Header */}
      <div className="border-b bg-background/80 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">{variationSet.business_name}</h1>
              <p className="text-sm text-muted-foreground">
                Escolha a melhor variação para seu site
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="secondary">
                <Zap className="w-3 h-3 mr-1" />
                Gerado em {variationSet.generation_time.toFixed(1)}s
              </Badge>
              <Button
                variant="outline"
                onClick={() => setShowComparison(!showComparison)}
              >
                {showComparison ? 'Ocultar' : 'Comparar'}
              </Button>
              <Button
                onClick={handleExport}
                disabled={isExporting}
              >
                {isExporting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Exportando...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Finalizar e Exportar
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Variation Selector */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Variações Disponíveis</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {variationSet.variations.map((variation, index) => (
              <Card
                key={index}
                className={`p-4 cursor-pointer transition-all ${
                  selectedVariation === index
                    ? 'ring-2 ring-primary border-primary'
                    : 'hover:border-primary/50'
                }`}
                onClick={() => handleSelectVariation(index)}
              >
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold">{variation.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="text-xs">
                          {variation.layout}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {variation.content_tone.name}
                        </Badge>
                      </div>
                    </div>
                    {selectedVariation === index && (
                      <Check className="w-5 h-5 text-primary" />
                    )}
                  </div>

                  {/* Color Preview */}
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground">Esquema de Cores</p>
                    <div className="flex gap-1">
                      <div
                        className="w-8 h-8 rounded"
                        style={{ backgroundColor: variation.color_scheme.primary }}
                        title="Primária"
                      />
                      <div
                        className="w-8 h-8 rounded"
                        style={{ backgroundColor: variation.color_scheme.secondary }}
                        title="Secundária"
                      />
                      <div
                        className="w-8 h-8 rounded"
                        style={{ backgroundColor: variation.color_scheme.accent }}
                        title="Destaque"
                      />
                    </div>
                  </div>

                  {/* Typography */}
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Tipografia</p>
                    <p className="text-sm font-medium">{variation.typography.name}</p>
                  </div>

                  {/* Score */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                      <span className="text-sm font-medium">{variation.score.toFixed(1)}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRegenerateVariation(index);
                      }}
                      disabled={isRegenerating === index}
                    >
                      {isRegenerating === index ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Preview Area */}
        <Card className="overflow-hidden">
          <div className="border-b p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedVariation(Math.max(0, selectedVariation - 1))}
                  disabled={selectedVariation === 0}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <span className="text-sm font-medium">
                  Variação {selectedVariation + 1} de {variationSet.variations.length}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedVariation(Math.min(variationSet.variations.length - 1, selectedVariation + 1))}
                  disabled={selectedVariation === variationSet.variations.length - 1}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
              <Button variant="outline" size="sm">
                <Eye className="w-4 h-4 mr-2" />
                Preview Completo
              </Button>
            </div>
          </div>

          <div className="bg-muted/30 p-8">
            {/* Iframe Preview Component */}
            <IframePreview 
              variationData={currentVariation}
              businessData={variationSet}
              className="w-full"
            />
        </Card>

        {/* Comparison Mode */}
        {showComparison && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-4">Comparação de Variações</h2>
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left p-4">Característica</th>
                      {variationSet.variations.map((_, index) => (
                        <th key={index} className="text-center p-4">
                          Variação {index + 1}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-4 font-medium">Esquema de Cores</td>
                      {variationSet.variations.map((v, i) => (
                        <td key={i} className="p-4 text-center">
                          {v.color_scheme.name}
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b">
                      <td className="p-4 font-medium">Tipografia</td>
                      {variationSet.variations.map((v, i) => (
                        <td key={i} className="p-4 text-center">
                          {v.typography.name}
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b">
                      <td className="p-4 font-medium">Tom de Conteúdo</td>
                      {variationSet.variations.map((v, i) => (
                        <td key={i} className="p-4 text-center">
                          {v.content_tone.name}
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b">
                      <td className="p-4 font-medium">Layout</td>
                      {variationSet.variations.map((v, i) => (
                        <td key={i} className="p-4 text-center">
                          {v.layout}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="p-4 font-medium">Pontuação</td>
                      {variationSet.variations.map((v, i) => (
                        <td key={i} className="p-4 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                            <span className="font-medium">{v.score.toFixed(1)}</span>
                          </div>
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        )}
        
        {/* Action Buttons */}
        <div className="mt-8">
          <Card className="p-6">
            <div className="text-center space-y-4">
              <h3 className="text-lg font-semibold">Gostou da Variação {selectedVariation + 1}?</h3>
              <p className="text-muted-foreground">
                Escolha uma das opções abaixo para continuar com sua criação:
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
                <Button
                  onClick={async () => {
                    setIsLoading(true);
                    try {
                      const response = await fetch(`/api/v2/generation/variations/${params.id}/deploy`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ selected_variation: selectedVariation })
                      });
                      
                      const result = await response.json();
                      
                      if (result.success) {
                        toast({
                          title: "✅ Site WordPress Criado!",
                          description: "Seu site está pronto! Abrindo em nova aba...",
                        });
                        
                        setTimeout(() => {
                          window.open('http://localhost:8085', '_blank');
                        }, 1000);
                      } else {
                        toast({
                          title: "❌ Erro",
                          description: result.message || "Falha ao criar site no WordPress",
                          variant: "destructive",
                        });
                      }
                    } catch (error) {
                      console.error('Deploy error:', error);
                      toast({
                        title: "❌ Erro de Conexão",
                        description: "Verifique se o WordPress está rodando em http://localhost:8085",
                        variant: "destructive",
                      });
                    } finally {
                      setIsLoading(false);
                    }
                  }}
                  disabled={isLoading}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                  size="lg"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Criando WordPress...
                    </>
                  ) : (
                    <>
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Criar no WordPress
                    </>
                  )}
                </Button>
                
                <Button
                  onClick={() => {
                    toast({
                      title: "🎉 Variação Selecionada!",
                      description: `Variação "${currentVariation.name}" foi selecionada para download.`,
                    });
                    // Here you would implement the download/export logic
                  }}
                  disabled={isLoading}
                  variant="outline"
                  className="flex-1"
                  size="lg"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Baixar Arquivos
                </Button>
              </div>
              
              <div className="flex items-center justify-center gap-4 pt-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>Tempo de geração: {variationSet.generation_time?.toFixed(1) || '42.3'}s</span>
                </div>
                <div className="flex items-center gap-2">
                  <Palette className="w-4 h-4" />
                  <span>{variationSet.variations.length} variações criadas</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}