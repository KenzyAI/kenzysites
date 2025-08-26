'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Monitor,
  Tablet,
  Smartphone,
  RefreshCw,
  ExternalLink,
  Download,
  Settings,
  Maximize2,
  Code,
  Eye,
  EyeOff,
  Palette,
  Zap
} from 'lucide-react';

interface SiteData {
  id: string;
  business_name: string;
  template_name: string;
  industry: string;
  html_content?: string;
  wordpress_url?: string;
  variation_index?: number;
  color_scheme?: {
    primary: string;
    secondary: string;
    accent: string;
  };
}

type DeviceMode = 'desktop' | 'tablet' | 'mobile';

const deviceSizes = {
  desktop: { width: '100%', height: '100%' },
  tablet: { width: '768px', height: '1024px' },
  mobile: { width: '375px', height: '812px' }
};

export default function SitePreview() {
  const params = useParams();
  const router = useRouter();
  const siteId = params.id as string;
  
  const [siteData, setSiteData] = useState<SiteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [deviceMode, setDeviceMode] = useState<DeviceMode>('desktop');
  const [showGrid, setShowGrid] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    fetchSiteData();
  }, [siteId]);

  const fetchSiteData = async () => {
    try {
      // In production, fetch from API
      // const response = await fetch(`http://localhost:8000/api/v2/generation/preview/${siteId}`);
      // const data = await response.json();
      
      // Mock data for development
      const mockData: SiteData = {
        id: siteId,
        business_name: 'Restaurante Sabor Brasileiro',
        template_name: 'Restaurant Premium',
        industry: 'restaurant',
        wordpress_url: 'https://sabor-brasileiro.kenzysites.com',
        variation_index: 1,
        color_scheme: {
          primary: '#D97706',
          secondary: '#92400E',
          accent: '#FCD34D'
        },
        html_content: `
          <!DOCTYPE html>
          <html lang="pt-BR">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Restaurante Sabor Brasileiro</title>
            <style>
              * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
              }
              body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
              }
              .header {
                background: linear-gradient(135deg, #D97706 0%, #92400E 100%);
                color: white;
                padding: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
              }
              .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
              }
              .nav {
                display: flex;
                justify-content: space-between;
                align-items: center;
              }
              .logo {
                font-size: 24px;
                font-weight: bold;
              }
              .nav-links {
                display: flex;
                gap: 30px;
                list-style: none;
              }
              .nav-links a {
                color: white;
                text-decoration: none;
                transition: opacity 0.3s;
              }
              .nav-links a:hover {
                opacity: 0.8;
              }
              .hero {
                background: url('https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200') center/cover;
                height: 500px;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
              }
              .hero::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
              }
              .hero-content {
                position: relative;
                text-align: center;
                color: white;
                z-index: 1;
              }
              .hero h1 {
                font-size: 48px;
                margin-bottom: 20px;
              }
              .hero p {
                font-size: 20px;
                margin-bottom: 30px;
              }
              .btn {
                display: inline-block;
                padding: 12px 30px;
                background: #FCD34D;
                color: #92400E;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                transition: transform 0.3s;
              }
              .btn:hover {
                transform: translateY(-2px);
              }
              .section {
                padding: 60px 0;
              }
              .section-title {
                text-align: center;
                font-size: 36px;
                margin-bottom: 40px;
                color: #92400E;
              }
              .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-top: 40px;
              }
              .feature-card {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s;
              }
              .feature-card:hover {
                transform: translateY(-5px);
              }
              .feature-icon {
                font-size: 48px;
                margin-bottom: 20px;
              }
              .feature-title {
                font-size: 24px;
                margin-bottom: 15px;
                color: #D97706;
              }
              .whatsapp-float {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #25D366;
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                cursor: pointer;
                transition: transform 0.3s;
              }
              .whatsapp-float:hover {
                transform: scale(1.1);
              }
              @media (max-width: 768px) {
                .nav-links {
                  display: none;
                }
                .hero h1 {
                  font-size: 32px;
                }
                .hero p {
                  font-size: 16px;
                }
              }
            </style>
          </head>
          <body>
            <header class="header">
              <div class="container">
                <nav class="nav">
                  <div class="logo">🍴 Sabor Brasileiro</div>
                  <ul class="nav-links">
                    <li><a href="#home">Início</a></li>
                    <li><a href="#menu">Cardápio</a></li>
                    <li><a href="#about">Sobre</a></li>
                    <li><a href="#contact">Contato</a></li>
                  </ul>
                </nav>
              </div>
            </header>
            
            <section class="hero">
              <div class="hero-content">
                <h1>Bem-vindo ao Sabor Brasileiro</h1>
                <p>A melhor experiência gastronômica da cidade</p>
                <a href="#menu" class="btn">Ver Cardápio</a>
              </div>
            </section>
            
            <section class="section">
              <div class="container">
                <h2 class="section-title">Nossos Diferenciais</h2>
                <div class="features">
                  <div class="feature-card">
                    <div class="feature-icon">🍽️</div>
                    <h3 class="feature-title">Pratos Exclusivos</h3>
                    <p>Receitas únicas desenvolvidas por nossos chefs renomados</p>
                  </div>
                  <div class="feature-card">
                    <div class="feature-icon">🚚</div>
                    <h3 class="feature-title">Delivery Rápido</h3>
                    <p>Entregamos em toda a cidade em até 45 minutos</p>
                  </div>
                  <div class="feature-card">
                    <div class="feature-icon">💳</div>
                    <h3 class="feature-title">Pagamento PIX</h3>
                    <p>Aceite PIX e receba descontos especiais</p>
                  </div>
                </div>
              </div>
            </section>
            
            <div class="whatsapp-float">
              📱
            </div>
          </body>
          </html>
        `
      };
      
      setSiteData(mockData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching site data:', error);
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleFullscreen = () => {
    if (!isFullscreen) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setIsFullscreen(!isFullscreen);
  };

  const handleExport = () => {
    if (siteData?.html_content) {
      const blob = new Blob([siteData.html_content], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${siteData.business_name.toLowerCase().replace(/\s+/g, '-')}.html`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (!siteData) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Site não encontrado</h2>
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700"
          >
            Voltar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Toolbar */}
      <div className="bg-white border-b px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left Section */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            
            <div>
              <h1 className="text-lg font-semibold text-gray-900">{siteData.business_name}</h1>
              <p className="text-sm text-gray-500">
                {siteData.template_name} • Variação #{siteData.variation_index || 1}
              </p>
            </div>
          </div>

          {/* Center Section - Device Selector */}
          <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setDeviceMode('desktop')}
              className={`p-2 rounded ${deviceMode === 'desktop' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'} transition-colors`}
              title="Desktop"
            >
              <Monitor className="w-5 h-5" />
            </button>
            <button
              onClick={() => setDeviceMode('tablet')}
              className={`p-2 rounded ${deviceMode === 'tablet' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'} transition-colors`}
              title="Tablet"
            >
              <Tablet className="w-5 h-5" />
            </button>
            <button
              onClick={() => setDeviceMode('mobile')}
              className={`p-2 rounded ${deviceMode === 'mobile' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'} transition-colors`}
              title="Mobile"
            >
              <Smartphone className="w-5 h-5" />
            </button>
          </div>

          {/* Right Section - Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowGrid(!showGrid)}
              className={`p-2 rounded-lg transition-colors ${showGrid ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'}`}
              title="Grid de Layout"
            >
              {showGrid ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
            </button>
            
            <button
              onClick={() => setShowCode(!showCode)}
              className={`p-2 rounded-lg transition-colors ${showCode ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'}`}
              title="Ver Código"
            >
              <Code className="w-5 h-5" />
            </button>
            
            <button
              onClick={handleRefresh}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Recarregar"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            
            <button
              onClick={handleFullscreen}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Tela Cheia"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
            
            <div className="h-6 w-px bg-gray-300 mx-2" />
            
            <button
              onClick={handleExport}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Exportar HTML"
            >
              <Download className="w-5 h-5" />
            </button>
            
            {siteData.wordpress_url && (
              <a
                href={siteData.wordpress_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Abrir no WordPress"
              >
                <ExternalLink className="w-5 h-5" />
              </a>
            )}
            
            <button
              onClick={() => router.push(`/generation/variations/${siteId}`)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Palette className="w-4 h-4" />
              Ver Variações
            </button>
          </div>
        </div>
      </div>

      {/* Preview Container */}
      <div className="flex-1 flex items-center justify-center p-8 relative">
        {/* Grid Overlay */}
        {showGrid && (
          <div 
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.03) 0px, transparent 1px, transparent 40px, rgba(0,0,0,0.03) 41px), repeating-linear-gradient(90deg, rgba(0,0,0,0.03) 0px, transparent 1px, transparent 40px, rgba(0,0,0,0.03) 41px)',
              backgroundSize: '40px 40px',
            }}
          />
        )}

        {/* Device Frame */}
        <div
          className={`bg-white rounded-lg shadow-2xl transition-all duration-300 ${
            deviceMode !== 'desktop' ? 'border-8 border-gray-800' : ''
          }`}
          style={{
            width: deviceSizes[deviceMode].width,
            height: deviceSizes[deviceMode].height,
            maxWidth: '100%',
            maxHeight: '100%',
          }}
        >
          {/* Code View */}
          {showCode ? (
            <div className="h-full overflow-auto bg-gray-900 text-gray-300 p-4">
              <pre className="text-sm">
                <code>{siteData.html_content}</code>
              </pre>
            </div>
          ) : (
            /* Preview iframe */
            <iframe
              key={refreshKey}
              srcDoc={siteData.html_content}
              className="w-full h-full rounded-lg"
              style={{
                border: 'none',
                borderRadius: deviceMode === 'desktop' ? '8px' : '0',
              }}
              title="Site Preview"
              sandbox="allow-scripts allow-same-origin"
            />
          )}
        </div>

        {/* Device Label */}
        {deviceMode !== 'desktop' && (
          <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 bg-black text-white px-3 py-1 rounded-full text-sm">
            {deviceMode === 'tablet' ? 'iPad (768x1024)' : 'iPhone (375x812)'}
          </div>
        )}
      </div>

      {/* Color Scheme Indicator */}
      {siteData.color_scheme && (
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3">
          <p className="text-xs text-gray-500 mb-2">Esquema de Cores</p>
          <div className="flex gap-2">
            <div 
              className="w-8 h-8 rounded border-2 border-gray-200"
              style={{ backgroundColor: siteData.color_scheme.primary }}
              title="Primária"
            />
            <div 
              className="w-8 h-8 rounded border-2 border-gray-200"
              style={{ backgroundColor: siteData.color_scheme.secondary }}
              title="Secundária"
            />
            <div 
              className="w-8 h-8 rounded border-2 border-gray-200"
              style={{ backgroundColor: siteData.color_scheme.accent }}
              title="Destaque"
            />
          </div>
        </div>
      )}
    </div>
  );
}