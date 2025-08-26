"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
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

export default function VariationSelector() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  
  const [selectedVariation, setSelectedVariation] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState<number | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // Mock data para teste
  const variationSet = {
    set_id: "test-123",
    business_name: "Teste Business",
    industry: "restaurant",
    variations: [
      {
        index: 0,
        name: "Moderno & Limpo",
        color_scheme: {
          name: "Moderno",
          primary: "#007cba",
          secondary: "#002c5f",
          accent: "#ffc107",
          text: "#333333",
          background: "#ffffff"
        },
        typography: {
          name: "Clean Sans",
          heading_font: "Montserrat",
          body_font: "Open Sans",
          base_size: "16px"
        },
        content_tone: {
          name: "Profissional",
          style: "formal",
          language_level: "standard",
          emoji_usage: false
        },
        layout: "modern",
        features: ["WhatsApp", "SEO", "Responsivo"],
        score: 8.5
      }
    ],
    generation_time: 45.2
  };

  const currentVariation = variationSet.variations[selectedVariation];

  useEffect(() => {
    // Simular carregamento
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  }, []);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-secondary/5">
      {/* Header */}
      <div className="border-b bg-background/80 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">{variationSet.business_name}</h1>
              <p className="text-sm text-muted-foreground">
                Selecione a variação ideal para seu site
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="secondary" className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {variationSet.generation_time}s
              </Badge>
              <Button
                onClick={() => router.push('/generation')}
                variant="outline"
                className="flex items-center gap-2"
              >
                <ChevronLeft className="w-4 h-4" />
                Nova Geração
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Preview Section */}
        <Card className="mb-8">
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4">Preview da Variação</h2>
            <IframePreview 
              variationData={currentVariation}
              businessData={variationSet}
              className="w-full"
            />
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-center gap-4 mb-8">
          <Button
            size="lg"
            className="flex items-center gap-2"
            onClick={() => {
              toast({
                title: "Site criado no WordPress! 🎉",
                description: "Redirecionando para seu novo site...",
              });
              setTimeout(() => {
                window.open('http://localhost:8085', '_blank');
              }, 1000);
            }}
          >
            <Zap className="w-5 h-5" />
            Criar no WordPress
          </Button>
          
          <Button
            variant="outline"
            size="lg"
            className="flex items-center gap-2"
            onClick={() => {
              toast({
                title: "Download iniciado 📦",
                description: `Variação "${currentVariation.name}" foi selecionada para download.`,
              });
            }}
          >
            <Download className="w-5 h-5" />
            Download
          </Button>
        </div>

        {/* Stats */}
        <Card>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary mb-1">
                  {currentVariation.score}/10
                </div>
                <p className="text-sm text-muted-foreground">Pontuação</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary mb-1">
                  {variationSet.generation_time}s
                </div>
                <p className="text-sm text-muted-foreground">Tempo de Geração</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary mb-1">
                  {variationSet.variations.length}
                </div>
                <p className="text-sm text-muted-foreground">Variações Criadas</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}