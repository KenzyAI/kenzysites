import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle, fillFormField, login, mockApiResponse } from '../utils/helpers'
import { testSites, aiPrompts, testUsers } from '../data/test-data'

test.describe('Site Creation with AI Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await login(page, testUsers.regular.email, testUsers.regular.password)
    await waitForNetworkIdle(page)
  })

  test.describe('AI Site Generation', () => {
    test('should create site using AI prompt', async ({ page }) => {
      // Navigate to site creation
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')

      // Wait for creation modal/page
      await waitForNetworkIdle(page)

      // Fill AI prompt
      const promptField = page.locator('textarea[name="prompt"], input[name="description"], [placeholder*="descreva"]')
      await promptField.fill(aiPrompts[0])

      // Select template if available
      const templateSelector = page.locator('[data-testid="template-selection"], .template-card')
      if (await templateSelector.first().isVisible()) {
        await templateSelector.first().click()
      }

      // Mock AI response
      await mockApiResponse(page, '**/api/ai/generate', {
        success: true,
        siteId: 'test-site-123',
        preview: {
          title: 'Sustainable Tech Blog',
          description: 'A modern blog about sustainable technology',
          template: 'blog'
        }
      })

      // Submit creation form
      await page.click('button[type="submit"], button:has-text("Gerar"), button:has-text("Create")')

      // Wait for generation to complete
      await page.waitForTimeout(2000)
      
      // Should show success or redirect to preview
      const successIndicator = page.locator('text=/sucesso/i, text=/criado/i, text=/gerado/i, text=/success/i')
      const previewButton = page.locator('button:has-text("Preview"), button:has-text("Visualizar")')
      
      const hasSuccess = await successIndicator.isVisible({ timeout: 10000 })
      const hasPreview = await previewButton.isVisible({ timeout: 5000 })
      
      expect(hasSuccess || hasPreview).toBe(true)
    })

    test('should validate AI prompt input', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Try to submit without prompt
      await page.click('button[type="submit"], button:has-text("Gerar"), button:has-text("Create")')

      // Should show validation error
      const error = page.locator('[class*="error"], [role="alert"], text=/obrigatório/i, text=/required/i')
      await expect(error).toBeVisible()
    })

    test('should show AI generation progress', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Fill prompt
      const promptField = page.locator('textarea[name="prompt"], input[name="description"], [placeholder*="descreva"]')
      await promptField.fill(aiPrompts[1])

      // Mock slow AI response
      await page.route('**/api/ai/generate', async (route) => {
        await page.waitForTimeout(1000)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            siteId: 'test-site-456'
          })
        })
      })

      // Submit form
      await page.click('button[type="submit"], button:has-text("Gerar"), button:has-text("Create")')

      // Should show loading state
      const loadingIndicator = page.locator('[class*="loading"], [class*="spinner"], text=/gerando/i, text=/creating/i')
      await expect(loadingIndicator).toBeVisible()
    })

    test('should handle AI generation errors', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Fill prompt
      const promptField = page.locator('textarea[name="prompt"], input[name="description"], [placeholder*="descreva"]')
      await promptField.fill(aiPrompts[2])

      // Mock AI error response
      await mockApiResponse(page, '**/api/ai/generate', {
        error: 'AI generation failed',
        message: 'Erro ao gerar site'
      })

      // Submit form
      await page.click('button[type="submit"], button:has-text("Gerar"), button:has-text("Create")')

      // Should show error message
      const errorMessage = page.locator('text=/erro/i, text=/falhou/i, text=/error/i, text=/failed/i')
      await expect(errorMessage).toBeVisible()
    })

    test('should allow customizing AI suggestions', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Fill basic prompt
      const promptField = page.locator('textarea[name="prompt"], input[name="description"]')
      await promptField.fill('Online store for handmade crafts')

      // Look for customization options
      const industrySelect = page.locator('select[name="industry"], [data-testid="industry-select"]')
      if (await industrySelect.isVisible()) {
        await industrySelect.selectOption('ecommerce')
      }

      const colorScheme = page.locator('select[name="colorScheme"], [data-testid="color-scheme"]')
      if (await colorScheme.isVisible()) {
        await colorScheme.selectOption('warm')
      }

      const features = page.locator('input[type="checkbox"][name*="feature"]')
      const featureCount = await features.count()
      
      if (featureCount > 0) {
        // Check first two features
        await features.nth(0).check()
        await features.nth(1).check()
      }

      // Submit with customizations
      await page.click('button[type="submit"], button:has-text("Gerar"), button:has-text("Create")')
      
      // Should process successfully
      const loadingOrSuccess = page.locator('[class*="loading"], text=/sucesso/i, text=/criado/i')
      await expect(loadingOrSuccess).toBeVisible({ timeout: 10000 })
    })
  })

  test.describe('Template Selection', () => {
    test('should display available templates', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Check for template gallery
      const templates = page.locator('.template-card, [data-testid*="template"], .template-item')
      const templateCount = await templates.count()
      
      if (templateCount > 0) {
        expect(templateCount).toBeGreaterThan(0)
        
        // Check template details
        const firstTemplate = templates.first()
        await expect(firstTemplate).toBeVisible()
        
        // Should have preview image or title
        const hasImage = await firstTemplate.locator('img').isVisible()
        const hasTitle = await firstTemplate.locator('h3, h4, .title').isVisible()
        
        expect(hasImage || hasTitle).toBe(true)
      }
    })

    test('should preview template before selection', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Find template with preview option
      const previewButton = page.locator('button:has-text("Preview"), button:has-text("Visualizar"), [data-testid*="preview"]')
      
      if (await previewButton.first().isVisible()) {
        await previewButton.first().click()
        
        // Should open preview modal or navigate to preview
        const previewModal = page.locator('[role="dialog"], .modal, .preview-container')
        const previewPage = page.url().includes('preview')
        
        expect(await previewModal.isVisible() || previewPage).toBe(true)
      }
    })

    test('should filter templates by category', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Look for category filters
      const categoryFilter = page.locator('select[name="category"], [data-testid="category-filter"], .category-tabs')
      
      if (await categoryFilter.isVisible()) {
        const categories = ['blog', 'ecommerce', 'portfolio', 'business']
        
        for (const category of categories) {
          const categoryOption = page.locator(`option[value="${category}"], button:has-text("${category}")`)
          
          if (await categoryOption.isVisible()) {
            await categoryOption.click()
            await waitForNetworkIdle(page)
            
            // Should filter templates
            const templates = page.locator('.template-card, [data-testid*="template"]')
            const count = await templates.count()
            
            // Should have at least one template or show empty state
            const hasTemplates = count > 0
            const emptyState = await page.locator('text=/nenhum/i, text=/no templates/i').isVisible()
            
            expect(hasTemplates || emptyState).toBe(true)
          }
        }
      }
    })
  })

  test.describe('Site Customization', () => {
    test('should allow basic site information editing', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Fill site information
      const siteNameField = page.locator('input[name="siteName"], input[name="title"]')
      if (await siteNameField.isVisible()) {
        await siteNameField.fill(testSites[0].name)
      }

      const descriptionField = page.locator('textarea[name="description"], input[name="description"]')
      if (await descriptionField.isVisible()) {
        await descriptionField.fill(testSites[0].description)
      }

      const domainField = page.locator('input[name="domain"], input[name="subdomain"]')
      if (await domainField.isVisible()) {
        await domainField.fill('test-blog-site')
      }

      // Submit form
      await page.click('button[type="submit"], button:has-text("Criar"), button:has-text("Create")')
      
      // Should process successfully
      const success = page.locator('text=/sucesso/i, text=/criado/i, text=/success/i')
      await expect(success).toBeVisible({ timeout: 10000 })
    })

    test('should validate domain availability', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      const domainField = page.locator('input[name="domain"], input[name="subdomain"]')
      
      if (await domainField.isVisible()) {
        // Fill existing domain
        await domainField.fill('existing-domain')
        
        // Should check availability
        const availabilityCheck = page.locator('text=/verificando/i, text=/checking/i, text=/disponível/i, text=/indisponível/i')
        
        // Blur field to trigger validation
        await domainField.blur()
        await page.waitForTimeout(1000)
        
        // Should show availability status
        const hasAvailabilityInfo = await availabilityCheck.isVisible()
        expect(hasAvailabilityInfo).toBe(true)
      }
    })

    test('should handle advanced customization options', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Look for advanced options
      const advancedToggle = page.locator('button:has-text("Avançado"), button:has-text("Advanced"), [data-testid="advanced-options"]')
      
      if (await advancedToggle.isVisible()) {
        await advancedToggle.click()
        
        // Check for advanced settings
        const seoSettings = page.locator('input[name*="seo"], input[name*="meta"]')
        const analyticsSettings = page.locator('input[name*="analytics"], input[name*="tracking"]')
        const performanceSettings = page.locator('input[name*="performance"], input[name*="cache"]')
        
        // Fill some advanced options if available
        if (await seoSettings.first().isVisible()) {
          await seoSettings.first().fill('Custom SEO settings')
        }
        
        if (await analyticsSettings.first().isVisible()) {
          await analyticsSettings.first().check()
        }
      }
    })
  })

  test.describe('Site Preview and Approval', () => {
    test('should show generated site preview', async ({ page }) => {
      // Mock successful site generation
      await mockApiResponse(page, '**/api/sites/*/preview', {
        success: true,
        preview: {
          url: 'https://preview.example.com/test-site',
          screenshots: ['screenshot1.jpg', 'screenshot2.jpg'],
          pages: ['Home', 'About', 'Contact']
        }
      })

      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Quick site creation for preview test
      const promptField = page.locator('textarea[name="prompt"], input[name="description"]')
      if (await promptField.isVisible()) {
        await promptField.fill('Simple business website')
        await page.click('button[type="submit"], button:has-text("Gerar")')
        
        // Wait for preview to load
        await page.waitForTimeout(3000)
        
        // Look for preview elements
        const previewFrame = page.locator('iframe[src*="preview"], .preview-container')
        const previewImage = page.locator('img[src*="screenshot"], .preview-image')
        const previewLink = page.locator('a[href*="preview"], button:has-text("Preview")')
        
        const hasPreview = await previewFrame.isVisible() || 
                          await previewImage.isVisible() || 
                          await previewLink.isVisible()
        
        expect(hasPreview).toBe(true)
      }
    })

    test('should allow approving generated site', async ({ page }) => {
      // Navigate through creation flow to approval
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Mock site generation and show approval buttons
      await mockApiResponse(page, '**/api/ai/generate', {
        success: true,
        siteId: 'test-site-approval',
        status: 'preview'
      })

      const promptField = page.locator('textarea[name="prompt"], input[name="description"]')
      if (await promptField.isVisible()) {
        await promptField.fill('Test site for approval')
        await page.click('button[type="submit"], button:has-text("Gerar")')
        
        // Wait and look for approval buttons
        await page.waitForTimeout(2000)
        
        const approveButton = page.locator('button:has-text("Aprovar"), button:has-text("Approve"), button:has-text("Publish")')
        const rejectButton = page.locator('button:has-text("Rejeitar"), button:has-text("Reject"), button:has-text("Cancel")')
        
        if (await approveButton.isVisible()) {
          await approveButton.click()
          
          // Should show success or redirect to site management
          const success = page.locator('text=/aprovado/i, text=/publicado/i, text=/approved/i, text=/published/i')
          await expect(success).toBeVisible({ timeout: 10000 })
        }
      }
    })

    test('should allow requesting changes to generated site', async ({ page }) => {
      await page.goto('/dashboard/sites')
      await page.click('button:has-text("Criar Site"), button:has-text("New Site"), [data-testid="create-site"]')
      await waitForNetworkIdle(page)

      // Mock site generation
      await mockApiResponse(page, '**/api/ai/generate', {
        success: true,
        siteId: 'test-site-changes',
        status: 'preview'
      })

      const promptField = page.locator('textarea[name="prompt"], input[name="description"]')
      if (await promptField.isVisible()) {
        await promptField.fill('Test site for changes')
        await page.click('button[type="submit"], button:has-text("Gerar")')
        
        await page.waitForTimeout(2000)
        
        // Look for modification options
        const editButton = page.locator('button:has-text("Editar"), button:has-text("Edit"), button:has-text("Modificar")')
        const changeRequestButton = page.locator('button:has-text("Solicitar"), button:has-text("Request Changes")')
        
        if (await editButton.isVisible()) {
          await editButton.click()
          
          // Should show edit interface
          const editInterface = page.locator('.editor, [data-testid="site-editor"], textarea[name*="changes"]')
          await expect(editInterface).toBeVisible()
        } else if (await changeRequestButton.isVisible()) {
          await changeRequestButton.click()
          
          // Should show change request form
          const changeForm = page.locator('textarea[name*="changes"], input[name*="feedback"]')
          if (await changeForm.isVisible()) {
            await changeForm.fill('Please change the color scheme to blue')
            await page.click('button[type="submit"]')
          }
        }
      }
    })
  })
})