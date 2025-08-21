import { 
  WPSiteConfig, 
  WPSiteInfo, 
  WPUser, 
  WPPost, 
  WPPage, 
  WPTheme, 
  WPPlugin, 
  WPCategory, 
  WPTag, 
  WPMedia, 
  WPComment, 
  WPSettings,
  WPAPIResponse,
  WPAPIError,
  WPQueryParams,
  WPHealthCheck,
  WPBackup
} from './types'

export class WordPressAPIClient {
  private config: WPSiteConfig
  private baseUrl: string

  constructor(config: WPSiteConfig) {
    this.config = config
    this.baseUrl = `${config.url.replace(/\/$/, '')}/wp-json/wp/v2`
  }

  /**
   * Make authenticated request to WordPress API
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<WPAPIResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers as Record<string, string>,
    }

    // Add authentication
    if (this.config.authMethod === 'basic' && this.config.username && this.config.password) {
      const credentials = btoa(`${this.config.username}:${this.config.password}`)
      headers['Authorization'] = `Basic ${credentials}`
    } else if (this.config.authMethod === 'application_password' && this.config.username && this.config.applicationPassword) {
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
        const error: WPAPIError = {
          code: responseData.code || 'unknown_error',
          message: responseData.message || 'Unknown error occurred',
          data: {
            status: response.status,
            ...responseData.data,
          },
        }
        throw error
      }

      return {
        data: responseData,
        headers: Object.fromEntries(response.headers.entries()),
        status: response.status,
      }
    } catch (error) {
      if (error instanceof Error && 'code' in error) {
        throw error
      }
      
      throw {
        code: 'network_error',
        message: error instanceof Error ? error.message : 'Network error occurred',
        data: { status: 0 },
      } as WPAPIError
    }
  }

  /**
   * Build query string from parameters
   */
  private buildQueryString(params: WPQueryParams): string {
    const searchParams = new URLSearchParams()

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(`${key}[]`, String(v)))
        } else {
          searchParams.append(key, String(value))
        }
      }
    })

    const queryString = searchParams.toString()
    return queryString ? `?${queryString}` : ''
  }

  /**
   * Get site information
   */
  async getSiteInfo(): Promise<WPSiteInfo> {
    const response = await this.request<WPSiteInfo>('/')
    return response.data
  }

  /**
   * Test connection to WordPress site
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.getSiteInfo()
      return true
    } catch {
      return false
    }
  }

  // USERS
  /**
   * Get users
   */
  async getUsers(params: WPQueryParams = {}): Promise<WPUser[]> {
    const queryString = this.buildQueryString(params)
    const response = await this.request<WPUser[]>(`/users${queryString}`)
    return response.data
  }

  /**
   * Get user by ID
   */
  async getUser(id: number): Promise<WPUser> {
    const response = await this.request<WPUser>(`/users/${id}`)
    return response.data
  }

  /**
   * Create user
   */
  async createUser(userData: Partial<WPUser>): Promise<WPUser> {
    const response = await this.request<WPUser>('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
    return response.data
  }

  /**
   * Update user
   */
  async updateUser(id: number, userData: Partial<WPUser>): Promise<WPUser> {
    const response = await this.request<WPUser>(`/users/${id}`, {
      method: 'POST',
      body: JSON.stringify(userData),
    })
    return response.data
  }

  /**
   * Delete user
   */
  async deleteUser(id: number, reassign?: number): Promise<{ deleted: boolean }> {
    const params = reassign ? `?reassign=${reassign}` : ''
    const response = await this.request<{ deleted: boolean }>(`/users/${id}${params}`, {
      method: 'DELETE',
    })
    return response.data
  }

  // POSTS
  /**
   * Get posts
   */
  async getPosts(params: WPQueryParams = {}): Promise<WPPost[]> {
    const queryString = this.buildQueryString(params)
    const response = await this.request<WPPost[]>(`/posts${queryString}`)
    return response.data
  }

  /**
   * Get post by ID
   */
  async getPost(id: number): Promise<WPPost> {
    const response = await this.request<WPPost>(`/posts/${id}`)
    return response.data
  }

  /**
   * Create post
   */
  async createPost(postData: Partial<WPPost>): Promise<WPPost> {
    const response = await this.request<WPPost>('/posts', {
      method: 'POST',
      body: JSON.stringify(postData),
    })
    return response.data
  }

  /**
   * Update post
   */
  async updatePost(id: number, postData: Partial<WPPost>): Promise<WPPost> {
    const response = await this.request<WPPost>(`/posts/${id}`, {
      method: 'POST',
      body: JSON.stringify(postData),
    })
    return response.data
  }

  /**
   * Delete post
   */
  async deletePost(id: number, force: boolean = false): Promise<{ deleted: boolean }> {
    const params = force ? '?force=true' : ''
    const response = await this.request<{ deleted: boolean }>(`/posts/${id}${params}`, {
      method: 'DELETE',
    })
    return response.data
  }

  // PAGES
  /**
   * Get pages
   */
  async getPages(params: WPQueryParams = {}): Promise<WPPage[]> {
    const queryString = this.buildQueryString(params)
    const response = await this.request<WPPage[]>(`/pages${queryString}`)
    return response.data
  }

  /**
   * Get page by ID
   */
  async getPage(id: number): Promise<WPPage> {
    const response = await this.request<WPPage>(`/pages/${id}`)
    return response.data
  }

  /**
   * Create page
   */
  async createPage(pageData: Partial<WPPage>): Promise<WPPage> {
    const response = await this.request<WPPage>('/pages', {
      method: 'POST',
      body: JSON.stringify(pageData),
    })
    return response.data
  }

  /**
   * Update page
   */
  async updatePage(id: number, pageData: Partial<WPPage>): Promise<WPPage> {
    const response = await this.request<WPPage>(`/pages/${id}`, {
      method: 'POST',
      body: JSON.stringify(pageData),
    })
    return response.data
  }

  /**
   * Delete page
   */
  async deletePage(id: number, force: boolean = false): Promise<{ deleted: boolean }> {
    const params = force ? '?force=true' : ''
    const response = await this.request<{ deleted: boolean }>(`/pages/${id}${params}`, {
      method: 'DELETE',
    })
    return response.data
  }

  // CATEGORIES
  /**
   * Get categories
   */
  async getCategories(params: WPQueryParams = {}): Promise<WPCategory[]> {
    const queryString = this.buildQueryString(params)
    const response = await this.request<WPCategory[]>(`/categories${queryString}`)
    return response.data
  }

  /**
   * Create category
   */
  async createCategory(categoryData: Partial<WPCategory>): Promise<WPCategory> {
    const response = await this.request<WPCategory>('/categories', {
      method: 'POST',
      body: JSON.stringify(categoryData),
    })
    return response.data
  }

  // TAGS
  /**
   * Get tags
   */
  async getTags(params: WPQueryParams = {}): Promise<WPTag[]> {
    const queryString = this.buildQueryString(params)
    const response = await this.request<WPTag[]>(`/tags${queryString}`)
    return response.data
  }

  /**
   * Create tag
   */
  async createTag(tagData: Partial<WPTag>): Promise<WPTag> {
    const response = await this.request<WPTag>('/tags', {
      method: 'POST',
      body: JSON.stringify(tagData),
    })
    return response.data
  }

  // MEDIA
  /**
   * Get media
   */
  async getMedia(params: WPQueryParams = {}): Promise<WPMedia[]> {
    const queryString = this.buildQueryString(params)
    const response = await this.request<WPMedia[]>(`/media${queryString}`)
    return response.data
  }

  /**
   * Upload media
   */
  async uploadMedia(file: File, title?: string, alt_text?: string): Promise<WPMedia> {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    if (alt_text) formData.append('alt_text', alt_text)

    const response = await this.request<WPMedia>('/media', {
      method: 'POST',
      body: formData,
      headers: {}, // Remove content-type to let browser set it with boundary
    })
    return response.data
  }

  // COMMENTS
  /**
   * Get comments
   */
  async getComments(params: WPQueryParams = {}): Promise<WPComment[]> {
    const queryString = this.buildQueryString(params)
    const response = await this.request<WPComment[]>(`/comments${queryString}`)
    return response.data
  }

  /**
   * Create comment
   */
  async createComment(commentData: Partial<WPComment>): Promise<WPComment> {
    const response = await this.request<WPComment>('/comments', {
      method: 'POST',
      body: JSON.stringify(commentData),
    })
    return response.data
  }

  // SETTINGS
  /**
   * Get settings
   */
  async getSettings(): Promise<WPSettings> {
    const response = await this.request<WPSettings>('/settings')
    return response.data
  }

  /**
   * Update settings
   */
  async updateSettings(settingsData: Partial<WPSettings>): Promise<WPSettings> {
    const response = await this.request<WPSettings>('/settings', {
      method: 'POST',
      body: JSON.stringify(settingsData),
    })
    return response.data
  }

  // THEMES (Requires additional plugin/API)
  /**
   * Get themes - Note: This requires a custom endpoint
   */
  async getThemes(): Promise<WPTheme[]> {
    try {
      const response = await this.request<WPTheme[]>('/themes')
      return response.data
    } catch (error) {
      // Fallback: Return mock data or empty array
      console.warn('Themes endpoint not available, using fallback')
      return []
    }
  }

  /**
   * Activate theme - Note: This requires a custom endpoint
   */
  async activateTheme(stylesheet: string): Promise<{ success: boolean }> {
    try {
      const response = await this.request<{ success: boolean }>('/themes/activate', {
        method: 'POST',
        body: JSON.stringify({ stylesheet }),
      })
      return response.data
    } catch (error) {
      console.warn('Theme activation endpoint not available')
      return { success: false }
    }
  }

  // PLUGINS (Requires additional plugin/API)
  /**
   * Get plugins - Note: This requires a custom endpoint
   */
  async getPlugins(): Promise<WPPlugin[]> {
    try {
      const response = await this.request<WPPlugin[]>('/plugins')
      return response.data
    } catch (error) {
      // Fallback: Return mock data or empty array
      console.warn('Plugins endpoint not available, using fallback')
      return []
    }
  }

  /**
   * Activate plugin - Note: This requires a custom endpoint
   */
  async activatePlugin(plugin: string): Promise<{ success: boolean }> {
    try {
      const response = await this.request<{ success: boolean }>('/plugins/activate', {
        method: 'POST',
        body: JSON.stringify({ plugin }),
      })
      return response.data
    } catch (error) {
      console.warn('Plugin activation endpoint not available')
      return { success: false }
    }
  }

  /**
   * Deactivate plugin - Note: This requires a custom endpoint
   */
  async deactivatePlugin(plugin: string): Promise<{ success: boolean }> {
    try {
      const response = await this.request<{ success: boolean }>('/plugins/deactivate', {
        method: 'POST',
        body: JSON.stringify({ plugin }),
      })
      return response.data
    } catch (error) {
      console.warn('Plugin deactivation endpoint not available')
      return { success: false }
    }
  }

  // HEALTH CHECK
  /**
   * Perform health check - Note: This requires a custom endpoint
   */
  async performHealthCheck(): Promise<WPHealthCheck> {
    try {
      const response = await this.request<WPHealthCheck>('/health-check')
      return response.data
    } catch (error) {
      // Return basic health check
      return {
        site_url: this.config.url,
        timestamp: new Date().toISOString(),
        status: 'warning',
        response_time: 0,
        ssl_valid: this.config.url.startsWith('https://'),
        ssl_expires: '',
        uptime_percentage: 0,
        checks: {
          database: { status: 'pass', message: 'Not checked', response_time: 0 },
          filesystem: { status: 'pass', message: 'Not checked', writable_directories: [] },
          security: { status: 'pass', wp_version: '', plugin_updates: 0, theme_updates: 0, security_plugins: [] },
          performance: { status: 'pass', page_load_time: 0, memory_usage: 0, memory_limit: '', active_plugins: 0 },
        },
        recommendations: ['Install health check plugin for detailed monitoring'],
      }
    }
  }

  // BACKUP
  /**
   * Create backup - Note: This requires a custom endpoint
   */
  async createBackup(type: 'full' | 'database' | 'files' = 'full'): Promise<WPBackup> {
    try {
      const response = await this.request<WPBackup>('/backup', {
        method: 'POST',
        body: JSON.stringify({ type }),
      })
      return response.data
    } catch (error) {
      throw new Error('Backup endpoint not available. Install backup plugin.')
    }
  }

  /**
   * Get backup status
   */
  async getBackupStatus(backupId: string): Promise<WPBackup> {
    try {
      const response = await this.request<WPBackup>(`/backup/${backupId}`)
      return response.data
    } catch (error) {
      throw new Error('Backup endpoint not available. Install backup plugin.')
    }
  }

  /**
   * List backups
   */
  async listBackups(): Promise<WPBackup[]> {
    try {
      const response = await this.request<WPBackup[]>('/backups')
      return response.data
    } catch (error) {
      return []
    }
  }
}