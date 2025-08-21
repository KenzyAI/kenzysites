'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Site } from '@/lib/hooks/use-sites'
import {
  Monitor,
  Tablet,
  Smartphone,
  RefreshCw,
  ExternalLink,
  Eye,
  Maximize2,
  Minimize2,
  Loader2,
  Globe,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface SitePreviewProps {
  site: Site
  children?: React.ReactNode
}

type DeviceType = 'desktop' | 'tablet' | 'mobile'

const deviceSizes = {
  desktop: { width: '100%', height: '600px', label: 'Desktop' },
  tablet: { width: '768px', height: '500px', label: 'Tablet' },
  mobile: { width: '375px', height: '600px', label: 'Mobile' },
}

// Mock website content for demo purposes
const generateMockSiteContent = (site: Site) => {
  const colors = {
    'e-commerce': { primary: '#059669', secondary: '#10b981', accent: '#34d399' },
    'blog': { primary: '#3b82f6', secondary: '#60a5fa', accent: '#93c5fd' },
    'portfolio': { primary: '#8b5cf6', secondary: '#a78bfa', accent: '#c4b5fd' },
    'corporate': { primary: '#1f2937', secondary: '#374151', accent: '#6b7280' },
    'landing-page': { primary: '#f59e0b', secondary: '#fbbf24', accent: '#fcd34d' },
  }

  const categoryColors = colors[site.category] || colors.blog

  return `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${site.name}</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
          line-height: 1.6; 
          color: #333;
          background: #fff;
        }
        
        .header {
          background: ${categoryColors.primary};
          color: white;
          padding: 1rem 0;
          position: sticky;
          top: 0;
          z-index: 100;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 1rem;
        }
        
        .nav {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .logo {
          font-size: 1.5rem;
          font-weight: bold;
        }
        
        .nav-links {
          display: flex;
          gap: 2rem;
          list-style: none;
        }
        
        .nav-links a {
          color: white;
          text-decoration: none;
          transition: opacity 0.2s;
        }
        
        .nav-links a:hover {
          opacity: 0.8;
        }
        
        .hero {
          background: linear-gradient(135deg, ${categoryColors.primary}, ${categoryColors.secondary});
          color: white;
          text-align: center;
          padding: 4rem 0;
        }
        
        .hero h1 {
          font-size: 3rem;
          margin-bottom: 1rem;
          font-weight: 700;
        }
        
        .hero p {
          font-size: 1.2rem;
          margin-bottom: 2rem;
          opacity: 0.9;
        }
        
        .cta-button {
          background: ${categoryColors.accent};
          color: ${categoryColors.primary};
          padding: 1rem 2rem;
          border: none;
          border-radius: 8px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s;
        }
        
        .cta-button:hover {
          transform: translateY(-2px);
        }
        
        .features {
          padding: 4rem 0;
          background: #f8fafc;
        }
        
        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin-top: 2rem;
        }
        
        .feature-card {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
          text-align: center;
        }
        
        .feature-icon {
          width: 60px;
          height: 60px;
          background: ${categoryColors.primary};
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          color: white;
          font-size: 1.5rem;
        }
        
        .footer {
          background: #1f2937;
          color: white;
          text-align: center;
          padding: 2rem 0;
          margin-top: 4rem;
        }
        
        .stats {
          display: flex;
          justify-content: space-around;
          background: white;
          padding: 2rem;
          margin: -2rem auto 0;
          border-radius: 12px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.1);
          max-width: 800px;
          position: relative;
          z-index: 10;
        }
        
        .stat {
          text-align: center;
        }
        
        .stat-number {
          font-size: 2rem;
          font-weight: bold;
          color: ${categoryColors.primary};
        }
        
        .stat-label {
          color: #6b7280;
          font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
          .hero h1 { font-size: 2rem; }
          .hero p { font-size: 1rem; }
          .nav-links { display: none; }
          .features-grid { grid-template-columns: 1fr; }
          .stats { 
            flex-direction: column; 
            gap: 1rem; 
            margin: 0 1rem;
          }
        }
      </style>
    </head>
    <body>
      <header class="header">
        <div class="container">
          <nav class="nav">
            <div class="logo">${site.name}</div>
            <ul class="nav-links">
              <li><a href="#home">Home</a></li>
              <li><a href="#about">Sobre</a></li>
              <li><a href="#services">Serviços</a></li>
              <li><a href="#contact">Contato</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <section class="hero">
        <div class="container">
          <h1>Bem-vindo ao ${site.name}</h1>
          <p>${site.description || 'Site moderno e profissional criado com WordPress AI Builder'}</p>
          <button class="cta-button">Saiba Mais</button>
          
          <div class="stats">
            <div class="stat">
              <div class="stat-number">${site.visitors.toLocaleString()}</div>
              <div class="stat-label">Visitantes</div>
            </div>
            <div class="stat">
              <div class="stat-number">${site.backups}</div>
              <div class="stat-label">Backups</div>
            </div>
            <div class="stat">
              <div class="stat-number">99.9%</div>
              <div class="stat-label">Uptime</div>
            </div>
          </div>
        </div>
      </section>

      <section class="features">
        <div class="container">
          <h2 style="text-align: center; margin-bottom: 1rem; font-size: 2.5rem;">Nossos Diferenciais</h2>
          <p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">
            Categoria: ${site.category.replace('-', ' ')} | Tema: ${site.theme}
          </p>
          
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">🚀</div>
              <h3>Performance</h3>
              <p>Site otimizado para alta velocidade e excelente experiência do usuário.</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🔒</div>
              <h3>Segurança</h3>
              <p>Proteção avançada com SSL, firewall e backups automáticos diários.</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">📱</div>
              <h3>Responsivo</h3>
              <p>Design adaptável que funciona perfeitamente em todos os dispositivos.</p>
            </div>
          </div>
        </div>
      </section>

      <footer class="footer">
        <div class="container">
          <p>&copy; 2024 ${site.name}. Todos os direitos reservados.</p>
          <p style="margin-top: 0.5rem; opacity: 0.7;">
            Criado com WordPress AI Builder | ${site.domain}
          </p>
        </div>
      </footer>
    </body>
    </html>
  `
}

export function SitePreview({ site, children }: SitePreviewProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [device, setDevice] = useState<DeviceType>('desktop')
  const [loading, setLoading] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleRefresh = () => {
    setLoading(true)
    setRefreshKey(prev => prev + 1)
    setTimeout(() => setLoading(false), 1000)
  }

  const mockContent = generateMockSiteContent(site)

  useEffect(() => {
    // Reset device to desktop when opening modal
    if (isOpen) {
      setDevice('desktop')
      setIsFullscreen(false)
    }
  }, [isOpen])

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="outline" size="sm">
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </Button>
        )}
      </DialogTrigger>

      <DialogContent 
        className={cn(
          'transition-all duration-300',
          isFullscreen ? 'max-w-[95vw] h-[95vh]' : 'max-w-6xl max-h-[90vh]'
        )}
      >
        <DialogHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Preview - {site.name}
              </DialogTitle>
              <DialogDescription>
                Visualização responsiva do site em diferentes dispositivos
              </DialogDescription>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsFullscreen(!isFullscreen)}
              >
                {isFullscreen ? (
                  <Minimize2 className="h-4 w-4" />
                ) : (
                  <Maximize2 className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </DialogHeader>

        {/* Site Info Bar */}
        <div className="flex items-center justify-between p-3 bg-muted rounded-lg flex-shrink-0">
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="flex items-center gap-1">
              <div className={`h-2 w-2 rounded-full bg-green-500`} />
              {site.status === 'active' ? 'Ativo' : 'Inativo'}
            </Badge>
            <span className="text-sm text-muted-foreground">
              {site.domain}
            </span>
            {site.ssl && (
              <Badge variant="outline" className="text-xs">
                🔒 SSL
              </Badge>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
            >
              <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              asChild
            >
              <a href={`https://${site.domain}`} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4" />
              </a>
            </Button>
          </div>
        </div>

        {/* Device Selector */}
        <div className="flex items-center justify-center gap-2 p-2 bg-muted rounded-lg flex-shrink-0">
          {Object.entries(deviceSizes).map(([key, config]) => (
            <Button
              key={key}
              variant={device === key ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setDevice(key as DeviceType)}
              className="flex items-center gap-2"
            >
              {key === 'desktop' && <Monitor className="h-4 w-4" />}
              {key === 'tablet' && <Tablet className="h-4 w-4" />}
              {key === 'mobile' && <Smartphone className="h-4 w-4" />}
              {config.label}
            </Button>
          ))}
        </div>

        {/* Preview Container */}
        <div className="flex-1 flex items-center justify-center p-4 min-h-0">
          <div 
            className={cn(
              'relative bg-white rounded-lg shadow-2xl transition-all duration-300',
              device === 'desktop' && 'w-full h-full',
              device === 'tablet' && 'w-[768px] h-[500px]',
              device === 'mobile' && 'w-[375px] h-[600px]'
            )}
            style={{
              maxWidth: device === 'desktop' ? '100%' : deviceSizes[device].width,
              maxHeight: device === 'desktop' ? '100%' : deviceSizes[device].height,
            }}
          >
            {/* Device Frame (for mobile/tablet) */}
            {device !== 'desktop' && (
              <>
                {/* Status bar for mobile */}
                {device === 'mobile' && (
                  <div className="absolute top-0 left-0 right-0 h-8 bg-black rounded-t-lg flex items-center justify-center">
                    <div className="flex items-center gap-1">
                      <div className="w-4 h-2 bg-white rounded-sm opacity-80" />
                      <div className="w-1 h-1 bg-white rounded-full" />
                      <div className="w-1 h-1 bg-white rounded-full" />
                      <div className="w-1 h-1 bg-white rounded-full" />
                      <div className="text-white text-xs ml-auto mr-2">100%</div>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Loading Overlay */}
            {loading && (
              <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-50 rounded-lg">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Carregando preview...</span>
                </div>
              </div>
            )}

            {/* Iframe */}
            <iframe
              key={refreshKey}
              srcDoc={mockContent}
              className={cn(
                'w-full h-full border-0 bg-white transition-all duration-300',
                device === 'mobile' ? 'rounded-lg mt-8' : 'rounded-lg',
                loading && 'opacity-30'
              )}
              title={`Preview ${site.name} - ${device}`}
              sandbox="allow-scripts allow-same-origin"
              loading="lazy"
            />

            {/* Device Info Overlay */}
            <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
              {deviceSizes[device].width} × {deviceSizes[device].height}
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="flex items-center justify-between text-sm text-muted-foreground border-t pt-3 flex-shrink-0">
          <div className="flex items-center gap-4">
            <span>Tema: {site.theme}</span>
            <span>Categoria: {site.category.replace('-', ' ')}</span>
            <span>PHP: {site.phpVersion}</span>
          </div>
          
          <div className="flex items-center gap-2">
            <Settings className="h-3 w-3" />
            <span>Preview Mode</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}