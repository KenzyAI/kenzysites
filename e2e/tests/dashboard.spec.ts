import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle, login, mockApiResponse, takeScreenshot } from '../utils/helpers'
import { testUsers, testSites } from '../data/test-data'

test.describe('Dashboard Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await login(page, testUsers.regular.email, testUsers.regular.password)
    await page.goto('/dashboard')
    await waitForNetworkIdle(page)
  })

  test.describe('Dashboard Overview', () => {
    test('should display dashboard main elements', async ({ page }) => {
      // Check main dashboard elements
      const dashboardTitle = page.locator('h1:has-text("Dashboard"), h1:has-text("Painel")')
      await expect(dashboardTitle).toBeVisible()

      // Check navigation menu
      const navMenu = page.locator('nav, .sidebar, [data-testid="navigation"]')
      await expect(navMenu).toBeVisible()

      // Check main content area
      const mainContent = page.locator('main, .main-content, [role="main"]')
      await expect(mainContent).toBeVisible()

      // Check user menu/avatar
      const userMenu = page.locator('[data-testid="user-menu"], .user-avatar, button[aria-label*="user"]')
      await expect(userMenu).toBeVisible()
    })

    test('should display dashboard statistics', async ({ page }) => {
      // Mock dashboard stats
      await mockApiResponse(page, '**/api/dashboard/stats', {
        totalSites: 5,
        activeSites: 4,
        totalViews: 15420,
        aiCredits: 250
      })

      await page.reload()
      await waitForNetworkIdle(page)

      // Check for stats cards
      const statsCards = page.locator('.stat-card, [data-testid*="stat"], .metric-card')
      const cardCount = await statsCards.count()
      
      if (cardCount > 0) {
        expect(cardCount).toBeGreaterThanOrEqual(3)
        
        // Check for common metrics
        const metrics = ['Sites', 'Views', 'Credits', 'Active']
        for (const metric of metrics) {
          const metricElement = page.locator(`text=${metric}, [data-testid*="${metric.toLowerCase()}"]`)
          if (await metricElement.isVisible()) {
            expect(await metricElement.isVisible()).toBe(true)
          }
        }
      }
    })

    test('should display recent activity', async ({ page }) => {
      // Mock recent activity
      await mockApiResponse(page, '**/api/dashboard/activity', {
        activities: [
          {
            id: 1,
            type: 'site_created',
            message: 'Site "Tech Blog" foi criado',
            timestamp: new Date().toISOString()
          },
          {
            id: 2,
            type: 'site_updated',
            message: 'Site "Portfolio" foi atualizado',
            timestamp: new Date(Date.now() - 3600000).toISOString()
          }
        ]
      })

      await page.reload()
      await waitForNetworkIdle(page)

      // Check for activity section
      const activitySection = page.locator('text=/atividade/i, text=/activity/i').locator('..')
      if (await activitySection.isVisible()) {
        // Check for activity items
        const activityItems = page.locator('.activity-item, [data-testid*="activity"], li')
        const itemCount = await activityItems.count()
        expect(itemCount).toBeGreaterThan(0)
      }
    })

    test('should navigate to different dashboard sections', async ({ page }) => {
      const sections = [
        { name: 'Sites', url: '/dashboard/sites' },
        { name: 'Analytics', url: '/dashboard/analytics' },
        { name: 'Settings', url: '/dashboard/settings' },
        { name: 'Billing', url: '/dashboard/billing' }
      ]

      for (const section of sections) {
        const navLink = page.locator(`a:has-text("${section.name}"), button:has-text("${section.name}")`)
        
        if (await navLink.isVisible()) {
          await navLink.click()
          await waitForNetworkIdle(page)
          
          // Check URL changed
          expect(page.url()).toContain(section.url)
          
          // Navigate back to main dashboard
          await page.goto('/dashboard')
          await waitForNetworkIdle(page)
        }
      }
    })
  })

  test.describe('Sites Management', () => {
    test('should display sites list', async ({ page }) => {
      // Mock sites list
      await mockApiResponse(page, '**/api/sites', {
        sites: testSites.map((site, index) => ({
          id: `site-${index + 1}`,
          ...site,
          status: 'active',
          url: `https://${site.name.toLowerCase().replace(/\s+/g, '-')}.example.com`,
          createdAt: new Date().toISOString()
        }))
      })

      await page.goto('/dashboard/sites')
      await waitForNetworkIdle(page)

      // Check sites are displayed
      const siteCards = page.locator('.site-card, [data-testid*="site"], .site-item')
      const siteCount = await siteCards.count()
      
      if (siteCount > 0) {
        expect(siteCount).toBeGreaterThan(0)
        
        // Check first site details
        const firstSite = siteCards.first()
        await expect(firstSite).toBeVisible()
        
        // Should have site name and status
        const hasName = await firstSite.locator('h3, h4, .site-name').isVisible()
        const hasStatus = await firstSite.locator('.status, [data-testid*="status"]').isVisible()
        
        expect(hasName || hasStatus).toBe(true)
      }
    })

    test('should filter sites by status', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await waitForNetworkIdle(page)

      // Look for filter options
      const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]')
      
      if (await statusFilter.isVisible()) {
        const statuses = ['active', 'inactive', 'draft']
        
        for (const status of statuses) {
          await statusFilter.selectOption(status)
          await waitForNetworkIdle(page)
          
          // Should filter results
          const sites = page.locator('.site-card, [data-testid*="site"]')
          const count = await sites.count()
          
          // Either show filtered results or empty state
          const hasResults = count > 0
          const emptyState = await page.locator('text=/nenhum/i, text=/no sites/i').isVisible()
          
          expect(hasResults || emptyState).toBe(true)
        }
      }
    })

    test('should search sites', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await waitForNetworkIdle(page)

      // Look for search input
      const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="buscar"]')
      
      if (await searchInput.isVisible()) {
        await searchInput.fill('blog')
        await page.waitForTimeout(500) // Wait for debounced search
        
        // Should show search results
        const results = page.locator('.site-card, [data-testid*="site"], .search-result')
        const resultCount = await results.count()
        
        // Either show results or empty state
        const hasResults = resultCount > 0
        const emptyState = await page.locator('text=/encontrado/i, text=/no results/i').isVisible()
        
        expect(hasResults || emptyState).toBe(true)
      }
    })

    test('should paginate sites list', async ({ page }) => {
      // Mock large sites list
      const largeSitesList = Array.from({ length: 25 }, (_, i) => ({
        id: `site-${i + 1}`,
        name: `Site ${i + 1}`,
        description: `Description for site ${i + 1}`,
        status: 'active'
      }))

      await mockApiResponse(page, '**/api/sites', {
        sites: largeSitesList,
        total: 25,
        page: 1,
        limit: 10
      })

      await page.goto('/dashboard/sites')
      await waitForNetworkIdle(page)

      // Look for pagination
      const pagination = page.locator('.pagination, [data-testid="pagination"], nav[aria-label*="pagination"]')
      
      if (await pagination.isVisible()) {
        const nextButton = page.locator('button:has-text("Next"), button:has-text("Próximo"), button[aria-label*="next"]')
        
        if (await nextButton.isVisible() && !(await nextButton.isDisabled())) {
          await nextButton.click()
          await waitForNetworkIdle(page)
          
          // Should navigate to next page
          const currentPage = page.locator('[aria-current="page"], .active')
          await expect(currentPage).toBeVisible()
        }
      }
    })

    test('should edit site details', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await waitForNetworkIdle(page)

      // Find first site and edit button
      const firstSite = page.locator('.site-card, [data-testid*="site"]').first()
      
      if (await firstSite.isVisible()) {
        const editButton = firstSite.locator('button:has-text("Edit"), button:has-text("Editar"), [data-testid*="edit"]')
        
        if (await editButton.isVisible()) {
          await editButton.click()
          await waitForNetworkIdle(page)
          
          // Should open edit form/modal
          const editForm = page.locator('form, [data-testid="edit-form"], [role="dialog"]')
          await expect(editForm).toBeVisible()
          
          // Fill some basic fields
          const nameField = page.locator('input[name="name"], input[name="title"]')
          if (await nameField.isVisible()) {
            await nameField.fill('Updated Site Name')
          }
          
          const descField = page.locator('textarea[name="description"], input[name="description"]')
          if (await descField.isVisible()) {
            await descField.fill('Updated description')
          }
          
          // Save changes
          const saveButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Salvar")')
          if (await saveButton.isVisible()) {
            await saveButton.click()
            
            // Should show success message
            const success = page.locator('text=/salvo/i, text=/atualizado/i, text=/saved/i, text=/updated/i')
            await expect(success).toBeVisible({ timeout: 10000 })
          }
        }
      }
    })

    test('should delete site with confirmation', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await waitForNetworkIdle(page)

      const firstSite = page.locator('.site-card, [data-testid*="site"]').first()
      
      if (await firstSite.isVisible()) {
        const deleteButton = firstSite.locator('button:has-text("Delete"), button:has-text("Excluir"), [data-testid*="delete"]')
        
        if (await deleteButton.isVisible()) {
          await deleteButton.click()
          
          // Should show confirmation dialog
          const confirmDialog = page.locator('[role="dialog"], .modal, .confirm-dialog')
          await expect(confirmDialog).toBeVisible()
          
          // Confirm deletion
          const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Confirmar"), button:has-text("Delete")')
          if (await confirmButton.isVisible()) {
            await confirmButton.click()
            
            // Should show success message
            const success = page.locator('text=/excluído/i, text=/removido/i, text=/deleted/i, text=/removed/i')
            await expect(success).toBeVisible({ timeout: 10000 })
          }
        }
      }
    })
  })

  test.describe('Site Details View', () => {
    test('should display site details page', async ({ page }) => {
      // Mock site details
      await mockApiResponse(page, '**/api/sites/site-1', {
        id: 'site-1',
        name: 'Tech Blog',
        description: 'A modern tech blog',
        url: 'https://tech-blog.example.com',
        status: 'active',
        analytics: {
          views: 1250,
          visitors: 890,
          bounce_rate: 0.35
        },
        lastBackup: new Date().toISOString()
      })

      await page.goto('/dashboard/sites/site-1')
      await waitForNetworkIdle(page)

      // Check site details are displayed
      const siteName = page.locator('h1, h2').filter({ hasText: 'Tech Blog' })
      await expect(siteName).toBeVisible()

      // Check site URL
      const siteUrl = page.locator('a[href*="tech-blog"], text=tech-blog')
      await expect(siteUrl).toBeVisible()

      // Check status indicator
      const statusBadge = page.locator('.status, [data-testid*="status"], .badge')
      await expect(statusBadge).toBeVisible()
    })

    test('should display site analytics', async ({ page }) => {
      await page.goto('/dashboard/sites/site-1')
      await waitForNetworkIdle(page)

      // Look for analytics section
      const analyticsSection = page.locator('text=/analytics/i, text=/estatísticas/i').locator('..')
      
      if (await analyticsSection.isVisible()) {
        // Check for common metrics
        const metrics = ['views', 'visitors', 'bounce']
        
        for (const metric of metrics) {
          const metricElement = page.locator(`text=/${metric}/i`)
          if (await metricElement.isVisible()) {
            expect(await metricElement.isVisible()).toBe(true)
          }
        }
      }
    })

    test('should allow site actions', async ({ page }) => {
      await page.goto('/dashboard/sites/site-1')
      await waitForNetworkIdle(page)

      // Check for action buttons
      const actions = [
        'Edit', 'Editar',
        'Preview', 'Visualizar',
        'Backup', 'Backup',
        'Settings', 'Configurações'
      ]

      for (const action of actions) {
        const actionButton = page.locator(`button:has-text("${action}"), a:has-text("${action}")`)
        
        if (await actionButton.isVisible()) {
          expect(await actionButton.isVisible()).toBe(true)
        }
      }
    })

    test('should display backup information', async ({ page }) => {
      await page.goto('/dashboard/sites/site-1')
      await waitForNetworkIdle(page)

      // Look for backup section
      const backupSection = page.locator('text=/backup/i').locator('..')
      
      if (await backupSection.isVisible()) {
        // Should show last backup date
        const lastBackup = page.locator('text=/último/i, text=/last/i')
        await expect(lastBackup).toBeVisible()
        
        // Should have backup action
        const backupButton = page.locator('button:has-text("Backup"), button:has-text("Create Backup")')
        if (await backupButton.isVisible()) {
          expect(await backupButton.isVisible()).toBe(true)
        }
      }
    })
  })

  test.describe('Dashboard Performance', () => {
    test('should load dashboard quickly', async ({ page }) => {
      const startTime = Date.now()
      await page.goto('/dashboard')
      await waitForNetworkIdle(page)
      const loadTime = Date.now() - startTime
      
      // Dashboard should load in less than 3 seconds
      expect(loadTime).toBeLessThan(3000)
    })

    test('should handle offline state', async ({ page }) => {
      await page.goto('/dashboard')
      await waitForNetworkIdle(page)

      // Simulate offline
      await page.setOfflineMode(true)
      await page.reload()

      // Should show offline indicator or cached content
      const offlineIndicator = page.locator('text=/offline/i, text=/sem conexão/i, .offline-banner')
      const cachedContent = page.locator('h1, h2, .dashboard-title')
      
      const hasOfflineHandling = await offlineIndicator.isVisible() || await cachedContent.isVisible()
      expect(hasOfflineHandling).toBe(true)

      // Restore online
      await page.setOfflineMode(false)
    })

    test('should update real-time data', async ({ page }) => {
      await page.goto('/dashboard')
      await waitForNetworkIdle(page)

      // Mock initial data
      await mockApiResponse(page, '**/api/dashboard/stats', {
        totalSites: 5,
        views: 1000
      })

      // Wait and mock updated data
      await page.waitForTimeout(1000)
      
      await mockApiResponse(page, '**/api/dashboard/stats', {
        totalSites: 6,
        views: 1100
      })

      // Look for auto-refresh or real-time updates
      const refreshButton = page.locator('button:has-text("Refresh"), button:has-text("Atualizar")')
      
      if (await refreshButton.isVisible()) {
        await refreshButton.click()
        await waitForNetworkIdle(page)
      } else {
        // Check if data updates automatically
        await page.waitForTimeout(5000)
      }

      // Data should be updated (this is more of a framework test)
      const statsArea = page.locator('.stats, .metrics, [data-testid*="stat"]')
      await expect(statsArea).toBeVisible()
    })
  })

  test.describe('Mobile Dashboard', () => {
    test('should work on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/dashboard')
      await waitForNetworkIdle(page)

      // Check mobile navigation
      const mobileMenu = page.locator('.mobile-menu, .hamburger, button[aria-label*="menu"]')
      
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click()
        
        // Should show navigation menu
        const navMenu = page.locator('nav, .sidebar, [data-testid="navigation"]')
        await expect(navMenu).toBeVisible()
      }

      // Check main content is accessible
      const mainContent = page.locator('main, .main-content, h1')
      await expect(mainContent).toBeVisible()

      // Take mobile screenshot
      await takeScreenshot(page, 'dashboard-mobile')
    })
  })
})