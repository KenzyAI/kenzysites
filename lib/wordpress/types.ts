// WordPress API Types and Interfaces

// WordPress Site Configuration
export interface WPSiteConfig {
  url: string
  username: string
  password?: string
  applicationPassword?: string
  authMethod: 'basic' | 'application_password' | 'jwt'
}

// WordPress Site Info
export interface WPSiteInfo {
  name: string
  description: string
  url: string
  home: string
  gmt_offset: number
  timezone_string: string
  namespaces: string[]
  authentication: any[]
  routes: Record<string, any>
  version: string
  php_version: string
  mysql_version: string
  theme: {
    name: string
    version: string
    author: string
    status: 'active' | 'inactive'
  }
  plugins: WPPlugin[]
  multisite: boolean
  permalink_structure: string
  language: string
  rtl: boolean
}

// WordPress User
export interface WPUser {
  id: number
  username: string
  name: string
  first_name: string
  last_name: string
  email: string
  url: string
  description: string
  link: string
  locale: string
  nickname: string
  slug: string
  roles: string[]
  capabilities: Record<string, boolean>
  extra_capabilities: Record<string, boolean>
  avatar_urls: Record<string, string>
  meta: any[]
}

// WordPress Post
export interface WPPost {
  id: number
  date: string
  date_gmt: string
  guid: {
    rendered: string
  }
  modified: string
  modified_gmt: string
  slug: string
  status: 'publish' | 'future' | 'draft' | 'pending' | 'private'
  type: string
  link: string
  title: {
    rendered: string
  }
  content: {
    rendered: string
    protected: boolean
  }
  excerpt: {
    rendered: string
    protected: boolean
  }
  author: number
  featured_media: number
  comment_status: 'open' | 'closed'
  ping_status: 'open' | 'closed'
  sticky: boolean
  template: string
  format: string
  meta: any[]
  categories: number[]
  tags: number[]
}

// WordPress Page
export interface WPPage extends Omit<WPPost, 'sticky' | 'categories' | 'tags'> {
  parent: number
  menu_order: number
}

// WordPress Theme
export interface WPTheme {
  name: string
  description: string
  author: string
  version: string
  template: string
  stylesheet: string
  status: 'active' | 'inactive'
  screenshot?: string
  tags: string[]
  theme_supports: Record<string, any>
  parent_theme?: string
  theme_uri?: string
  author_uri?: string
}

// WordPress Plugin
export interface WPPlugin {
  plugin: string
  status: 'active' | 'inactive'
  name: string
  plugin_uri: string
  author: string
  author_uri: string
  description: {
    rendered: string
  }
  version: string
  network_only: boolean
  requires_wp: string
  requires_php: string
  text_domain: string
}

// WordPress Category
export interface WPCategory {
  id: number
  count: number
  description: string
  link: string
  name: string
  slug: string
  taxonomy: string
  parent: number
  meta: any[]
}

// WordPress Tag
export interface WPTag {
  id: number
  count: number
  description: string
  link: string
  name: string
  slug: string
  taxonomy: string
  meta: any[]
}

// WordPress Media
export interface WPMedia {
  id: number
  date: string
  date_gmt: string
  guid: {
    rendered: string
  }
  modified: string
  modified_gmt: string
  slug: string
  status: string
  type: string
  link: string
  title: {
    rendered: string
  }
  author: number
  comment_status: 'open' | 'closed'
  ping_status: 'open' | 'closed'
  template: string
  meta: any[]
  description: {
    rendered: string
  }
  caption: {
    rendered: string
  }
  alt_text: string
  media_type: 'image' | 'video' | 'audio' | 'file'
  mime_type: string
  media_details: {
    width: number
    height: number
    file: string
    sizes: Record<string, {
      file: string
      width: number
      height: number
      mime_type: string
      source_url: string
    }>
    image_meta: Record<string, any>
  }
  post: number
  source_url: string
}

// WordPress Comment
export interface WPComment {
  id: number
  post: number
  parent: number
  author: number
  author_name: string
  author_email: string
  author_url: string
  author_ip: string
  author_user_agent: string
  date: string
  date_gmt: string
  content: {
    rendered: string
  }
  link: string
  status: 'approved' | 'hold' | 'spam' | 'trash'
  type: string
  author_avatar_urls: Record<string, string>
  meta: any[]
}

// WordPress Settings
export interface WPSettings {
  title: string
  description: string
  url: string
  email: string
  timezone: string
  date_format: string
  time_format: string
  start_of_week: number
  language: string
  use_smilies: boolean
  default_category: number
  default_post_format: string
  posts_per_page: number
  discussion_settings: {
    default_pingback_flag: boolean
    default_ping_status: 'open' | 'closed'
    default_comment_status: 'open' | 'closed'
    require_name_email: boolean
    comment_registration: boolean
    close_comments_for_old_posts: boolean
    close_comments_days_old: number
    thread_comments: boolean
    thread_comments_depth: number
    page_comments: boolean
    comments_per_page: number
    default_comments_page: 'newest' | 'oldest'
    comment_order: 'asc' | 'desc'
    comments_notify: boolean
    moderation_notify: boolean
    comment_moderation: boolean
    comment_whitelist: boolean
    comment_max_links: number
    moderation_keys: string
    blacklist_keys: string
  }
}

// API Response Types
export interface WPAPIResponse<T> {
  data: T
  headers: Record<string, string>
  status: number
}

export interface WPAPIError {
  code: string
  message: string
  data: {
    status: number
    params?: Record<string, any>
    details?: Record<string, any>
  }
}

// Query Parameters
export interface WPQueryParams {
  context?: 'view' | 'embed' | 'edit'
  page?: number
  per_page?: number
  search?: string
  after?: string
  before?: string
  exclude?: number[]
  include?: number[]
  offset?: number
  order?: 'asc' | 'desc'
  orderby?: string
  slug?: string[]
  status?: string[]
  categories?: number[]
  categories_exclude?: number[]
  tags?: number[]
  tags_exclude?: number[]
  sticky?: boolean
  author?: number[]
  author_exclude?: number[]
}

// Backup Types
export interface WPBackup {
  id: string
  site_url: string
  created_at: string
  size: number
  type: 'full' | 'database' | 'files'
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  progress: number
  files: {
    database?: string
    uploads?: string
    themes?: string
    plugins?: string
    core?: string
  }
  metadata: {
    wp_version: string
    php_version: string
    mysql_version: string
    active_theme: string
    active_plugins: string[]
  }
}

// Health Check Types
export interface WPHealthCheck {
  site_url: string
  timestamp: string
  status: 'healthy' | 'warning' | 'critical' | 'offline'
  response_time: number
  ssl_valid: boolean
  ssl_expires: string
  uptime_percentage: number
  checks: {
    database: {
      status: 'pass' | 'fail'
      message: string
      response_time: number
    }
    filesystem: {
      status: 'pass' | 'fail'
      message: string
      writable_directories: string[]
    }
    security: {
      status: 'pass' | 'warning' | 'fail'
      wp_version: string
      plugin_updates: number
      theme_updates: number
      security_plugins: string[]
    }
    performance: {
      status: 'pass' | 'warning' | 'fail'
      page_load_time: number
      memory_usage: number
      memory_limit: string
      active_plugins: number
    }
  }
  recommendations: string[]
}

// Provisioning Types
export interface WPProvisioningRequest {
  domain: string
  site_name: string
  admin_username: string
  admin_password: string
  admin_email: string
  theme?: string
  plugins?: string[]
  initial_content?: boolean
  ssl_enabled?: boolean
  backup_enabled?: boolean
  staging_enabled?: boolean
}

export interface WPProvisioningResponse {
  id: string
  status: 'pending' | 'provisioning' | 'completed' | 'failed'
  progress: number
  site_url: string
  admin_url: string
  staging_url?: string
  credentials: {
    wp_admin: {
      username: string
      password: string
    }
    database: {
      host: string
      name: string
      username: string
      password: string
    }
    ftp?: {
      host: string
      username: string
      password: string
      port: number
    }
  }
  ssl_certificate?: {
    issuer: string
    expires: string
    status: 'active' | 'pending' | 'failed'
  }
  error?: string
  created_at: string
  completed_at?: string
}