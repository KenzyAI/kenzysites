import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle, checkAccessibility } from '../utils/helpers'
import { expectedContent } from '../data/test-data'

test.describe('Homepage Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await waitForNetworkIdle(page)
  })

  test('should display homepage with correct content', async ({ page }) => {
    // Check main heading
    const heading = page.locator('h1')
    await expect(heading).toContainText('Crie Sites WordPress')
    await expect(heading).toContainText('Inteligência Artificial')

    // Check description
    const description = page.locator('text=/Transforme suas ideias/')
    await expect(description).toBeVisible()

    // Check CTA buttons
    const ctaButton = page.locator('text=Começar Grátis')
    await expect(ctaButton).toBeVisible()
    
    const demoButton = page.locator('text=Ver Demo')
    await expect(demoButton).toBeVisible()

    // Check feature checkmarks
    await expect(page.locator('text=Sem cartão de crédito')).toBeVisible()
    await expect(page.locator('text=Setup em 3 minutos')).toBeVisible()
    await expect(page.locator('text=Suporte 24/7')).toBeVisible()
  })

  test('should display all feature cards', async ({ page }) => {
    const features = expectedContent.features
    
    for (const feature of features) {
      const card = page.locator(`text=${feature}`)
      await expect(card).toBeVisible()
    }
  })

  test('should display statistics section', async ({ page }) => {
    // Check stats
    await expect(page.locator('text=10.000+')).toBeVisible()
    await expect(page.locator('text=Sites Criados')).toBeVisible()
    
    await expect(page.locator('text=99.9%')).toBeVisible()
    await expect(page.locator('text=Uptime Garantido')).toBeVisible()
    
    await expect(page.locator('text=<3min')).toBeVisible()
    await expect(page.locator('text=Tempo de Criação')).toBeVisible()
    
    await expect(page.locator('text=24/7').first()).toBeVisible()
    await expect(page.locator('text=Suporte Premium')).toBeVisible()
  })

  test('should display testimonials', async ({ page }) => {
    // Check testimonials section
    const testimonialsSection = page.locator('text=O Que Nossos Clientes Dizem')
    await expect(testimonialsSection).toBeVisible()

    // Check for testimonial cards
    const testimonialCards = page.locator('[class*="card"]').filter({
      has: page.locator('.lucide-star')
    })
    
    const count = await testimonialCards.count()
    expect(count).toBeGreaterThanOrEqual(3)
  })

  test('should navigate to register page from CTA', async ({ page }) => {
    // Click on main CTA
    await page.click('text=Começar Grátis')
    await page.waitForURL('**/register')
    
    // Verify we're on register page
    const url = page.url()
    expect(url).toContain('/register')
  })

  test('should navigate to demo page', async ({ page }) => {
    // Click on demo button
    await page.click('text=Ver Demo')
    await page.waitForURL('**/demo')
    
    // Verify we're on demo page
    const url = page.url()
    expect(url).toContain('/demo')
  })

  test('should have proper SEO meta tags', async ({ page }) => {
    // Check title
    const title = await page.title()
    expect(title).toContain('WordPress')
    
    // Check meta description
    const metaDescription = await page.locator('meta[name="description"]').getAttribute('content')
    expect(metaDescription).toBeTruthy()
    
    // Check Open Graph tags
    const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content')
    expect(ogTitle).toBeTruthy()
  })

  test('should be accessible', async ({ page }) => {
    const accessibility = await checkAccessibility(page)
    
    // Check no images without alt text
    expect(accessibility.imagesWithoutAlt).toBe(0)
    
    // Check inputs have labels
    expect(accessibility.inputsWithoutLabels).toBe(0)
    
    // Check heading hierarchy
    expect(accessibility.headings.length).toBeGreaterThan(0)
  })

  test('should handle dark mode toggle', async ({ page }) => {
    // Find theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle"], button[aria-label*="theme"]')
    
    if (await themeToggle.isVisible()) {
      // Get initial theme
      const htmlElement = page.locator('html')
      const initialTheme = await htmlElement.getAttribute('class')
      
      // Toggle theme
      await themeToggle.click()
      await page.waitForTimeout(500) // Wait for animation
      
      // Check theme changed
      const newTheme = await htmlElement.getAttribute('class')
      expect(newTheme).not.toBe(initialTheme)
    }
  })

  test('should have working navigation links', async ({ page }) => {
    // Test navigation links if they exist
    const navLinks = [
      { text: 'Recursos', href: '#features' },
      { text: 'Preços', href: '#pricing' },
      { text: 'Sobre', href: '#about' },
      { text: 'Contato', href: '#contact' },
    ]
    
    for (const link of navLinks) {
      const element = page.locator(`a:has-text("${link.text}")`)
      if (await element.isVisible()) {
        const href = await element.getAttribute('href')
        expect(href).toBeTruthy()
      }
    }
  })

  test('should be responsive', async ({ page }) => {
    // Test different viewport sizes
    const viewports = [
      { width: 1920, height: 1080, name: 'Desktop' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 375, height: 667, name: 'Mobile' },
    ]
    
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
      await page.waitForTimeout(500)
      
      // Check main elements are visible
      const heading = page.locator('h1')
      await expect(heading).toBeVisible()
      
      // Check CTA button is visible
      const ctaButton = page.locator('text=Começar Grátis')
      await expect(ctaButton).toBeVisible()
    }
  })

  test('should load quickly', async ({ page }) => {
    const startTime = Date.now()
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    const loadTime = Date.now() - startTime
    
    // Page should load in less than 3 seconds
    expect(loadTime).toBeLessThan(3000)
  })
})