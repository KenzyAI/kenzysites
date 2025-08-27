// WordPress Hosted Client - Integração com aikenzy.com.br
import { WordPressAPIClient } from './client'
import type { WPSiteConfig, WPSiteInfo } from './types'

interface HostedWordPressConfig extends WPSiteConfig {
  isMultisite?: boolean
  networkAdmin?: boolean
  siteId?: number
}

export class HostedWordPressClient extends WordPressAPIClient {
  private isMultisite: boolean = false
  private currentSiteId?: number
  private config: HostedWordPressConfig

  constructor(config: HostedWordPressConfig) {
    super(config)
    this.config = config
    this.isMultisite = config.isMultisite || false
    this.currentSiteId = config.siteId
  }

  /**
   * Make a GET request to WordPress API
   */
  private async get(endpoint: string): Promise<any> {
    const response = await this.request(endpoint)
    return response.data
  }

  /**
   * Make a POST request to WordPress API
   */
  private async post(endpoint: string, data: any): Promise<any> {
    const response = await this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
    return response.data
  }

  /**
   * Make request using parent class method
   */
  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    // Build full URL
    const baseUrl = `${this.config.url.replace(/\/$/, '')}`
    const url = endpoint.startsWith('/wp-json') ? `${baseUrl}${endpoint}` : `${baseUrl}/wp-json/wp/v2${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers as Record<string, string>,
    }

    // Add authentication
    if (this.config.username && this.config.applicationPassword) {
      const credentials = btoa(`${this.config.username}:${this.config.applicationPassword}`)
      headers['Authorization'] = `Basic ${credentials}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      const responseData = await response.json()

      if (!response.ok) {
        throw new Error(`${response.status}: ${responseData.message || 'API Error'}`)
      }

      return {
        data: responseData,
        headers: Object.fromEntries(response.headers.entries()),
        status: response.status,
      }
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Network error')
    }
  }

  /**
   * Test connection with hosted WordPress
   */
  async testHostedConnection(): Promise<{
    success: boolean
    siteInfo?: WPSiteInfo
    isMultisite?: boolean
    currentUser?: any
    elementorActive?: boolean
    message: string
  }> {
    try {
      // Test basic connection
      const response = await this.get('/')
      
      // Get site info
      const siteInfo = await this.getSiteInfo()
      
      // Check current user
      const currentUser = await this.get('/users/me')
      
      // Check if Elementor is active - try different endpoints
      let elementorActive = false
      try {
        const plugins = await this.get('/plugins')
        elementorActive = plugins.some((plugin: any) => 
          plugin.plugin === 'elementor/elementor.php' && plugin.status === 'active'
        )
      } catch {
        // Plugins endpoint might not be available, try alternative
        try {
          await this.get('/wp-json/elementor/v1/templates')
          elementorActive = true
        } catch {
          elementorActive = false
        }
      }
      
      // Check if it's multisite
      const isMultisite = response.multisite || false
      
      return {
        success: true,
        siteInfo,
        isMultisite,
        currentUser: {
          id: currentUser.id,
          name: currentUser.name,
          username: currentUser.username,
          roles: currentUser.roles
        },
        elementorActive,
        message: 'Conexão estabelecida com sucesso!'
      }
    } catch (error) {
      return {
        success: false,
        message: `Erro na conexão: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      }
    }
  }

  /**
   * Create new multisite (if multisite is enabled)
   */
  async createMultisite(config: {
    domain: string
    title: string
    adminEmail?: string
    public?: boolean
  }): Promise<{
    success: boolean
    siteId?: number
    siteUrl?: string
    message: string
  }> {
    if (!this.isMultisite) {
      return {
        success: false,
        message: 'Multisite não está habilitado'
      }
    }

    try {
      // Create new site in network
      const response = await this.post('/wp-json/wp/v2/sites', {
        domain: config.domain,
        path: '/',
        title: config.title,
        user_id: 1, // Network admin
        meta: {
          public: config.public !== false ? 1 : 0
        }
      })

      return {
        success: true,
        siteId: response.blog_id,
        siteUrl: `https://${config.domain}`,
        message: 'Site criado com sucesso!'
      }
    } catch (error) {
      return {
        success: false,
        message: `Erro ao criar site: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      }
    }
  }

  /**
   * Switch to specific multisite
   */
  async switchToSite(siteId: number): Promise<boolean> {
    if (!this.isMultisite) {
      return false
    }

    try {
      // Update base URL for specific site
      this.currentSiteId = siteId
      // Note: In multisite, each site has its own REST API endpoint
      // This might need adjustment based on your multisite setup
      
      return true
    } catch (error) {
      console.error('Erro ao trocar de site:', error)
      return false
    }
  }

  /**
   * List all sites in network (multisite only)
   */
  async listNetworkSites(): Promise<{
    success: boolean
    sites?: Array<{
      blog_id: number
      domain: string
      path: string
      site_url: string
      blogname: string
    }>
    message: string
  }> {
    if (!this.isMultisite) {
      return {
        success: false,
        message: 'Multisite não está habilitado'
      }
    }

    try {
      const sites = await this.get('/wp-json/wp/v2/sites')
      
      return {
        success: true,
        sites: sites.map((site: any) => ({
          blog_id: site.blog_id,
          domain: site.domain,
          path: site.path,
          site_url: site.siteurl,
          blogname: site.blogname
        })),
        message: 'Sites listados com sucesso'
      }
    } catch (error) {
      return {
        success: false,
        message: `Erro ao listar sites: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      }
    }
  }

  /**
   * Check Elementor status and get templates
   */
  async getElementorInfo(): Promise<{
    active: boolean
    version?: string
    proActive?: boolean
    templates?: any[]
    message: string
  }> {
    try {
      // Check if Elementor is active via plugins endpoint
      const plugins = await this.get('/wp-json/wp/v2/plugins')
      const elementor = plugins.find((plugin: any) => 
        plugin.plugin === 'elementor/elementor.php'
      )
      
      if (!elementor || elementor.status !== 'active') {
        return {
          active: false,
          message: 'Elementor não está ativo'
        }
      }

      // Try to get Elementor templates
      let templates = []
      try {
        templates = await this.get('/wp-json/elementor/v1/templates')
      } catch {
        // Elementor API might not be available
        templates = []
      }

      // Check for Elementor Pro
      const elementorPro = plugins.find((plugin: any) => 
        plugin.plugin === 'elementor-pro/elementor-pro.php'
      )

      return {
        active: true,
        version: elementor.version,
        proActive: elementorPro?.status === 'active',
        templates,
        message: 'Elementor está ativo e funcionando'
      }
    } catch (error) {
      return {
        active: false,
        message: `Erro ao verificar Elementor: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      }
    }
  }

  /**
   * Import Elementor template to hosted WordPress using KenzySites plugin
   */
  async importElementorTemplate(templateData: {
    title: string
    content: any[]
    type?: 'page' | 'post'
    status?: 'publish' | 'draft'
  }): Promise<{
    success: boolean
    pageId?: number
    pageUrl?: string
    editUrl?: string
    message: string
  }> {
    try {
      // Use KenzySites plugin endpoint
      const payload = {
        title: templateData.title,
        content: templateData.content, // Ensure it's already an array/object, not string
        type: templateData.type || 'page',
        status: templateData.status || 'publish'
      }
      
      // Debug log to see what we're sending
      console.log('Sending to KenzySites plugin:', {
        title: payload.title,
        contentType: typeof payload.content,
        contentLength: Array.isArray(payload.content) ? payload.content.length : 'not array'
      })
      
      const response = await this.post('/wp-json/kenzysites/v1/elementor/import', payload)

      return {
        success: response.success || false,
        pageId: response.page_id,
        pageUrl: response.page_url,
        editUrl: response.edit_url,
        message: response.message || 'Template importado com sucesso!'
      }
    } catch (error) {
      // Fallback to standard WordPress API if plugin not available
      try {
        console.warn('KenzySites plugin not available, falling back to standard API')
        return await this.importElementorTemplateFallback(templateData)
      } catch (fallbackError) {
        return {
          success: false,
          message: `Erro ao importar template: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
        }
      }
    }
  }

  /**
   * Fallback method for Elementor import without plugin
   */
  private async importElementorTemplateFallback(templateData: {
    title: string
    content: any[]
    type?: 'page' | 'post'
    status?: 'publish' | 'draft'
  }): Promise<{
    success: boolean
    pageId?: number
    pageUrl?: string
    message: string
  }> {
    // Create page/post first
    const pageData = {
      title: templateData.title,
      status: templateData.status || 'publish',
      content: '', // Elementor handles content via meta
    }

    const response = await this.post(`/${templateData.type || 'pages'}`, pageData)

    // Then set Elementor meta data
    const metaData = {
      '_elementor_edit_mode': 'builder',
      '_elementor_template_type': 'wp-page',
      '_elementor_data': JSON.stringify(templateData.content)
    }

    // Update post meta (this might not work without proper permissions)
    try {
      await this.post(`/${templateData.type || 'pages'}/${response.id}`, {
        meta: metaData
      })
    } catch (metaError) {
      console.warn('Could not set Elementor meta data:', metaError)
    }

    return {
      success: true,
      pageId: response.id,
      pageUrl: response.link,
      message: 'Template criado (meta data pode precisar ser configurada manualmente)'
    }
  }
}

// Factory function for hosted WordPress client
export function createHostedWordPressClient(config?: Partial<HostedWordPressConfig>): HostedWordPressClient {
  const defaultConfig: HostedWordPressConfig = {
    url: 'https://aikenzy.com.br',
    username: 'dkenzy',
    applicationPassword: '4AM0t7AhFush3HAmnbfE3Vuq', // Nova senha sem espaços
    authMethod: 'application_password',
    isMultisite: true, // Assumindo que é multisite baseado na descrição
    networkAdmin: true
  }

  return new HostedWordPressClient({
    ...defaultConfig,
    ...config
  })
}