"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Monitor, 
  Smartphone, 
  Tablet, 
  RefreshCw, 
  ExternalLink,
  Loader2,
  Eye,
  AlertCircle
} from 'lucide-react';

interface IframePreviewProps {
  variationData: any;
  businessData: any;
  className?: string;
}

type DeviceMode = 'desktop' | 'tablet' | 'mobile';

const IframePreview: React.FC<IframePreviewProps> = ({ 
  variationData, 
  businessData, 
  className = '' 
}) => {
  const [deviceMode, setDeviceMode] = useState<DeviceMode>('desktop');
  const [isLoading, setIsLoading] = useState(true);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    generatePreviewUrl();
  }, [variationData, businessData]);

  const generatePreviewUrl = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      // Create preview data
      const previewData = {
        business_name: businessData.business_name,
        industry: businessData.industry,
        description: businessData.business_description,
        variation: variationData,
        timestamp: Date.now()
      };

      // Generate preview HTML
      const previewHtml = generatePreviewHTML(previewData);
      
      // Create blob URL for iframe
      const blob = new Blob([previewHtml], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
      
    } catch (err) {
      console.error('Error generating preview:', err);
      setError('Erro ao gerar preview');
    } finally {
      setIsLoading(false);
    }
  };

  const generatePreviewHTML = (data: any) => {
    const { business_name, industry, description, variation } = data;
    
    const industryContent = {
      restaurant: {
        hero_title: 'Sabores Autênticos da Nossa Cozinha',
        hero_subtitle: 'Descubra pratos únicos preparados com ingredientes frescos e técnicas tradicionais.',
        cta_primary: 'Ver Cardápio',
        cta_secondary: 'Reservar Mesa',
        sections: [
          { title: 'Nossos Pratos', content: 'Especialidades da casa preparadas com amor e tradição.' },
          { title: 'Ambiente Acolhedor', content: 'Um espaço pensado para momentos especiais em família.' },
          { title: 'Ingredientes Frescos', content: 'Selecionamos os melhores ingredientes da região.' }
        ]
      },
      healthcare: {
        hero_title: 'Cuidando da Sua Saúde com Excelência',
        hero_subtitle: 'Atendimento médico especializado com tecnologia de ponta e cuidado humanizado.',
        cta_primary: 'Agendar Consulta',
        cta_secondary: 'Emergência 24h',
        sections: [
          { title: 'Especialistas Qualificados', content: 'Equipe médica com anos de experiência e formação continuada.' },
          { title: 'Tecnologia Avançada', content: 'Equipamentos modernos para diagnósticos precisos.' },
          { title: 'Atendimento Humanizado', content: 'Cuidado integral focado no bem-estar do paciente.' }
        ]
      },
      ecommerce: {
        hero_title: 'Produtos Premium para Você',
        hero_subtitle: 'Encontre os melhores produtos com qualidade garantida e entrega rápida.',
        cta_primary: 'Ver Produtos',
        cta_secondary: 'Ofertas Especiais',
        sections: [
          { title: 'Qualidade Garantida', content: 'Produtos selecionados com certificação de qualidade.' },
          { title: 'Entrega Rápida', content: 'Receba em casa com segurança e agilidade.' },
          { title: 'Atendimento Exclusivo', content: 'Suporte personalizado para sua melhor experiência.' }
        ]
      },
      services: {
        hero_title: 'Soluções Profissionais de Qualidade',
        hero_subtitle: 'Serviços especializados para atender às suas necessidades com excelência.',
        cta_primary: 'Contratar Serviço',
        cta_secondary: 'Orçamento Grátis',
        sections: [
          { title: 'Profissionais Capacitados', content: 'Equipe especializada e experiente em cada área.' },
          { title: 'Resultados Garantidos', content: 'Compromisso com a qualidade e satisfação do cliente.' },
          { title: 'Atendimento Personalizado', content: 'Soluções sob medida para cada necessidade.' }
        ]
      },
      education: {
        hero_title: 'Educação de Qualidade para o Futuro',
        hero_subtitle: 'Formação completa com metodologia moderna e professores especializados.',
        cta_primary: 'Matricule-se',
        cta_secondary: 'Aula Experimental',
        sections: [
          { title: 'Metodologia Inovadora', content: 'Ensino moderno focado no desenvolvimento integral.' },
          { title: 'Professores Qualificados', content: 'Educadores experientes e apaixonados pelo ensino.' },
          { title: 'Infraestrutura Completa', content: 'Ambiente preparado para uma educação de excelência.' }
        ]
      }
    };

    const content = industryContent[industry as keyof typeof industryContent] || industryContent.services;

    return `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${business_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=${variation.typography.heading_font.replace(' ', '+')}:wght@400;600;700&family=${variation.typography.body_font.replace(' ', '+')}:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: ${variation.color_scheme.primary};
            --secondary: ${variation.color_scheme.secondary};
            --accent: ${variation.color_scheme.accent};
            --text: ${variation.color_scheme.text};
            --bg: ${variation.color_scheme.background};
        }
        .primary-color { color: var(--primary); }
        .secondary-color { color: var(--secondary); }
        .accent-color { color: var(--accent); }
        .text-color { color: var(--text); }
        .bg-primary { background-color: var(--primary); }
        .bg-secondary { background-color: var(--secondary); }
        .bg-accent { background-color: var(--accent); }
        .border-primary { border-color: var(--primary); }
        .heading-font { font-family: '${variation.typography.heading_font}', sans-serif; }
        .body-font { font-family: '${variation.typography.body_font}', sans-serif; }
        
        .whatsapp-float {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #25D366;
            color: white;
            border-radius: 50px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            transition: transform 0.3s ease;
        }
        .whatsapp-float:hover {
            transform: scale(1.1);
        }
        
        .animate-fade-in {
            animation: fadeIn 0.8s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .gradient-bg {
            background: linear-gradient(135deg, ${variation.color_scheme.primary}15, ${variation.color_scheme.secondary}10);
        }
    </style>
</head>
<body class="bg-white body-font" style="color: var(--text);">
    <!-- Header -->
    <header class="border-b bg-white/95 backdrop-blur-sm fixed w-full top-0 z-50">
        <div class="container mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
                        <span class="text-white font-bold text-lg">${business_name.charAt(0)}</span>
                    </div>
                    <h1 class="text-xl font-bold heading-font primary-color">${business_name}</h1>
                </div>
                <nav class="hidden md:flex space-x-8">
                    <a href="#home" class="text-color hover:text-primary transition-colors">Início</a>
                    <a href="#about" class="text-color hover:text-primary transition-colors">Sobre</a>
                    <a href="#services" class="text-color hover:text-primary transition-colors">Serviços</a>
                    <a href="#contact" class="text-color hover:text-primary transition-colors">Contato</a>
                </nav>
                <button class="md:hidden p-2">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                    </svg>
                </button>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section id="home" class="gradient-bg pt-24 pb-16 animate-fade-in">
        <div class="container mx-auto px-4 text-center">
            <h2 class="text-4xl md:text-6xl font-bold heading-font primary-color mb-6">
                ${content.hero_title}
            </h2>
            <p class="text-xl body-font text-gray-600 mb-8 max-w-3xl mx-auto">
                ${content.hero_subtitle}
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <button class="bg-primary text-white px-8 py-4 rounded-lg font-semibold hover:opacity-90 transition-opacity">
                    ${content.cta_primary}
                </button>
                <button class="border-2 border-primary primary-color px-8 py-4 rounded-lg font-semibold hover:bg-primary hover:text-white transition-colors">
                    ${content.cta_secondary}
                </button>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="about" class="py-16 bg-gray-50">
        <div class="container mx-auto px-4">
            <div class="grid md:grid-cols-3 gap-8">
                ${content.sections.map((section, index) => `
                    <div class="bg-white p-8 rounded-xl shadow-sm hover:shadow-lg transition-shadow">
                        <div class="w-16 h-16 bg-primary rounded-lg flex items-center justify-center mb-6">
                            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold heading-font primary-color mb-4">${section.title}</h3>
                        <p class="body-font text-gray-600">${section.content}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-16 bg-white">
        <div class="container mx-auto px-4 text-center">
            <h3 class="text-3xl font-bold heading-font primary-color mb-8">Entre em Contato</h3>
            <p class="text-lg body-font text-gray-600 mb-8">${description}</p>
            <div class="flex flex-col sm:flex-row gap-6 justify-center items-center">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                        <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
                        </svg>
                    </div>
                    <span class="body-font">(11) 99999-9999</span>
                </div>
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                        <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                        </svg>
                    </div>
                    <span class="body-font">@${business_name.toLowerCase().replace(/\s+/g, '')}</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-8">
        <div class="container mx-auto px-4 text-center">
            <p class="body-font">&copy; ${new Date().getFullYear()} ${business_name}. Todos os direitos reservados.</p>
            <p class="body-font text-gray-400 text-sm mt-2">Criado com KenzySites</p>
        </div>
    </footer>

    <!-- WhatsApp Float Button -->
    <a href="https://wa.me/5511999999999" target="_blank" class="whatsapp-float">
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
        </svg>
    </a>
</body>
</html>`;
  };

  const getDeviceDimensions = () => {
    switch (deviceMode) {
      case 'mobile':
        return { width: '375px', height: '667px' };
      case 'tablet':
        return { width: '768px', height: '1024px' };
      case 'desktop':
      default:
        return { width: '100%', height: '800px' };
    }
  };

  const dimensions = getDeviceDimensions();

  return (
    <Card className={`overflow-hidden ${className}`}>
      {/* Device Mode Controls */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-b">
        <div className="flex items-center gap-2">
          <Button
            variant={deviceMode === 'desktop' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setDeviceMode('desktop')}
            className="flex items-center gap-2"
          >
            <Monitor className="w-4 h-4" />
            Desktop
          </Button>
          <Button
            variant={deviceMode === 'tablet' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setDeviceMode('tablet')}
            className="flex items-center gap-2"
          >
            <Tablet className="w-4 h-4" />
            Tablet
          </Button>
          <Button
            variant={deviceMode === 'mobile' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setDeviceMode('mobile')}
            className="flex items-center gap-2"
          >
            <Smartphone className="w-4 h-4" />
            Mobile
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="flex items-center gap-1">
            <Eye className="w-3 h-3" />
            Preview ao Vivo
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={generatePreviewUrl}
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Atualizar
          </Button>
          {previewUrl && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(previewUrl, '_blank')}
              className="flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              Abrir
            </Button>
          )}
        </div>
      </div>

      {/* Preview Frame */}
      <div className="bg-gray-100 p-4 flex justify-center">
        <div
          className="bg-white rounded-lg shadow-xl overflow-hidden transition-all duration-300"
          style={{
            width: dimensions.width,
            height: dimensions.height,
            maxWidth: '100%'
          }}
        >
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">Gerando preview...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <AlertCircle className="w-8 h-8 mx-auto mb-4 text-red-400" />
                <p className="text-red-600 mb-4">{error}</p>
                <Button onClick={generatePreviewUrl} variant="outline" size="sm">
                  Tentar Novamente
                </Button>
              </div>
            </div>
          ) : (
            <iframe
              src={previewUrl}
              className="w-full h-full border-0"
              title="Site Preview"
              sandbox="allow-same-origin allow-scripts"
            />
          )}
        </div>
      </div>
    </Card>
  );
};

export default IframePreview;