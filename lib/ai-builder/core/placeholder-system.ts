// Sistema de Placeholders Inteligentes para Templates Elementor

export interface PlaceholderMapping {
  key: string
  type: 'text' | 'image' | 'url' | 'phone' | 'email' | 'cta' | 'list'
  context: string // Contexto semântico para o agente
  required: boolean
  fallback?: string
  validation?: RegExp
}

export interface TemplatePlaceholders {
  templateId: string
  placeholders: PlaceholderMapping[]
  sections: {
    [sectionName: string]: {
      priority: number
      placeholders: string[] // keys dos placeholders
    }
  }
}

export class PlaceholderSystem {
  private placeholderPattern = /\{\{([A-Z_]+(?:\.[A-Z_]+)*)\}\}/g
  
  /**
   * Analisa um template e extrai placeholders automaticamente
   */
  extractPlaceholders(template: any): TemplatePlaceholders {
    const placeholders: PlaceholderMapping[] = []
    const sections: { [key: string]: { priority: number; placeholders: string[] } } = {}
    
    this.scanElement(template.content, placeholders, sections)
    
    return {
      templateId: template.id,
      placeholders: this.deduplicatePlaceholders(placeholders),
      sections
    }
  }
  
  /**
   * Escaneia elementos recursivamente procurando por placeholders
   */
  private scanElement(elements: any[], placeholders: PlaceholderMapping[], sections: any, level = 0) {
    elements.forEach((element, index) => {
      const sectionKey = `section_${level}_${index}`
      
      if (element.settings) {
        const textFields = ['title', 'text', 'editor', 'content', 'caption', 'description', 'button_text']
        
        textFields.forEach(field => {
          if (element.settings[field] && typeof element.settings[field] === 'string') {
            const text = element.settings[field]
            const matches = text.matchAll(this.placeholderPattern)
            
            for (const match of matches) {
              const placeholder = this.createPlaceholderMapping(
                match[1], 
                field, 
                element.widgetType || element.elType,
                text
              )
              
              placeholders.push(placeholder)
              
              if (!sections[sectionKey]) {
                sections[sectionKey] = { priority: level, placeholders: [] }
              }
              sections[sectionKey].placeholders.push(placeholder.key)
            }
          }
        })
      }
      
      if (element.elements) {
        this.scanElement(element.elements, placeholders, sections, level + 1)
      }
    })
  }
  
  /**
   * Cria mapeamento inteligente de placeholder baseado no contexto
   */
  private createPlaceholderMapping(
    key: string, 
    field: string, 
    widgetType: string,
    originalText: string
  ): PlaceholderMapping {
    let type: PlaceholderMapping['type'] = 'text'
    let context = `${widgetType} ${field}`
    let validation: RegExp | undefined
    
    // Análise semântica do contexto
    if (key.includes('PHONE') || key.includes('TELEFONE')) {
      type = 'phone'
      validation = /^\(\d{2}\)\s*\d{4,5}-?\d{4}$/
      context = 'Número de telefone para contato'
    } else if (key.includes('EMAIL')) {
      type = 'email'
      validation = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      context = 'Endereço de email para contato'
    } else if (key.includes('CTA') || key.includes('BUTTON') || key.includes('BOTAO')) {
      type = 'cta'
      context = 'Texto para chamada de ação (botão)'
    } else if (key.includes('URL') || key.includes('LINK')) {
      type = 'url'
      validation = /^https?:\/\/.+/
      context = 'URL ou link'
    } else if (key.includes('IMAGE') || key.includes('IMAGEM')) {
      type = 'image'
      context = 'URL de imagem'
    } else if (key.includes('LIST') || key.includes('LISTA')) {
      type = 'list'
      context = 'Lista de itens (separados por vírgula)'
    }
    
    // Contexto específico baseado no widget
    if (widgetType === 'heading') {
      context = 'Título principal da seção'
    } else if (widgetType === 'text-editor') {
      context = 'Conteúdo de texto longo'
    } else if (widgetType === 'button') {
      context = 'Texto do botão de ação'
      type = 'cta'
    }
    
    return {
      key,
      type,
      context,
      required: this.isRequiredField(key, field, widgetType),
      fallback: this.getFallback(key, type),
      validation
    }
  }
  
  private isRequiredField(key: string, field: string, widgetType: string): boolean {
    // Campos críticos que sempre precisam ser preenchidos
    const criticalKeys = ['BUSINESS_NAME', 'MAIN_HEADLINE', 'PRIMARY_CTA']
    const criticalFields = ['title', 'button_text']
    
    return criticalKeys.some(ck => key.includes(ck)) || 
           (criticalFields.includes(field) && widgetType === 'heading')
  }
  
  private getFallback(key: string, type: PlaceholderMapping['type']): string {
    const fallbacks: { [key: string]: string } = {
      'text': 'Conteúdo personalizado',
      'phone': '(11) 99999-9999',
      'email': 'contato@empresa.com.br',
      'cta': 'Entre em Contato',
      'url': 'https://exemplo.com.br',
      'list': 'Item 1, Item 2, Item 3'
    }
    
    // Fallbacks específicos por contexto
    if (key.includes('BUSINESS_NAME')) return 'Sua Empresa'
    if (key.includes('SPECIALTY') || key.includes('ESPECIALIDADE')) return 'Especialista'
    if (key.includes('SERVICE')) return 'Nossos Serviços'
    
    return fallbacks[type] || 'Conteúdo'
  }
  
  private deduplicatePlaceholders(placeholders: PlaceholderMapping[]): PlaceholderMapping[] {
    const seen = new Set()
    return placeholders.filter(p => {
      if (seen.has(p.key)) return false
      seen.add(p.key)
      return true
    })
  }
  
  /**
   * Substitui placeholders no template com valores reais
   */
  replacePlaceholders(template: any, values: Record<string, any>): any {
    const templateCopy = JSON.parse(JSON.stringify(template))
    
    this.replaceInElement(templateCopy.content, values)
    
    return templateCopy
  }
  
  private replaceInElement(elements: any[], values: Record<string, any>) {
    elements.forEach(element => {
      if (element.settings) {
        const textFields = ['title', 'text', 'editor', 'content', 'caption', 'description', 'button_text']
        
        textFields.forEach(field => {
          if (element.settings[field] && typeof element.settings[field] === 'string') {
            element.settings[field] = element.settings[field].replace(
              this.placeholderPattern,
              (match: string, key: string) => {
                return values[key] || match // Mantém placeholder se valor não existir
              }
            )
          }
        })
      }
      
      if (element.elements) {
        this.replaceInElement(element.elements, values)
      }
    })
  }
}