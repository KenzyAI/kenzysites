// AI Content Generator - Generates personalized content for websites

import type { 
  BusinessInfo, 
  GeneratedContent, 
  ContentGenerationContext,
  AIBuilderConfig 
} from '../types'

interface AIProvider {
  generateText(prompt: string, options?: { maxTokens?: number; temperature?: number }): Promise<string>
}

export class AIContentGenerator {
  private config: AIBuilderConfig
  private aiProvider?: AIProvider

  constructor(config: AIBuilderConfig) {
    this.config = config
    this.initializeAI()
  }

  /**
   * Initialize AI provider (OpenAI/Claude)
   */
  private initializeAI(): void {
    // TODO: Initialize actual AI provider when API keys are available
    // For now, we'll use mock responses
    this.aiProvider = {
      generateText: this.mockAIGeneration.bind(this)
    }
  }

  /**
   * Mock AI generation for development/testing
   */
  private async mockAIGeneration(prompt: string): Promise<string> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Simple mock responses based on prompt content
    if (prompt.includes('headline') || prompt.includes('título')) {
      return 'Transforme Sua Visão em Realidade'
    }
    
    if (prompt.includes('tagline') || prompt.includes('slogan')) {
      return 'Soluções inovadoras para o seu sucesso'
    }
    
    if (prompt.includes('about') || prompt.includes('sobre')) {
      return 'Somos uma empresa dedicada a fornecer soluções excepcionais que superam as expectativas dos nossos clientes. Com anos de experiência no mercado, nossa equipe combina expertise técnica com atendimento personalizado para entregar resultados que realmente importam.'
    }
    
    if (prompt.includes('service') || prompt.includes('serviço')) {
      return 'Oferecemos serviços especializados com foco na qualidade e satisfação do cliente.'
    }
    
    if (prompt.includes('testimonial') || prompt.includes('depoimento')) {
      return 'Excelente trabalho! Superaram todas as nossas expectativas e entregaram um resultado incrível.'
    }
    
    if (prompt.includes('cta') || prompt.includes('call to action')) {
      return 'Entre em Contato Agora'
    }
    
    // Default response
    return 'Conteúdo personalizado gerado para atender às suas necessidades específicas.'
  }

  /**
   * Generate complete content for a business
   */
  async generateBusinessContent(businessInfo: BusinessInfo): Promise<GeneratedContent> {
    const businessType = businessInfo.type
    const businessName = businessInfo.name
    const industry = businessInfo.industry || businessType
    
    // Generate main content pieces
    const [
      headline,
      tagline,
      description,
      about,
      features,
      services,
      testimonials,
      cta
    ] = await Promise.all([
      this.generateHeadline(businessInfo),
      this.generateTagline(businessInfo),
      this.generateDescription(businessInfo),
      this.generateAbout(businessInfo),
      this.generateFeatures(businessInfo),
      this.generateServices(businessInfo),
      this.generateTestimonials(businessInfo),
      this.generateCTA(businessInfo)
    ])

    return {
      headline,
      tagline,
      description,
      about,
      features,
      services,
      testimonials,
      cta,
      contact: {
        phone: businessInfo.phone,
        email: businessInfo.email,
        address: businessInfo.location
      },
      images: await this.generateImageSelections(businessInfo)
    }
  }

  /**
   * Generate headline for business
   */
  private async generateHeadline(businessInfo: BusinessInfo): Promise<string> {
    const prompt = this.buildPrompt('headline', businessInfo, {
      context: `Create a compelling headline for ${businessInfo.name}, a ${businessInfo.type} business`,
      requirements: [
        'Maximum 60 characters',
        'Engaging and professional',
        'Reflects the business value proposition',
        'Industry-appropriate tone'
      ]
    })

    return await this.aiProvider!.generateText(prompt)
  }

  /**
   * Generate tagline/slogan
   */
  private async generateTagline(businessInfo: BusinessInfo): Promise<string> {
    const prompt = this.buildPrompt('tagline', businessInfo, {
      context: `Create a memorable tagline for ${businessInfo.name}`,
      requirements: [
        'Short and catchy',
        'Complements the business mission',
        'Easy to remember',
        'Professional yet approachable'
      ]
    })

    return await this.aiProvider!.generateText(prompt)
  }

  /**
   * Generate business description
   */
  private async generateDescription(businessInfo: BusinessInfo): Promise<string> {
    const prompt = this.buildPrompt('description', businessInfo, {
      context: `Write a compelling description for ${businessInfo.name}`,
      requirements: [
        '2-3 sentences',
        'Highlights main services/products',
        'Appeals to target audience',
        'Professional and engaging'
      ]
    })

    return await this.aiProvider!.generateText(prompt)
  }

  /**
   * Generate about section
   */
  private async generateAbout(businessInfo: BusinessInfo): Promise<string> {
    const prompt = this.buildPrompt('about', businessInfo, {
      context: `Write an 'About Us' section for ${businessInfo.name}`,
      requirements: [
        '3-4 sentences',
        'Tells the company story',
        'Builds trust and credibility',
        'Mentions experience and expertise'
      ]
    })

    return await this.aiProvider!.generateText(prompt)
  }

  /**
   * Generate key features/benefits
   */
  private async generateFeatures(businessInfo: BusinessInfo): Promise<string[]> {
    const prompt = this.buildPrompt('features', businessInfo, {
      context: `List 4-6 key features/benefits of ${businessInfo.name}`,
      requirements: [
        'Each feature in 3-5 words',
        'Focus on customer benefits',
        'Industry-relevant',
        'Differentiating factors'
      ]
    })

    const response = await this.aiProvider!.generateText(prompt)
    
    // Parse response into array (assuming comma-separated or line-separated)
    return response.split(/[,\n]/).map(feature => feature.trim()).filter(Boolean).slice(0, 6)
  }

  /**
   * Generate services
   */
  private async generateServices(businessInfo: BusinessInfo): Promise<Array<{
    title: string
    description: string
    icon?: string
  }>> {
    const servicesCount = businessInfo.services?.length || 3
    const services = []

    for (let i = 0; i < Math.min(servicesCount, 6); i++) {
      const serviceName = businessInfo.services?.[i] || `Service ${i + 1}`
      
      const prompt = this.buildPrompt('service', businessInfo, {
        context: `Create content for the service "${serviceName}" offered by ${businessInfo.name}`,
        requirements: [
          'Service title (3-5 words)',
          'Service description (1-2 sentences)',
          'Professional and benefit-focused'
        ]
      })

      const response = await this.aiProvider!.generateText(prompt)
      
      services.push({
        title: serviceName,
        description: response,
        icon: this.getServiceIcon(serviceName, businessInfo.type)
      })
    }

    return services
  }

  /**
   * Generate testimonials
   */
  private async generateTestimonials(businessInfo: BusinessInfo): Promise<Array<{
    text: string
    author: string
    role: string
  }>> {
    const testimonials = []

    for (let i = 0; i < 3; i++) {
      const prompt = this.buildPrompt('testimonial', businessInfo, {
        context: `Create a realistic testimonial for ${businessInfo.name}`,
        requirements: [
          '2-3 sentences',
          'Specific and credible',
          'Highlights business strengths',
          'Natural and authentic tone'
        ]
      })

      const text = await this.aiProvider!.generateText(prompt)
      
      testimonials.push({
        text,
        author: this.generateCustomerName(businessInfo.type),
        role: this.generateCustomerRole(businessInfo.type)
      })
    }

    return testimonials
  }

  /**
   * Generate call-to-action
   */
  private async generateCTA(businessInfo: BusinessInfo): Promise<{
    primary: string
    secondary?: string
  }> {
    const prompt = this.buildPrompt('cta', businessInfo, {
      context: `Create compelling call-to-action buttons for ${businessInfo.name}`,
      requirements: [
        'Primary CTA: 2-4 words, action-oriented',
        'Secondary CTA: alternative action',
        'Urgent but not pushy',
        'Industry-appropriate'
      ]
    })

    const response = await this.aiProvider!.generateText(prompt)
    
    // Parse primary and secondary CTAs
    const lines = response.split('\n').filter(Boolean)
    
    return {
      primary: lines[0]?.trim() || 'Entre em Contato',
      secondary: lines[1]?.trim() || 'Saiba Mais'
    }
  }

  /**
   * Generate image selection keywords
   */
  private async generateImageSelections(businessInfo: BusinessInfo): Promise<{
    hero: string[]
    gallery: string[]
    team: string[]
    services: string[]
  }> {
    // Generate keywords based on business type and industry
    const baseKeywords = this.getBusinessKeywords(businessInfo)
    
    return {
      hero: [`${businessInfo.type}`, ...baseKeywords.slice(0, 3)],
      gallery: [...baseKeywords, 'professional', 'quality'],
      team: ['team', 'professional', 'office', businessInfo.type],
      services: businessInfo.services?.slice(0, 4) || baseKeywords.slice(0, 4)
    }
  }

  /**
   * Generate content for specific section
   */
  async generateSectionContent(context: ContentGenerationContext): Promise<string> {
    const prompt = this.buildPrompt('section', context.businessInfo, {
      context: `Generate content for ${context.sectionType} section`,
      requirements: [
        `Target length: ${context.targetLength || 'medium'}`,
        `Tone: ${context.tone || 'professional'}`,
        'Relevant to business and section type',
        'Engaging and well-written'
      ],
      sectionType: context.sectionType,
      existingContent: context.existingContent
    })

    return await this.aiProvider!.generateText(prompt)
  }

  /**
   * Build AI prompt with context and requirements
   */
  private buildPrompt(
    type: string, 
    businessInfo: BusinessInfo, 
    options: {
      context: string
      requirements: string[]
      sectionType?: string
      existingContent?: string
    }
  ): string {
    const { context, requirements, sectionType, existingContent } = options
    
    let prompt = `${context}\n\n`
    
    prompt += `Business Information:\n`
    prompt += `- Name: ${businessInfo.name}\n`
    prompt += `- Type: ${businessInfo.type}\n`
    prompt += `- Industry: ${businessInfo.industry || businessInfo.type}\n`
    prompt += `- Description: ${businessInfo.description}\n`
    
    if (businessInfo.services?.length) {
      prompt += `- Services: ${businessInfo.services.join(', ')}\n`
    }
    
    if (businessInfo.targetAudience) {
      prompt += `- Target Audience: ${businessInfo.targetAudience}\n`
    }
    
    if (businessInfo.location) {
      prompt += `- Location: ${businessInfo.location}\n`
    }
    
    prompt += `\nRequirements:\n`
    requirements.forEach(req => {
      prompt += `- ${req}\n`
    })
    
    if (sectionType) {
      prompt += `\nSection Type: ${sectionType}\n`
    }
    
    if (existingContent) {
      prompt += `\nExisting Content to Improve/Replace:\n"${existingContent}"\n`
    }
    
    prompt += `\nGenerate content in Portuguese (pt-BR) unless specified otherwise.\n`
    prompt += `Focus on the business value proposition and customer benefits.\n`
    
    return prompt
  }

  /**
   * Get appropriate icon for service
   */
  private getServiceIcon(serviceName: string, businessType: string): string {
    const iconMap: Record<string, string> = {
      'consulting': 'fas fa-lightbulb',
      'development': 'fas fa-code',
      'design': 'fas fa-palette',
      'marketing': 'fas fa-megaphone',
      'support': 'fas fa-headset',
      'training': 'fas fa-graduation-cap',
      'maintenance': 'fas fa-tools',
      'restaurant': 'fas fa-utensils',
      'delivery': 'fas fa-truck',
      'catering': 'fas fa-wine-glass'
    }
    
    const serviceLower = serviceName.toLowerCase()
    
    for (const [key, icon] of Object.entries(iconMap)) {
      if (serviceLower.includes(key)) {
        return icon
      }
    }
    
    // Default icons by business type
    const typeIcons: Record<string, string> = {
      'restaurant': 'fas fa-utensils',
      'business': 'fas fa-briefcase',
      'portfolio': 'fas fa-images',
      'ecommerce': 'fas fa-shopping-cart',
      'blog': 'fas fa-pen',
      'landing': 'fas fa-rocket'
    }
    
    return typeIcons[businessType] || 'fas fa-star'
  }

  /**
   * Generate realistic customer names
   */
  private generateCustomerName(businessType: string): string {
    const names = [
      'Ana Silva', 'João Santos', 'Maria Oliveira', 'Pedro Costa',
      'Carla Ferreira', 'Lucas Pereira', 'Fernanda Lima', 'Ricardo Almeida',
      'Juliana Rocha', 'Marcelo Souza', 'Patricia Mendes', 'André Barbosa'
    ]
    
    return names[Math.floor(Math.random() * names.length)]
  }

  /**
   * Generate appropriate customer roles
   */
  private generateCustomerRole(businessType: string): string {
    const rolesByType: Record<string, string[]> = {
      'restaurant': ['Cliente Fiel', 'Food Blogger', 'Empresária Local'],
      'business': ['CEO', 'Gerente de Projetos', 'Empresário', 'Diretora'],
      'portfolio': ['Cliente', 'Empresário', 'Criativo'],
      'ecommerce': ['Compradora Frequente', 'Cliente VIP', 'Usuário'],
      'blog': ['Leitor Assíduo', 'Profissional da Área', 'Seguidor'],
      'landing': ['Usuário', 'Cliente', 'Visitante']
    }
    
    const roles = rolesByType[businessType] || ['Cliente', 'Usuário', 'Parceiro']
    return roles[Math.floor(Math.random() * roles.length)]
  }

  /**
   * Get keywords based on business info
   */
  private getBusinessKeywords(businessInfo: BusinessInfo): string[] {
    const keywordsByType: Record<string, string[]> = {
      'restaurant': ['food', 'dining', 'chef', 'cuisine', 'meal', 'restaurant'],
      'business': ['professional', 'service', 'team', 'office', 'corporate', 'success'],
      'portfolio': ['creative', 'design', 'art', 'work', 'portfolio', 'project'],
      'ecommerce': ['product', 'shop', 'store', 'commerce', 'retail', 'shopping'],
      'blog': ['writing', 'content', 'blog', 'article', 'information', 'knowledge'],
      'landing': ['service', 'solution', 'product', 'business', 'professional', 'quality']
    }
    
    return keywordsByType[businessInfo.type] || ['business', 'professional', 'service', 'quality']
  }
}