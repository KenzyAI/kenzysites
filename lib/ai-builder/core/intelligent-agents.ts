// Agentes Inteligentes para Análise e Modificação de Conteúdo

import type { BusinessInfo } from '../types'

// Missing type definition
export interface PlaceholderMapping {
  [key: string]: string
}

export interface ContentAnalysis {
  intent: string
  sentiment: 'professional' | 'casual' | 'urgent' | 'friendly'
  businessContext: string[]
  suggestedReplacements: Array<{
    original: string
    suggested: string
    confidence: number
    reasoning: string
  }>
}

export interface AgentContext {
  businessInfo: BusinessInfo
  templateContext: string
  sectionType: 'hero' | 'about' | 'services' | 'testimonials' | 'contact' | 'cta'
  existingContent: string
}

export class SemanticAnalysisAgent {
  private businessKeywords: Map<string, string[]> = new Map([
    ['medical', ['saúde', 'médico', 'clínica', 'tratamento', 'consulta', 'paciente', 'especialista']],
    ['restaurant', ['comida', 'prato', 'sabor', 'chef', 'restaurante', 'cardápio', 'delivery']],
    ['business', ['empresa', 'solução', 'serviço', 'cliente', 'negócio', 'profissional', 'qualidade']],
    ['technology', ['tecnologia', 'sistema', 'software', 'digital', 'inovação', 'desenvolvimento']],
    ['beauty', ['beleza', 'estética', 'tratamento', 'pele', 'cuidado', 'aparência', 'bem-estar']]
  ])
  
  /**
   * Analisa o conteúdo existente e sugere melhorias contextuais
   */
  analyzeContent(content: string, context: AgentContext): ContentAnalysis {
    const businessType = this.detectBusinessType(context.businessInfo)
    const keywords = this.businessKeywords.get(businessType) || []
    
    return {
      intent: this.detectIntent(content, context.sectionType),
      sentiment: this.analyzeSentiment(content),
      businessContext: this.extractBusinessContext(content, keywords),
      suggestedReplacements: this.generateReplacements(content, context)
    }
  }
  
  private detectBusinessType(businessInfo: BusinessInfo): string {
    const industry = businessInfo.industry?.toLowerCase() || ''
    const description = businessInfo.description?.toLowerCase() || ''
    const combined = `${industry} ${description} ${businessInfo.type}`
    
    if (combined.includes('medic') || combined.includes('saúde') || combined.includes('dermatolog')) {
      return 'medical'
    }
    if (combined.includes('restaurant') || combined.includes('food') || combined.includes('comida')) {
      return 'restaurant'
    }
    if (combined.includes('tech') || combined.includes('software') || combined.includes('digital')) {
      return 'technology'
    }
    if (combined.includes('beauty') || combined.includes('estetic') || combined.includes('beleza')) {
      return 'beauty'
    }
    
    return 'business'
  }
  
  private detectIntent(content: string, sectionType: string): string {
    const intentMap: { [key: string]: string } = {
      'hero': 'Capturar atenção e apresentar valor principal',
      'about': 'Construir confiança e credibilidade',
      'services': 'Detalhar ofertas e benefícios',
      'testimonials': 'Prova social e validação',
      'contact': 'Facilitar contato e conversão',
      'cta': 'Incentivar ação específica'
    }
    
    return intentMap[sectionType] || 'Informar e engajar'
  }
  
  private analyzeSentiment(content: string): ContentAnalysis['sentiment'] {
    const professionalWords = ['especialista', 'qualidade', 'experiência', 'profissional']
    const casualWords = ['legal', 'show', 'massa', 'bacana']
    const urgentWords = ['agora', 'hoje', 'limitado', 'urgente']
    const friendlyWords = ['querido', 'amigo', 'família', 'cuidado']
    
    const lower = content.toLowerCase()
    
    if (professionalWords.some(w => lower.includes(w))) return 'professional'
    if (urgentWords.some(w => lower.includes(w))) return 'urgent'
    if (friendlyWords.some(w => lower.includes(w))) return 'friendly'
    if (casualWords.some(w => lower.includes(w))) return 'casual'
    
    return 'professional'
  }
  
  private extractBusinessContext(content: string, keywords: string[]): string[] {
    const found: string[] = []
    const lower = content.toLowerCase()
    
    keywords.forEach(keyword => {
      if (lower.includes(keyword)) {
        found.push(keyword)
      }
    })
    
    return found
  }
  
  private generateReplacements(content: string, context: AgentContext): ContentAnalysis['suggestedReplacements'] {
    const replacements: ContentAnalysis['suggestedReplacements'] = []
    const businessInfo = context.businessInfo
    
    // Substituições de nome genérico
    const genericNames = ['Dr. João', 'Dra. Maria', 'Empresa', 'Negócio', 'Profissional']
    genericNames.forEach(generic => {
      if (content.includes(generic)) {
        replacements.push({
          original: generic,
          suggested: businessInfo.name,
          confidence: 0.95,
          reasoning: 'Substituição de nome genérico pelo nome real do negócio'
        })
      }
    })
    
    // Substituições de especialidade
    if (businessInfo.industry && context.sectionType === 'hero') {
      const specialtyReplacements = this.getSpecialtyReplacements(businessInfo.industry)
      specialtyReplacements.forEach(replacement => {
        if (content.toLowerCase().includes(replacement.pattern)) {
          replacements.push({
            original: replacement.pattern,
            suggested: replacement.replacement,
            confidence: 0.85,
            reasoning: 'Ajuste de especialidade baseado no setor do negócio'
          })
        }
      })
    }
    
    // Substituições de serviços
    if (businessInfo.services && businessInfo.services.length > 0) {
      const serviceKeywords = ['serviços', 'oferecemos', 'especialidades']
      serviceKeywords.forEach(keyword => {
        if (content.toLowerCase().includes(keyword)) {
          replacements.push({
            original: `nossos ${keyword}`,
            suggested: `nossos serviços: ${businessInfo.services?.slice(0, 3).join(', ') || 'diversos serviços'}`,
            confidence: 0.8,
            reasoning: 'Inclusão de serviços específicos do negócio'
          })
        }
      })
    }
    
    return replacements
  }
  
  private getSpecialtyReplacements(industry: string): Array<{pattern: string, replacement: string}> {
    const replacements: { [key: string]: Array<{pattern: string, replacement: string}> } = {
      'healthcare': [
        { pattern: 'especialista', replacement: 'especialista em saúde' },
        { pattern: 'profissional', replacement: 'profissional da saúde' }
      ],
      'technology': [
        { pattern: 'especialista', replacement: 'especialista em tecnologia' },
        { pattern: 'soluções', replacement: 'soluções tecnológicas' }
      ],
      'food-service': [
        { pattern: 'especialista', replacement: 'especialista culinário' },
        { pattern: 'experiência', replacement: 'experiência gastronômica' }
      ]
    }
    
    return replacements[industry] || []
  }
}

export class ContentGenerationAgent {
  /**
   * Gera conteúdo contextual baseado no negócio e análise semântica
   */
  async generateContextualContent(
    placeholderKey: string, 
    mapping: PlaceholderMapping,
    businessInfo: BusinessInfo,
    analysis: ContentAnalysis
  ): Promise<string> {
    // Por enquanto, geração baseada em regras
    // TODO: Integrar com API da OpenAI/Claude
    
    const generators: { [key: string]: () => string } = {
      'BUSINESS_NAME': () => businessInfo.name,
      'BUSINESS_SPECIALTY': () => this.generateSpecialty(businessInfo),
      'MAIN_HEADLINE': () => this.generateHeadline(businessInfo, analysis),
      'MAIN_DESCRIPTION': () => this.generateDescription(businessInfo),
      'PRIMARY_CTA': () => this.generateCTA(businessInfo, analysis),
      'PHONE': () => businessInfo.phone || '(11) 99999-9999',
      'EMAIL': () => businessInfo.email || `contato@${businessInfo.name.toLowerCase().replace(/\s+/g, '')}.com.br`,
      'SERVICES_LIST': () => businessInfo.services?.join(', ') || 'Nossos serviços especializados'
    }
    
    const generator = generators[placeholderKey]
    if (generator) {
      return generator()
    }
    
    // Geração contextual baseada no tipo
    return this.generateByType(mapping, businessInfo, analysis)
  }
  
  private generateSpecialty(businessInfo: BusinessInfo): string {
    const specialtyMap: { [key: string]: string } = {
      'healthcare': 'Especialista em Saúde',
      'dermatology': 'Dermatologia Avançada',
      'technology': 'Soluções Tecnológicas',
      'restaurant': 'Experiência Gastronômica',
      'beauty': 'Cuidados Estéticos'
    }
    
    const industry = businessInfo.industry?.toLowerCase() || ''
    const description = businessInfo.description?.toLowerCase() || ''
    
    if (description.includes('dermatolog')) return 'Dermatologia Avançada'
    if (industry.includes('tech')) return 'Soluções Tecnológicas'
    if (industry.includes('food')) return 'Experiência Gastronômica'
    
    return specialtyMap[industry] || 'Especialista Professional'
  }
  
  private generateHeadline(businessInfo: BusinessInfo, analysis: ContentAnalysis): string {
    const templates = {
      'medical': [
        `Cuidados Especializados com ${businessInfo.name}`,
        `Sua Saúde em Boas Mãos - ${businessInfo.name}`,
        `${businessInfo.name} - Excelência em Cuidados`
      ],
      'business': [
        `Transforme Seu Negócio com ${businessInfo.name}`,
        `${businessInfo.name} - Soluções que Funcionam`,
        `Resultados Excepcionais com ${businessInfo.name}`
      ],
      'restaurant': [
        `Sabores Únicos no ${businessInfo.name}`,
        `${businessInfo.name} - Experiência Gastronômica`,
        `Tradição e Sabor no ${businessInfo.name}`
      ]
    }
    
    const businessType = this.detectBusinessTypeFromAnalysis(analysis)
    const options = templates[businessType as keyof typeof templates] || templates['business']
    
    return options[Math.floor(Math.random() * options.length)]
  }
  
  private generateDescription(businessInfo: BusinessInfo): string {
    const base = businessInfo.description || `${businessInfo.name} oferece serviços especializados`
    
    if (businessInfo.services && businessInfo.services.length > 0) {
      return `${base}. Especializado em: ${businessInfo.services.slice(0, 3).join(', ')}.`
    }
    
    return `${base} com foco na excelência e satisfação do cliente.`
  }
  
  private generateCTA(businessInfo: BusinessInfo, analysis: ContentAnalysis): string {
    const ctasByType: { [key: string]: string[] } = {
      'medical': ['Agendar Consulta', 'Marcar Avaliação', 'Falar com Especialista'],
      'business': ['Solicitar Proposta', 'Falar com Consultor', 'Conhecer Soluções'],
      'restaurant': ['Fazer Reserva', 'Ver Cardápio', 'Pedir Delivery']
    }
    
    const businessType = this.detectBusinessTypeFromAnalysis(analysis)
    const options = ctasByType[businessType] || ['Entre em Contato', 'Saiba Mais', 'Fale Conosco']
    
    return options[0] // Usar a primeira opção como padrão
  }
  
  private generateByType(mapping: PlaceholderMapping, businessInfo: BusinessInfo, analysis: ContentAnalysis): string {
    switch (mapping.type) {
      case 'cta':
        return this.generateCTA(businessInfo, analysis)
      case 'phone':
        return businessInfo.phone || mapping.fallback || '(11) 99999-9999'
      case 'email':
        return businessInfo.email || mapping.fallback || 'contato@empresa.com.br'
      case 'list':
        return businessInfo.services?.join(', ') || mapping.fallback || 'Serviço 1, Serviço 2'
      default:
        return mapping.fallback || 'Conteúdo personalizado'
    }
  }
  
  private detectBusinessTypeFromAnalysis(analysis: ContentAnalysis): string {
    const context = analysis.businessContext.join(' ')
    
    if (context.includes('médico') || context.includes('saúde')) return 'medical'
    if (context.includes('comida') || context.includes('restaurante')) return 'restaurant'
    
    return 'business'
  }
}