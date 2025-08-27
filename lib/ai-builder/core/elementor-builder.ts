// Elementor AI Builder - Main orchestrator for AI-powered website generation

import type {
  BusinessInfo,
  ElementorTemplate,
  GeneratedContent,
  SiteGenerationRequest,
  SiteGenerationResponse,
  TemplateMatch,
  AIBuilderConfig,
  GenerationProgress,
  SelectedImage
} from '../types'

import { ElementorTemplateParser } from './template-parser'
import { AIContentGenerator } from './content-generator'
import { HostedWordPressClient } from '../../wordpress/hosted-client'
import { WordPressColorManager, type ColorScheme } from '../../wordpress/color-manager'

export class ElementorAIBuilder {
  private templateParser: ElementorTemplateParser
  private contentGenerator: AIContentGenerator
  private colorManager: WordPressColorManager
  private wpClient?: HostedWordPressClient
  private config: AIBuilderConfig
  private templates: ElementorTemplate[] = []

  constructor(config: AIBuilderConfig, wpClient?: HostedWordPressClient) {
    this.config = config
    this.wpClient = wpClient
    this.templateParser = new ElementorTemplateParser()
    this.contentGenerator = new AIContentGenerator(config)
    this.colorManager = new WordPressColorManager(wpClient)
  }

  /**
   * Load template library
   */
  async loadTemplates(templates: ElementorTemplate[] | string[]): Promise<void> {
    if (typeof templates[0] === 'string') {
      // Load from JSON files
      this.templates = await this.loadTemplatesFromFiles(templates as string[])
    } else {
      // Use provided template objects
      this.templates = templates as ElementorTemplate[]
    }
  }

  /**
   * Build complete website from business description
   */
  async buildFromPrompt(
    request: SiteGenerationRequest,
    onProgress?: (progress: GenerationProgress) => void
  ): Promise<SiteGenerationResponse> {
    try {
      // Stage 1: Analyze business information
      onProgress?.({
        stage: 'analyzing',
        progress: 10,
        message: 'Analisando informações do negócio...'
      })

      const businessInfo = this.enhanceBusinessInfo(request.businessInfo)

      // Stage 2: Select appropriate template
      onProgress?.({
        stage: 'selecting_template',
        progress: 25,
        message: 'Selecionando template ideal...'
      })

      const selectedTemplate = request.templateId 
        ? await this.getTemplateById(request.templateId)
        : await this.selectBestTemplate(businessInfo)

      if (!selectedTemplate) {
        throw new Error('No suitable template found')
      }

      // Stage 3: Generate personalized content
      onProgress?.({
        stage: 'generating_content',
        progress: 50,
        message: 'Gerando conteúdo personalizado...',
        details: { template_selected: selectedTemplate.title }
      })

      const generatedContent = await this.contentGenerator.generateBusinessContent(businessInfo)

      // Stage 4: Customize template with generated content
      onProgress?.({
        stage: 'customizing',
        progress: 75,
        message: 'Personalizando template...',
        details: { 
          template_selected: selectedTemplate.title,
          content_generated: true 
        }
      })

      // Stage 4.5: Generate AI-powered color scheme
      onProgress?.({
        stage: 'customizing',
        progress: 80,
        message: 'Gerando esquema de cores...',
        details: { 
          template_selected: selectedTemplate.title,
          content_generated: true
        }
      })

      const colorScheme = await this.colorManager.generateColorScheme({
        industry: businessInfo.type as any,
        mood: request.preferences?.style === 'corporate' ? 'professional' : 
              request.preferences?.style === 'creative' ? 'creative' : 'professional',
        brandColors: request.customization?.primaryColor ? [request.customization.primaryColor] : undefined
      })

      const customizedTemplate = await this.customizeTemplate(
        selectedTemplate,
        generatedContent,
        businessInfo,
        request.preferences,
        request.customization,
        colorScheme
      )

      // Stage 5: Deploy to WordPress (if client available)
      if (this.wpClient) {
        onProgress?.({
          stage: 'deploying',
          progress: 90,
          message: 'Publicando no WordPress...',
          details: { 
            template_selected: selectedTemplate.title,
            content_generated: true,
            deployment_started: true
          }
        })

        const deployResult = await this.deployToWordPress(customizedTemplate, businessInfo)
        
        onProgress?.({
          stage: 'completed',
          progress: 100,
          message: 'Site criado com sucesso!'
        })

        return {
          success: true,
          ...deployResult,
          template_used: selectedTemplate.title,
          generation_time: Date.now()
        }
      }

      // Return template data without deployment
      onProgress?.({
        stage: 'completed',
        progress: 100,
        message: 'Template personalizado pronto!'
      })

      return {
        success: true,
        siteId: 'template-' + Date.now(),
        template_used: selectedTemplate.title,
        generation_time: Date.now()
      }

    } catch (error) {
      onProgress?.({
        stage: 'error',
        progress: 0,
        message: 'Erro na geração do site',
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      })

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  /**
   * Select best template for business
   */
  async selectBestTemplate(businessInfo: BusinessInfo): Promise<ElementorTemplate | null> {
    if (this.templates.length === 0) {
      throw new Error('No templates loaded')
    }

    const matches = this.templates.map(template => ({
      template,
      score: this.calculateTemplateScore(template, businessInfo),
      reasons: this.getMatchReasons(template, businessInfo)
    }))

    // Sort by score (highest first)
    matches.sort((a, b) => b.score - a.score)

    return matches[0]?.template || null
  }

  /**
   * Calculate how well a template matches the business
   */
  private calculateTemplateScore(template: ElementorTemplate, businessInfo: BusinessInfo): number {
    let score = 0

    // Category match (highest weight)
    if (template.category.includes(businessInfo.type)) {
      score += 40
    }

    // Industry match
    if (businessInfo.industry && template.tags.some(tag => 
      tag.toLowerCase().includes(businessInfo.industry!.toLowerCase())
    )) {
      score += 30
    }

    // Service match
    if (businessInfo.services?.some(service =>
      template.tags.some(tag => tag.toLowerCase().includes(service.toLowerCase()))
    )) {
      score += 20
    }

    // Template complexity vs business needs
    const stats = this.templateParser.getTemplateStats(template)
    
    // Simple businesses prefer simpler templates
    if (businessInfo.type === 'landing' && stats.totalElements < 20) {
      score += 15
    }
    
    // Complex businesses can handle more complex templates
    if (['ecommerce', 'business'].includes(businessInfo.type) && stats.totalElements > 30) {
      score += 10
    }

    return score
  }

  /**
   * Get reasons why template matches business
   */
  private getMatchReasons(template: ElementorTemplate, businessInfo: BusinessInfo): string[] {
    const reasons: string[] = []

    if (template.category.includes(businessInfo.type)) {
      reasons.push(`Categoria '${businessInfo.type}' combinada`)
    }

    if (businessInfo.industry && template.tags.some(tag => 
      tag.toLowerCase().includes(businessInfo.industry!.toLowerCase())
    )) {
      reasons.push(`Setor '${businessInfo.industry}' relevante`)
    }

    const stats = this.templateParser.getTemplateStats(template)
    if (stats.imageElements > 5) {
      reasons.push('Rico em elementos visuais')
    }

    if (stats.textElements > 10) {
      reasons.push('Bom para conteúdo extenso')
    }

    return reasons
  }

  /**
   * Get template by ID
   */
  async getTemplateById(templateId: string): Promise<ElementorTemplate | null> {
    return this.templates.find(t => t.id === templateId) || null
  }

  /**
   * Customize template with generated content
   */
  private async customizeTemplate(
    template: ElementorTemplate,
    content: GeneratedContent,
    businessInfo: BusinessInfo,
    preferences?: SiteGenerationRequest['preferences'],
    customization?: SiteGenerationRequest['customization'],
    colorScheme?: ColorScheme
  ): Promise<ElementorTemplate> {
    // Clone template to avoid modifying original
    const customized = this.templateParser.clone(template)

    // Replace text content
    const textReplacements: Record<string, string> = {
      'company_name': businessInfo.name,
      'business_name': businessInfo.name,
      'headline': content.headline,
      'tagline': content.tagline || '',
      'description': content.description,
      'about': content.about,
      'phone': businessInfo.phone || '',
      'email': businessInfo.email || '',
      'address': businessInfo.location || '',
      'cta_primary': content.cta.primary,
      'cta_secondary': content.cta.secondary || '',
      
      // Common placeholders
      'Your Business Name': businessInfo.name,
      'Company Name': businessInfo.name,
      'Business Title': content.headline,
      'Your Tagline': content.tagline || content.description,
      'About Your Business': content.about,
      'Get Started': content.cta.primary,
      'Learn More': content.cta.secondary || 'Saiba Mais',
      'Contact Us': 'Entre em Contato'
    }

    this.templateParser.replaceTextContent(customized, textReplacements)

    // Replace services content
    if (content.services.length > 0) {
      const servicesElements = this.templateParser.findElements(customized, {
        widgetType: 'text-editor'
      })

      // TODO: Implement more sophisticated service replacement
      // For now, we'll use the text replacement above
    }

    // Apply AI-generated color scheme
    if (colorScheme) {
      // Update template elements with new colors (for elements not using Global Settings)
      this.templateParser.updateColors(customized, {
        primary: colorScheme.primary,
        secondary: colorScheme.secondary,
        accent: colorScheme.accent,
        text: colorScheme.text,
        background: colorScheme.background || '#ffffff'
      })
      
      // Store color scheme for WordPress deployment
      customized.colorScheme = colorScheme
    }

    // Replace images (mock implementation)
    const imageReplacements = await this.generateImageReplacements(content.images)
    this.templateParser.replaceImages(customized, imageReplacements)

    return customized
  }

  /**
   * Generate color scheme based on preferences
   */
  private generateColorScheme(
    colorScheme?: string,
    customization?: { primaryColor?: string; secondaryColor?: string }
  ): Record<string, string> {
    const schemes = {
      light: {
        primary: '#007cba',
        secondary: '#005a87',
        background: '#ffffff',
        text: '#333333'
      },
      dark: {
        primary: '#00a0d2',
        secondary: '#0073aa',
        background: '#1a1a1a',
        text: '#ffffff'
      },
      colorful: {
        primary: '#e74c3c',
        secondary: '#3498db',
        background: '#ffffff',
        text: '#2c3e50'
      },
      minimal: {
        primary: '#666666',
        secondary: '#999999',
        background: '#ffffff',
        text: '#333333'
      }
    }

    const baseScheme = schemes[colorScheme as keyof typeof schemes] || schemes.light

    // Apply custom colors if provided
    return {
      ...baseScheme,
      primary: customization?.primaryColor || baseScheme.primary,
      secondary: customization?.secondaryColor || baseScheme.secondary
    }
  }

  /**
   * Generate image replacements (mock implementation)
   */
  private async generateImageReplacements(imageSelections: GeneratedContent['images']): Promise<Record<string, { url: string; alt?: string }>> {
    // TODO: Integrate with Unsplash/Pexels API
    // For now, return placeholder images
    
    const placeholderBase = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43'
    
    return {
      'hero-image': {
        url: `${placeholderBase}?w=1920&h=1080&fit=crop`,
        alt: 'Hero Image'
      },
      'about-image': {
        url: `${placeholderBase}?w=800&h=600&fit=crop`,
        alt: 'About Us'
      },
      'service-image': {
        url: `${placeholderBase}?w=600&h=400&fit=crop`,
        alt: 'Our Services'
      }
    }
  }

  /**
   * Deploy customized template to WordPress
   */
  private async deployToWordPress(
    template: ElementorTemplate,
    businessInfo: BusinessInfo
  ): Promise<{
    siteId?: string
    pages?: Array<{ id: number; title: string; url: string; type: string }>
    preview_url?: string
  }> {
    if (!this.wpClient) {
      throw new Error('WordPress client not configured')
    }

    try {
      // Create main page
      const importResult = await this.wpClient.importElementorTemplate({
        title: businessInfo.name,
        content: template.content,
        type: 'page',
        status: 'publish'
      })

      if (!importResult.success) {
        throw new Error(importResult.message)
      }

      // Apply color scheme to WordPress Global Settings (if available)
      if (template.colorScheme && this.wpClient) {
        try {
          await this.wpClient.applyColorScheme(1, template.colorScheme) // Site ID 1 for main site
        } catch (colorError) {
          console.warn('Cores não foram aplicadas ao Global Settings:', colorError)
          // Continue without colors - não é crítico
        }
      }

      return {
        siteId: importResult.pageId?.toString(),
        pages: [{
          id: importResult.pageId!,
          title: businessInfo.name,
          url: importResult.pageUrl!,
          type: 'page'
        }],
        preview_url: importResult.pageUrl
      }

    } catch (error) {
      throw new Error(`Failed to deploy to WordPress: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Enhance business information with inferred data
   */
  private enhanceBusinessInfo(businessInfo: BusinessInfo): BusinessInfo {
    return {
      ...businessInfo,
      industry: businessInfo.industry || this.inferIndustry(businessInfo),
      services: businessInfo.services || this.inferServices(businessInfo)
    }
  }

  /**
   * Infer industry from business type and description
   */
  private inferIndustry(businessInfo: BusinessInfo): string {
    const industryMap: Record<string, string> = {
      'restaurant': 'food-service',
      'business': 'professional-services',
      'portfolio': 'creative',
      'ecommerce': 'retail',
      'blog': 'content-media',
      'landing': 'marketing'
    }

    return industryMap[businessInfo.type] || 'general'
  }

  /**
   * Infer services from business type
   */
  private inferServices(businessInfo: BusinessInfo): string[] {
    const serviceMap: Record<string, string[]> = {
      'restaurant': ['Refeições', 'Delivery', 'Catering'],
      'business': ['Consultoria', 'Serviços', 'Suporte'],
      'portfolio': ['Design', 'Desenvolvimento', 'Criação'],
      'ecommerce': ['Produtos', 'Vendas', 'Suporte'],
      'blog': ['Conteúdo', 'Artigos', 'Notícias'],
      'landing': ['Produto', 'Serviço', 'Solução']
    }

    return serviceMap[businessInfo.type] || ['Serviços', 'Soluções', 'Suporte']
  }

  /**
   * Load templates from JSON files
   */
  private async loadTemplatesFromFiles(filePaths: string[]): Promise<ElementorTemplate[]> {
    // TODO: Implement file loading
    // For now, return mock templates
    return []
  }

  /**
   * Get available templates
   */
  getAvailableTemplates(): ElementorTemplate[] {
    return this.templates
  }

  /**
   * Get templates by category
   */
  getTemplatesByCategory(category: string): ElementorTemplate[] {
    return this.templates.filter(template => 
      template.category.includes(category)
    )
  }

  /**
   * Search templates by keyword
   */
  searchTemplates(query: string): ElementorTemplate[] {
    const lowerQuery = query.toLowerCase()
    
    return this.templates.filter(template =>
      template.title.toLowerCase().includes(lowerQuery) ||
      template.category.some(cat => cat.toLowerCase().includes(lowerQuery)) ||
      template.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    )
  }
}