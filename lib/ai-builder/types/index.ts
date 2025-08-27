// AI Builder - Type Definitions

// Business Information Types
export interface BusinessInfo {
  name: string
  type: 'restaurant' | 'business' | 'portfolio' | 'ecommerce' | 'blog' | 'landing' | 'other'
  description: string
  industry?: string
  services?: string[]
  targetAudience?: string
  location?: string
  phone?: string
  email?: string
  website?: string
  socialMedia?: {
    facebook?: string
    instagram?: string
    linkedin?: string
    twitter?: string
  }
}

// Elementor Template Types
export interface ElementorElement {
  id: string
  elType: 'section' | 'column' | 'widget'
  settings: Record<string, any>
  elements?: ElementorElement[]
  widgetType?: string
  isInner?: boolean
}

export interface ElementorTemplate {
  id: string
  title: string
  type: 'page' | 'section' | 'widget'
  category: string[]
  tags: string[]
  content: ElementorElement[]
  thumbnail?: string
  preview_url?: string
  requiredPlugins?: string[]
  customizable: {
    colors: boolean
    fonts: boolean
    content: boolean
    images: boolean
  }
  colorScheme?: {
    primary: string
    secondary: string
    accent: string
    text: string
    background?: string
  }
}

// Generated Content Types
export interface GeneratedContent {
  headline: string
  tagline?: string
  description: string
  features: string[]
  services: Array<{
    title: string
    description: string
    icon?: string
  }>
  testimonials: Array<{
    text: string
    author: string
    role: string
  }>
  cta: {
    primary: string
    secondary?: string
  }
  contact: {
    address?: string
    phone?: string
    email?: string
    hours?: string
  }
  about: string
  images: {
    hero: string[]
    gallery: string[]
    team: string[]
    services: string[]
  }
}

// AI Builder Configuration
export interface AIBuilderConfig {
  openaiApiKey?: string
  claudeApiKey?: string
  unsplashApiKey?: string
  pexelsApiKey?: string
  defaultModel?: 'gpt-4' | 'gpt-3.5-turbo' | 'claude-3'
  maxTokens?: number
  temperature?: number
}

// Template Matching
export interface TemplateMatch {
  template: ElementorTemplate
  score: number
  reasons: string[]
}

// Site Generation Request
export interface SiteGenerationRequest {
  businessInfo: BusinessInfo
  templateId?: string
  preferences?: {
    colorScheme?: 'auto' | 'light' | 'dark' | 'colorful' | 'minimal'
    style?: 'modern' | 'classic' | 'creative' | 'corporate' | 'fun'
    layout?: 'single-page' | 'multi-page'
    includePages?: ('home' | 'about' | 'services' | 'contact' | 'blog' | 'portfolio')[]
  }
  customization?: {
    primaryColor?: string
    secondaryColor?: string
    fontFamily?: string
    logo?: string
  }
}

// Site Generation Response
export interface SiteGenerationResponse {
  success: boolean
  siteId?: string
  pages?: Array<{
    id: number
    title: string
    url: string
    type: string
  }>
  preview_url?: string
  template_used?: string
  generation_time?: number
  error?: string
  warnings?: string[]
}

// WordPress Integration
export interface WordPressSiteConfig {
  id?: number
  domain: string
  title: string
  isSubsite?: boolean
  parentSiteId?: number
  template_data: ElementorTemplate[]
  status: 'creating' | 'active' | 'error' | 'suspended'
  created_at?: string
  updated_at?: string
}

// Template Library
export interface TemplateLibrary {
  id: string
  name: string
  description: string
  templates: ElementorTemplate[]
  categories: string[]
  lastUpdated: string
  version: string
}

// AI Generation Progress
export interface GenerationProgress {
  stage: 'analyzing' | 'selecting_template' | 'generating_content' | 'customizing' | 'deploying' | 'completed' | 'error'
  progress: number // 0-100
  message: string
  details?: {
    template_selected?: string
    content_generated?: boolean
    images_selected?: boolean
    deployment_started?: boolean
  }
  error?: string
}

// Image Selection
export interface SelectedImage {
  url: string
  thumbnail: string
  alt: string
  source: 'unsplash' | 'pexels' | 'custom'
  tags: string[]
  license?: string
}

// Content Generation Context
export interface ContentGenerationContext {
  businessInfo: BusinessInfo
  template: ElementorTemplate
  sectionType: string
  existingContent?: string
  targetLength?: 'short' | 'medium' | 'long'
  tone?: 'professional' | 'friendly' | 'creative' | 'technical'
}

// AI Builder Error Types
export interface AIBuilderError {
  code: string
  message: string
  stage?: string
  details?: Record<string, any>
  recoverable: boolean
}