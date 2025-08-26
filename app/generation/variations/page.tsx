'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useRouter } from 'next/navigation';
import { 
  CheckCircle, 
  Zap, 
  Globe, 
  Smartphone,
  Search,
  MessageCircle,
  CreditCard,
  ArrowLeft,
  ExternalLink,
  Star
} from 'lucide-react';

export default function VariationsPage() {
  const router = useRouter();
  const [variations, setVariations] = useState<any[]>([]);
  const [selectedVariation, setSelectedVariation] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load variations from sessionStorage
    const storedData = sessionStorage.getItem('generatedVariations');
    if (storedData) {
      const data = JSON.parse(storedData);
      setVariations(data.variations || []);
    }
  }, []);

  const handleSelectVariation = async (variationId: string) => {
    setSelectedVariation(variationId);
    setIsLoading(true);
    
    // Simulate WordPress site creation
    setTimeout(() => {
      router.push('/dashboard/sites');
    }, 2000);
  };

  const getFeatureIcon = (feature: string) => {
    switch(feature) {
      case 'responsive': return <Smartphone className="w-4 h-4" />;
      case 'seo_optimized': return <Search className="w-4 h-4" />;
      case 'fast_loading': return <Zap className="w-4 h-4" />;
      case 'whatsapp_integration': return <MessageCircle className="w-4 h-4" />;
      case 'pix_payment': return <CreditCard className="w-4 h-4" />;
      default: return <CheckCircle className="w-4 h-4" />;
    }
  };

  if (variations.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-muted p-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">Nenhuma variação disponível</h1>
          <p className="text-muted-foreground mb-8">
            Por favor, gere um site primeiro.
          </p>
          <Button onClick={() => router.push('/generation')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar para Geração
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <Badge className="mb-4" variant="secondary">
            <Star className="w-3 h-3 mr-1" />
            IA Gerou {variations.length} Variações
          </Badge>
          <h1 className="text-4xl font-bold mb-4">
            Escolha o Design Perfeito 🎨
          </h1>
          <p className="text-xl text-muted-foreground">
            Cada variação foi otimizada para o seu negócio
          </p>
        </div>

        {/* Variations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {variations.map((variation, index) => (
            <Card 
              key={variation.id}
              className={`overflow-hidden transition-all duration-300 ${
                selectedVariation === variation.id 
                  ? 'ring-4 ring-primary shadow-2xl scale-105' 
                  : 'hover:shadow-xl hover:scale-102'
              }`}
            >
              {/* Preview Image */}
              <div className="aspect-video bg-gradient-to-br from-primary/10 to-primary/5 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <Globe className="w-16 h-16 text-primary/30 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Preview</p>
                  </div>
                </div>
                {variation.score && (
                  <Badge className="absolute top-4 right-4">
                    Score: {variation.score}
                  </Badge>
                )}
              </div>

              {/* Content */}
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">{variation.name}</h3>
                <p className="text-muted-foreground mb-4">
                  {variation.description}
                </p>

                {/* Features */}
                <div className="space-y-2 mb-4">
                  {Object.entries(variation.features || {})
                    .filter(([_, value]) => value === true)
                    .slice(0, 3)
                    .map(([feature, _]) => (
                      <div key={feature} className="flex items-center gap-2 text-sm">
                        {getFeatureIcon(feature)}
                        <span className="capitalize">
                          {feature.replace(/_/g, ' ')}
                        </span>
                      </div>
                    ))
                  }
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => window.open(`/preview/${variation.id}`, '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-1" />
                    Preview
                  </Button>
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={() => handleSelectVariation(variation.id)}
                    disabled={isLoading && selectedVariation === variation.id}
                  >
                    {isLoading && selectedVariation === variation.id ? (
                      <>Criando...</>
                    ) : (
                      <>Escolher</>
                    )}
                  </Button>
                </div>

                {/* Time estimate */}
                {variation.estimated_time && (
                  <p className="text-xs text-muted-foreground text-center mt-3">
                    Tempo estimado: {variation.estimated_time}
                  </p>
                )}
              </div>
            </Card>
          ))}
        </div>

        {/* Footer Actions */}
        <div className="mt-12 text-center">
          <Button 
            variant="outline" 
            onClick={() => router.push('/generation')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Gerar Novas Variações
          </Button>
        </div>
      </div>
    </div>
  );
}