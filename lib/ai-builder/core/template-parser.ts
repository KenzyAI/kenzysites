// Elementor Template Parser - Core functionality for parsing and manipulating Elementor templates

import type { ElementorTemplate, ElementorElement } from '../types'

export class ElementorTemplateParser {
  /**
   * Parse Elementor JSON string into template object
   */
  parse(jsonString: string): ElementorTemplate {
    try {
      const data = JSON.parse(jsonString)
      return this.validateTemplate(data)
    } catch (error) {
      throw new Error(`Failed to parse Elementor template: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Convert template object back to JSON string
   */
  stringify(template: ElementorTemplate): string {
    return JSON.stringify(template, null, 2)
  }

  /**
   * Validate template structure
   */
  private validateTemplate(data: any): ElementorTemplate {
    if (!data.content || !Array.isArray(data.content)) {
      throw new Error('Invalid template: missing or invalid content array')
    }

    return {
      id: data.id || this.generateId(),
      title: data.title || 'Untitled Template',
      type: data.type || 'page',
      category: Array.isArray(data.category) ? data.category : [],
      tags: Array.isArray(data.tags) ? data.tags : [],
      content: data.content.map((element: any) => this.parseElement(element)),
      thumbnail: data.thumbnail,
      preview_url: data.preview_url,
      requiredPlugins: data.requiredPlugins || ['elementor'],
      customizable: {
        colors: data.customizable?.colors !== false,
        fonts: data.customizable?.fonts !== false,
        content: data.customizable?.content !== false,
        images: data.customizable?.images !== false,
        ...data.customizable
      }
    }
  }

  /**
   * Parse individual Elementor element
   */
  private parseElement(elementData: any): ElementorElement {
    const element: ElementorElement = {
      id: elementData.id || this.generateId(),
      elType: elementData.elType || 'widget',
      settings: elementData.settings || {}
    }

    if (elementData.widgetType) {
      element.widgetType = elementData.widgetType
    }

    if (elementData.elements && Array.isArray(elementData.elements)) {
      element.elements = elementData.elements.map((child: any) => this.parseElement(child))
    }

    if (elementData.isInner) {
      element.isInner = elementData.isInner
    }

    return element
  }

  /**
   * Find elements by type (widget type, element type, etc.)
   */
  findElements(template: ElementorTemplate, criteria: {
    elType?: string
    widgetType?: string
    setting?: { key: string; value?: any }
  }): ElementorElement[] {
    const results: ElementorElement[] = []

    const searchRecursive = (elements: ElementorElement[]) => {
      for (const element of elements) {
        let matches = true

        // Check element type
        if (criteria.elType && element.elType !== criteria.elType) {
          matches = false
        }

        // Check widget type
        if (criteria.widgetType && element.widgetType !== criteria.widgetType) {
          matches = false
        }

        // Check settings
        if (criteria.setting) {
          const settingValue = element.settings[criteria.setting.key]
          if (criteria.setting.value !== undefined) {
            if (settingValue !== criteria.setting.value) {
              matches = false
            }
          } else if (settingValue === undefined) {
            matches = false
          }
        }

        if (matches) {
          results.push(element)
        }

        // Search in child elements
        if (element.elements) {
          searchRecursive(element.elements)
        }
      }
    }

    searchRecursive(template.content)
    return results
  }

  /**
   * Update element settings by ID
   */
  updateElement(template: ElementorTemplate, elementId: string, newSettings: Record<string, any>): boolean {
    const updateRecursive = (elements: ElementorElement[]): boolean => {
      for (const element of elements) {
        if (element.id === elementId) {
          element.settings = { ...element.settings, ...newSettings }
          return true
        }

        if (element.elements && updateRecursive(element.elements)) {
          return true
        }
      }
      return false
    }

    return updateRecursive(template.content)
  }

  /**
   * Replace text content in template
   */
  replaceTextContent(template: ElementorTemplate, replacements: Record<string, string>): void {
    const replaceRecursive = (elements: ElementorElement[]) => {
      for (const element of elements) {
        // Handle different text widgets
        this.replaceTextInElement(element, replacements)

        // Recurse into child elements
        if (element.elements) {
          replaceRecursive(element.elements)
        }
      }
    }

    replaceRecursive(template.content)
  }

  /**
   * Replace text content in a specific element
   */
  private replaceTextInElement(element: ElementorElement, replacements: Record<string, string>): void {
    const settings = element.settings

    // Common text fields in different widgets
    const textFields = [
      'title', 'text', 'content', 'editor', 'caption', 'description',
      'button_text', 'link_text', 'heading', 'sub_heading', 'label'
    ]

    for (const field of textFields) {
      if (settings[field] && typeof settings[field] === 'string') {
        let text = settings[field]
        
        for (const [search, replace] of Object.entries(replacements)) {
          // Handle both placeholder format {{key}} and plain text
          const placeholderPattern = new RegExp(`\\{\\{${search}\\}\\}`, 'g')
          text = text.replace(placeholderPattern, replace)
          
          // Also handle direct text replacement for common phrases
          if (search.length > 3) { // Only replace longer phrases to avoid accidental replacements
            const directPattern = new RegExp(search, 'gi')
            text = text.replace(directPattern, replace)
          }
        }
        
        settings[field] = text
      }
    }

    // Handle more complex structures (like button links)
    if (settings.link && typeof settings.link === 'object') {
      if (settings.link.url && typeof settings.link.url === 'string') {
        for (const [search, replace] of Object.entries(replacements)) {
          settings.link.url = settings.link.url.replace(new RegExp(`\\{\\{${search}\\}\\}`, 'g'), replace)
        }
      }
    }
  }

  /**
   * Replace images in template
   */
  replaceImages(template: ElementorTemplate, imageReplacements: Record<string, { url: string; alt?: string }>): void {
    const replaceRecursive = (elements: ElementorElement[]) => {
      for (const element of elements) {
        this.replaceImagesInElement(element, imageReplacements)

        if (element.elements) {
          replaceRecursive(element.elements)
        }
      }
    }

    replaceRecursive(template.content)
  }

  /**
   * Replace images in a specific element
   */
  private replaceImagesInElement(element: ElementorElement, imageReplacements: Record<string, { url: string; alt?: string }>): void {
    const settings = element.settings

    // Handle image widget
    if (element.widgetType === 'image' && settings.image) {
      for (const [key, replacement] of Object.entries(imageReplacements)) {
        if (settings.image.url && settings.image.url.includes(key)) {
          settings.image = {
            ...settings.image,
            url: replacement.url,
            alt: replacement.alt || settings.image.alt || ''
          }
          break
        }
      }
    }

    // Handle background images
    if (settings.background_image) {
      for (const [key, replacement] of Object.entries(imageReplacements)) {
        if (settings.background_image.url && settings.background_image.url.includes(key)) {
          settings.background_image = {
            ...settings.background_image,
            url: replacement.url
          }
          break
        }
      }
    }

    // Handle other image fields
    const imageFields = ['image', 'bg_image', 'icon_image', 'logo_image']
    for (const field of imageFields) {
      if (settings[field] && typeof settings[field] === 'object' && settings[field].url) {
        for (const [key, replacement] of Object.entries(imageReplacements)) {
          if (settings[field].url.includes(key)) {
            settings[field] = {
              ...settings[field],
              url: replacement.url,
              alt: replacement.alt || settings[field].alt || ''
            }
            break
          }
        }
      }
    }
  }

  /**
   * Update colors in template
   */
  updateColors(template: ElementorTemplate, colorScheme: {
    primary?: string
    secondary?: string
    accent?: string
    text?: string
    background?: string
  }): void {
    const updateRecursive = (elements: ElementorElement[]) => {
      for (const element of elements) {
        this.updateColorsInElement(element, colorScheme)

        if (element.elements) {
          updateRecursive(element.elements)
        }
      }
    }

    updateRecursive(template.content)
  }

  /**
   * Update colors in a specific element
   */
  private updateColorsInElement(element: ElementorElement, colorScheme: Record<string, string>): void {
    const settings = element.settings

    // Map of common color settings to color scheme keys
    const colorMappings = {
      // Text colors
      'color': 'text',
      'text_color': 'text',
      'heading_color': 'text',
      'title_color': 'text',
      
      // Background colors
      'background_color': 'background',
      'bg_color': 'background',
      
      // Primary/accent colors (buttons, links, etc.)
      'button_background_color': 'primary',
      'link_color': 'primary',
      'icon_color': 'primary',
      'border_color': 'secondary'
    }

    for (const [settingKey, colorKey] of Object.entries(colorMappings)) {
      if (settings[settingKey] && colorScheme[colorKey]) {
        settings[settingKey] = colorScheme[colorKey]
      }
    }
  }

  /**
   * Generate unique ID for elements
   */
  private generateId(): string {
    return Math.random().toString(36).substr(2, 9)
  }

  /**
   * Clone template (deep copy)
   */
  clone(template: ElementorTemplate): ElementorTemplate {
    return JSON.parse(JSON.stringify(template))
  }

  /**
   * Get template statistics
   */
  getTemplateStats(template: ElementorTemplate): {
    totalElements: number
    elementTypes: Record<string, number>
    widgetTypes: Record<string, number>
    textElements: number
    imageElements: number
  } {
    const stats = {
      totalElements: 0,
      elementTypes: {} as Record<string, number>,
      widgetTypes: {} as Record<string, number>,
      textElements: 0,
      imageElements: 0
    }

    const countRecursive = (elements: ElementorElement[]) => {
      for (const element of elements) {
        stats.totalElements++
        
        // Count element types
        stats.elementTypes[element.elType] = (stats.elementTypes[element.elType] || 0) + 1
        
        // Count widget types
        if (element.widgetType) {
          stats.widgetTypes[element.widgetType] = (stats.widgetTypes[element.widgetType] || 0) + 1
          
          // Count text and image elements
          if (['heading', 'text-editor', 'testimonial'].includes(element.widgetType)) {
            stats.textElements++
          }
          if (['image', 'image-carousel', 'image-gallery'].includes(element.widgetType)) {
            stats.imageElements++
          }
        }

        if (element.elements) {
          countRecursive(element.elements)
        }
      }
    }

    countRecursive(template.content)
    return stats
  }
}