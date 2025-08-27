// WordPress Color Management - Global Settings Integration

export interface ColorScheme {
  primary: string
  secondary: string
  text: string
  accent: string
  background?: string
}

export interface ColorGenerationRequest {
  industry: 'medical' | 'business' | 'restaurant' | 'tech' | 'education' | 'other'
  mood: 'professional' | 'friendly' | 'modern' | 'classic' | 'creative'
  brandColors?: string[] // Cores existentes da marca
}

export class WordPressColorManager {
  constructor(private wpClient: any) {}

  /**
   * Gera esquema de cores usando IA + regra 60-30-10
   */
  async generateColorScheme(request: ColorGenerationRequest): Promise<ColorScheme> {
    // Cores base por indústria (machine learning approach)
    const industryColors = {
      medical: { hue: 200, saturation: 70, lightness: 45 }, // Azul confiança
      business: { hue: 220, saturation: 80, lightness: 40 }, // Azul corporativo  
      restaurant: { hue: 25, saturation: 85, lightness: 50 }, // Laranja apetitoso
      tech: { hue: 260, saturation: 75, lightness: 55 }, // Roxo inovação
      education: { hue: 120, saturation: 60, lightness: 45 }, // Verde crescimento
      other: { hue: 200, saturation: 65, lightness: 50 }
    }

    const base = industryColors[request.industry] || industryColors.other
    
    // Aplicar mood variations
    const moodAdjustments = {
      professional: { saturation: -10, lightness: -5 },
      friendly: { saturation: +15, lightness: +10 },
      modern: { saturation: +5, lightness: +5 },
      classic: { saturation: -15, lightness: -10 }, 
      creative: { saturation: +20, lightness: +15 }
    }

    const adjustment = moodAdjustments[request.mood]
    
    // Gerar cores seguindo strategy 60-30-10
    return {
      primary: this.hslToHex(
        base.hue,
        Math.max(0, Math.min(100, base.saturation + adjustment.saturation)),
        Math.max(0, Math.min(100, base.lightness + adjustment.lightness))
      ),
      secondary: this.hslToHex(
        (base.hue + 30) % 360, // Cor análoga
        Math.max(0, base.saturation - 20),
        Math.max(0, base.lightness + 20)
      ),
      accent: this.hslToHex(
        (base.hue + 180) % 360, // Cor complementar
        Math.min(100, base.saturation + 10),
        Math.max(0, base.lightness - 10)
      ),
      text: this.hslToHex(0, 0, 25), // Cinza escuro
      background: this.hslToHex(0, 0, 98) // Branco quase puro
    }
  }

  /**
   * Aplica esquema de cores no Elementor Kit via WordPress API
   */
  async applyColorSchemeToSite(siteId: number, colorScheme: ColorScheme): Promise<{
    success: boolean
    kitId?: number
    message: string
  }> {
    try {
      // 1. Obter Kit ID ativo
      const kitId = await this.getActiveKitId(siteId)
      
      // 2. Montar estrutura de cores do Elementor
      const elementorColors = {
        system_colors: [
          {
            _id: "primary",
            title: "Primary", 
            color: colorScheme.primary
          },
          {
            _id: "secondary",
            title: "Secondary",
            color: colorScheme.secondary  
          },
          {
            _id: "text",
            title: "Text",
            color: colorScheme.text
          },
          {
            _id: "accent", 
            title: "Accent",
            color: colorScheme.accent
          }
        ]
      }

      // 3. Atualizar via WordPress REST API
      const response = await this.wpClient.post(`/wp/v2/elementor-kits/${kitId}`, {
        meta: {
          elementor_page_settings: JSON.stringify(elementorColors)
        }
      })

      // 4. Regenerar CSS do Elementor
      await this.regenerateElementorCSS(siteId)

      return {
        success: true,
        kitId,
        message: 'Esquema de cores aplicado com sucesso!'
      }

    } catch (error) {
      return {
        success: false,
        message: `Erro ao aplicar cores: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      }
    }
  }

  /**
   * Obter ID do Kit ativo do Elementor
   */
  private async getActiveKitId(siteId: number): Promise<number> {
    // Alternar para o site específico (se multisite)
    if (siteId > 1) {
      await this.wpClient.switchToSite(siteId)
    }

    const response = await this.wpClient.get('/wp-json/wp/v2/elementor/options/elementor_active_kit')
    return parseInt(response.value)
  }

  /**
   * Regenerar CSS do Elementor após mudanças
   */
  private async regenerateElementorCSS(siteId: number): Promise<void> {
    try {
      await this.wpClient.post('/wp-json/elementor/v1/regenerate-css', {
        site_id: siteId
      })
    } catch (error) {
      console.warn('Aviso: CSS não foi regenerado automaticamente:', error)
    }
  }

  /**
   * Converter HSL para HEX
   */
  private hslToHex(h: number, s: number, l: number): string {
    l /= 100
    const a = s * Math.min(l, 1 - l) / 100
    const f = (n: number) => {
      const k = (n + h / 30) % 12
      const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
      return Math.round(255 * color).toString(16).padStart(2, '0')
    }
    return `#${f(0)}${f(8)}${f(4)}`
  }

  /**
   * Validar se as cores têm contraste adequado (WCAG)
   */
  validateColorContrast(colorScheme: ColorScheme): {
    valid: boolean
    issues: string[]
  } {
    const issues: string[] = []
    
    // Calcular contraste entre text e background
    const textContrast = this.calculateContrast(colorScheme.text, colorScheme.background || '#ffffff')
    
    if (textContrast < 4.5) {
      issues.push('Contraste insuficiente entre texto e fundo')
    }

    return {
      valid: issues.length === 0,
      issues
    }
  }

  /**
   * Calcular rácio de contraste entre duas cores
   */
  private calculateContrast(color1: string, color2: string): number {
    const getLuminance = (hex: string): number => {
      const r = parseInt(hex.slice(1, 3), 16) / 255
      const g = parseInt(hex.slice(3, 5), 16) / 255
      const b = parseInt(hex.slice(5, 7), 16) / 255
      
      const [rs, gs, bs] = [r, g, b].map(c => 
        c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
      )
      
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
    }

    const lum1 = getLuminance(color1)
    const lum2 = getLuminance(color2)
    const brightest = Math.max(lum1, lum2)
    const darkest = Math.min(lum1, lum2)
    
    return (brightest + 0.05) / (darkest + 0.05)
  }
}