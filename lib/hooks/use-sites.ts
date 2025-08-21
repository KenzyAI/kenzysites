'use client'

import { useState, useEffect, useCallback } from 'react'

export interface Site {
  id: number
  name: string
  domain: string
  subdomain?: string
  status: 'active' | 'inactive' | 'maintenance' | 'suspended'
  plan: 'basic' | 'pro' | 'enterprise'
  visitors: number
  createdAt: Date
  lastUpdate: Date
  owner: string
  ownerEmail: string
  description?: string
  category: string
  theme: string
  plugins: string[]
  ssl: boolean
  backups: number
  storage: number // MB
  bandwidth: number // GB
  customDomain?: string
  wpVersion?: string
  phpVersion: string
  settings: {
    maintenanceMode: boolean
    seoEnabled: boolean
    analyticsId?: string
    cacheEnabled: boolean
    compressionEnabled: boolean
  }
}

export interface CreateSiteData {
  name: string
  domain: string
  subdomain?: string
  plan: Site['plan']
  category: string
  theme?: string
  description?: string
  ownerEmail: string
  customDomain?: string
}

export interface UpdateSiteData extends Partial<CreateSiteData> {
  id: number
  status?: Site['status']
  settings?: Partial<Site['settings']>
}

interface SiteFilters {
  status?: Site['status']
  plan?: Site['plan']
  category?: string
  search?: string
}

// Mock data generator for sites
const generateMockSites = (count: number): Site[] => {
  const statuses: Site['status'][] = ['active', 'inactive', 'maintenance', 'suspended']
  const plans: Site['plan'][] = ['basic', 'pro', 'enterprise']
  const categories = ['e-commerce', 'blog', 'portfolio', 'corporate', 'landing-page', 'news']
  const themes = ['twentytwentyfour', 'astra', 'generatepress', 'storefront', 'kadence']
  const owners = ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Lima']
  const emails = ['joao@email.com', 'maria@email.com', 'pedro@email.com', 'ana@email.com', 'carlos@email.com']
  const phpVersions = ['8.1', '8.2', '8.3']
  const wpVersions = ['6.4.1', '6.4.2', '6.5.0']

  return Array.from({ length: count }, (_, i) => {
    const plan = plans[Math.floor(Math.random() * plans.length)]
    return {
      id: i + 1,
      name: `Site ${i + 1}`,
      domain: `site-${i + 1}.exemplo.com`,
      subdomain: `site-${i + 1}`,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      plan,
      visitors: Math.floor(Math.random() * 10000) + 100,
      createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
      lastUpdate: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
      owner: owners[Math.floor(Math.random() * owners.length)],
      ownerEmail: emails[Math.floor(Math.random() * emails.length)],
      description: `Descrição do site ${i + 1} - Um projeto incrível com foco em ${categories[Math.floor(Math.random() * categories.length)]}.`,
      category: categories[Math.floor(Math.random() * categories.length)],
      theme: themes[Math.floor(Math.random() * themes.length)],
      plugins: ['akismet', 'jetpack', 'yoast-seo'].slice(0, Math.floor(Math.random() * 3) + 1),
      ssl: Math.random() > 0.1, // 90% have SSL
      backups: Math.floor(Math.random() * 30) + 1,
      storage: Math.floor(Math.random() * (plan === 'basic' ? 1000 : plan === 'pro' ? 5000 : 10000)) + 100,
      bandwidth: Math.floor(Math.random() * (plan === 'basic' ? 50 : plan === 'pro' ? 200 : 500)) + 10,
      customDomain: Math.random() > 0.7 ? `${i + 1}-custom.com` : undefined,
      wpVersion: wpVersions[Math.floor(Math.random() * wpVersions.length)],
      phpVersion: phpVersions[Math.floor(Math.random() * phpVersions.length)],
      settings: {
        maintenanceMode: Math.random() > 0.9,
        seoEnabled: Math.random() > 0.2,
        analyticsId: Math.random() > 0.5 ? `GA-${Math.random().toString(36).substr(2, 9)}` : undefined,
        cacheEnabled: Math.random() > 0.3,
        compressionEnabled: Math.random() > 0.4,
      },
    }
  })
}

const mockSites = generateMockSites(150)

// Simulate API delays
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export function useSites() {
  const [sites, setSites] = useState<Site[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>()

  // Fetch sites with filters
  const fetchSites = useCallback(async (filters?: SiteFilters) => {
    setLoading(true)
    setError(undefined)

    try {
      await delay(500) // Simulate API call

      let filteredSites = [...mockSites]

      if (filters?.status) {
        filteredSites = filteredSites.filter((site) => site.status === filters.status)
      }

      if (filters?.plan) {
        filteredSites = filteredSites.filter((site) => site.plan === filters.plan)
      }

      if (filters?.category) {
        filteredSites = filteredSites.filter((site) => site.category === filters.category)
      }

      if (filters?.search) {
        const searchLower = filters.search.toLowerCase()
        filteredSites = filteredSites.filter(
          (site) =>
            site.name.toLowerCase().includes(searchLower) ||
            site.domain.toLowerCase().includes(searchLower) ||
            site.owner.toLowerCase().includes(searchLower) ||
            site.ownerEmail.toLowerCase().includes(searchLower)
        )
      }

      setSites(filteredSites)
    } catch (err) {
      setError('Erro ao carregar sites')
      console.error('Failed to fetch sites:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Create site
  const createSite = useCallback(async (data: CreateSiteData): Promise<Site> => {
    setLoading(true)
    try {
      await delay(1000)

      const newSite: Site = {
        id: mockSites.length + 1,
        name: data.name,
        domain: data.domain,
        subdomain: data.subdomain,
        status: 'active',
        plan: data.plan,
        visitors: 0,
        createdAt: new Date(),
        lastUpdate: new Date(),
        owner: 'Current User',
        ownerEmail: data.ownerEmail,
        description: data.description,
        category: data.category,
        theme: data.theme || 'twentytwentyfour',
        plugins: ['akismet'],
        ssl: true,
        backups: 0,
        storage: 100,
        bandwidth: 0,
        customDomain: data.customDomain,
        wpVersion: '6.5.0',
        phpVersion: '8.2',
        settings: {
          maintenanceMode: false,
          seoEnabled: true,
          cacheEnabled: true,
          compressionEnabled: true,
        },
      }

      mockSites.push(newSite)
      setSites((prev) => [...prev, newSite])

      return newSite
    } catch (err) {
      setError('Erro ao criar site')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // Update site
  const updateSite = useCallback(async (data: UpdateSiteData): Promise<Site> => {
    setLoading(true)
    try {
      await delay(800)

      const siteIndex = mockSites.findIndex((site) => site.id === data.id)
      if (siteIndex === -1) {
        throw new Error('Site não encontrado')
      }

      const updatedSite = {
        ...mockSites[siteIndex],
        ...data,
        lastUpdate: new Date(),
        settings: {
          ...mockSites[siteIndex].settings,
          ...(data.settings || {}),
        },
      }

      mockSites[siteIndex] = updatedSite
      setSites((prev) => prev.map((site) => (site.id === data.id ? updatedSite : site)))

      return updatedSite
    } catch (err) {
      setError('Erro ao atualizar site')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // Delete site
  const deleteSite = useCallback(async (id: number): Promise<void> => {
    setLoading(true)
    try {
      await delay(600)

      const siteIndex = mockSites.findIndex((site) => site.id === id)
      if (siteIndex === -1) {
        throw new Error('Site não encontrado')
      }

      mockSites.splice(siteIndex, 1)
      setSites((prev) => prev.filter((site) => site.id !== id))
    } catch (err) {
      setError('Erro ao excluir site')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // Get site by ID
  const getSite = useCallback(async (id: number): Promise<Site | null> => {
    setLoading(true)
    try {
      await delay(300)

      const site = mockSites.find((site) => site.id === id)
      return site || null
    } catch (err) {
      setError('Erro ao buscar site')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // Bulk operations
  const bulkUpdateStatus = useCallback(async (ids: number[], status: Site['status']): Promise<void> => {
    setLoading(true)
    try {
      await delay(1000)

      ids.forEach((id) => {
        const siteIndex = mockSites.findIndex((site) => site.id === id)
        if (siteIndex !== -1) {
          mockSites[siteIndex].status = status
          mockSites[siteIndex].lastUpdate = new Date()
        }
      })

      setSites((prev) =>
        prev.map((site) => (ids.includes(site.id) ? { ...site, status, lastUpdate: new Date() } : site))
      )
    } catch (err) {
      setError('Erro ao atualizar sites em lote')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const bulkDelete = useCallback(async (ids: number[]): Promise<void> => {
    setLoading(true)
    try {
      await delay(1200)

      ids.forEach((id) => {
        const siteIndex = mockSites.findIndex((site) => site.id === id)
        if (siteIndex !== -1) {
          mockSites.splice(siteIndex, 1)
        }
      })

      setSites((prev) => prev.filter((site) => !ids.includes(site.id)))
    } catch (err) {
      setError('Erro ao excluir sites em lote')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // Load initial data
  useEffect(() => {
    fetchSites()
  }, [fetchSites])

  return {
    sites,
    loading,
    error,
    fetchSites,
    createSite,
    updateSite,
    deleteSite,
    getSite,
    bulkUpdateStatus,
    bulkDelete,
    refetch: fetchSites,
  }
}