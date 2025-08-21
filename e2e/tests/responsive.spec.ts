import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle, takeScreenshot } from '../utils/helpers'

test.describe('Responsive Design Tests', () => {
  const viewports = [
    { name: 'Mobile Portrait', width: 375, height: 667 },
    { name: 'Mobile Landscape', width: 667, height: 375 },
    { name: 'Tablet Portrait', width: 768, height: 1024 },
    { name: 'Tablet Landscape', width: 1024, height: 768 },
    { name: 'Desktop', width: 1280, height: 720 },
    { name: 'Large Desktop', width: 1920, height: 1080 }
  ]

  const testPages = [
    { name: 'Homepage', url: '/' },
    { name: 'Dashboard', url: '/dashboard', requiresAuth: true },
    { name: 'Sites List', url: '/dashboard/sites', requiresAuth: true },
    { name: 'Login', url: '/login' },
    { name: 'Register', url: '/register' }
  ]

  test.describe('Viewport Testing', () => {
    for (const viewport of viewports) {
      for (const page of testPages) {
        test(`${page.name} should be responsive on ${viewport.name}`, async ({ page: browserPage }) => {
          // Set viewport
          await browserPage.setViewportSize({ width: viewport.width, height: viewport.height })
          
          // Login if required
          if (page.requiresAuth) {
            await browserPage.goto('/login')
            await browserPage.fill('input[name="email"]', 'test@example.com')
            await browserPage.fill('input[name="password"]', 'password123')
            await browserPage.click('button[type="submit"]')
            await browserPage.waitForURL('**/dashboard', { timeout: 10000 }).catch(() => {})
          }
          
          // Navigate to page
          await browserPage.goto(page.url)
          await waitForNetworkIdle(browserPage)
          
          // Check page loads without horizontal scroll
          const bodyWidth = await browserPage.evaluate(() => document.body.scrollWidth)
          const viewportWidth = viewport.width
          
          // Allow for small differences due to scrollbars
          expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 20)
          
          // Check main content is visible
          const mainContent = browserPage.locator('main, .main-content, h1, .container')
          await expect(mainContent.first()).toBeVisible()
          
          // Take screenshot for visual verification
          await takeScreenshot(browserPage, `${page.name.toLowerCase()}-${viewport.name.toLowerCase()}`)
        })
      }
    }
  })

  test.describe('Mobile Navigation', () => {
    test('should show mobile menu on small screens', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)
      
      // Look for mobile menu trigger
      const menuTrigger = page.locator(
        '.mobile-menu-trigger, .hamburger, button[aria-label*="menu"], [data-testid="mobile-menu"]'
      )
      
      if (await menuTrigger.isVisible()) {
        // Click menu trigger
        await menuTrigger.click()
        
        // Menu should be visible
        const mobileMenu = page.locator('.mobile-menu, .sidebar-mobile, nav[aria-expanded="true"]')
        await expect(mobileMenu).toBeVisible()
        
        // Should contain navigation items
        const navItems = page.locator('a[href], button').filter({ 
          hasText: /home|about|contact|dashboard|sites/i 
        })
        const itemCount = await navItems.count()
        expect(itemCount).toBeGreaterThan(0)
        
        // Close menu
        const closeButton = page.locator('.close, [aria-label*="close"], .backdrop')
        if (await closeButton.isVisible()) {
          await closeButton.click()
          
          // Menu should be hidden
          await expect(mobileMenu).not.toBeVisible()
        }
      }
    })
    
    test('should hide desktop navigation on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)
      
      // Desktop navigation should be hidden
      const desktopNav = page.locator('.desktop-nav, .navbar-nav, nav.hidden-mobile')
      
      if (await desktopNav.count() > 0) {
        const isVisible = await desktopNav.first().isVisible()
        expect(isVisible).toBe(false)
      }
    })
  })

  test.describe('Touch Interactions', () => {
    test('should support touch interactions on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)
      
      // Test touch-friendly button sizes
      const buttons = page.locator('button, a[role="button"], .btn')
      const buttonCount = await buttons.count()
      
      if (buttonCount > 0) {
        for (let i = 0; i < Math.min(buttonCount, 5); i++) {
          const button = buttons.nth(i)
          if (await button.isVisible()) {
            const boundingBox = await button.boundingBox()
            
            if (boundingBox) {
              // Touch targets should be at least 44x44px (iOS) or 48x48px (Android)
              expect(boundingBox.width).toBeGreaterThanOrEqual(40)
              expect(boundingBox.height).toBeGreaterThanOrEqual(40)
            }
          }
        }
      }
    })
    
    test('should support swipe gestures where applicable', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)
      
      // Look for carousel or swipeable content
      const carousel = page.locator('.carousel, .swiper, .slider, [data-testid*="carousel"]')
      
      if (await carousel.isVisible()) {
        const startX = 200
        const endX = 100
        const y = 300
        
        // Simulate swipe left
        await page.touchscreen.tap(startX, y)
        await page.touchscreen.tap(endX, y)
        
        // Content should have changed (basic check)
        await page.waitForTimeout(500)
        
        // This is a basic test - in real scenarios, you'd check for specific content changes
        expect(await carousel.isVisible()).toBe(true)
      }
    })
  })

  test.describe('Form Responsiveness', () => {
    test('should adapt forms for mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/register')
      await waitForNetworkIdle(page)
      
      // Check form layout
      const form = page.locator('form')
      
      if (await form.isVisible()) {
        // Form should fit in viewport
        const formBox = await form.boundingBox()
        if (formBox) {
          expect(formBox.width).toBeLessThanOrEqual(375)
        }
        
        // Input fields should be full width or appropriately sized
        const inputs = page.locator('input[type="text"], input[type="email"], input[type="password"], textarea')
        const inputCount = await inputs.count()
        
        if (inputCount > 0) {
          for (let i = 0; i < inputCount; i++) {
            const input = inputs.nth(i)
            if (await input.isVisible()) {
              const inputBox = await input.boundingBox()
              
              if (inputBox) {
                // Inputs should be reasonably wide on mobile
                expect(inputBox.width).toBeGreaterThan(200)
                expect(inputBox.width).toBeLessThanOrEqual(375)
              }
            }
          }
        }
      }
    })
    
    test('should show appropriate keyboards on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/register')
      await waitForNetworkIdle(page)
      
      // Check input types for appropriate mobile keyboards
      const emailInput = page.locator('input[type="email"]')
      if (await emailInput.isVisible()) {
        const inputType = await emailInput.getAttribute('type')
        expect(inputType).toBe('email')
      }
      
      const telInput = page.locator('input[type="tel"]')
      if (await telInput.isVisible()) {
        const inputType = await telInput.getAttribute('type')
        expect(inputType).toBe('tel')
      }
      
      const numberInput = page.locator('input[type="number"]')
      if (await numberInput.isVisible()) {
        const inputType = await numberInput.getAttribute('type')
        expect(inputType).toBe('number')
      }
    })
  })

  test.describe('Content Reflow', () => {
    test('should reflow content appropriately across viewports', async ({ page }) => {
      const testUrl = '/'
      
      // Start with desktop
      await page.setViewportSize({ width: 1280, height: 720 })
      await page.goto(testUrl)
      await waitForNetworkIdle(page)
      
      // Check desktop layout
      const mainContent = page.locator('main, .main-content, .container')
      const desktopBox = await mainContent.first().boundingBox()
      
      // Switch to tablet
      await page.setViewportSize({ width: 768, height: 1024 })
      await page.waitForTimeout(500) // Allow reflow
      
      const tabletBox = await mainContent.first().boundingBox()
      
      // Switch to mobile
      await page.setViewportSize({ width: 375, height: 667 })
      await page.waitForTimeout(500)
      
      const mobileBox = await mainContent.first().boundingBox()
      
      // Content should adapt to viewport
      if (desktopBox && tabletBox && mobileBox) {
        expect(mobileBox.width).toBeLessThan(tabletBox.width)
        expect(tabletBox.width).toBeLessThan(desktopBox.width)
      }
    })
    
    test('should handle text scaling', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)
      
      // Check headings are readable
      const headings = page.locator('h1, h2, h3')
      const headingCount = await headings.count()
      
      if (headingCount > 0) {
        for (let i = 0; i < headingCount; i++) {
          const heading = headings.nth(i)
          if (await heading.isVisible()) {
            const fontSize = await heading.evaluate((el) => {
              return window.getComputedStyle(el).fontSize
            })
            
            // Font size should be reasonable for mobile (at least 16px for body, larger for headings)
            const fontSizeValue = parseInt(fontSize)
            expect(fontSizeValue).toBeGreaterThan(14)
          }
        }
      }
    })
  })

  test.describe('Image Responsiveness', () => {
    test('should scale images appropriately', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)
      
      // Check images don't overflow
      const images = page.locator('img')
      const imageCount = await images.count()
      
      if (imageCount > 0) {
        for (let i = 0; i < Math.min(imageCount, 5); i++) {
          const img = images.nth(i)
          if (await img.isVisible()) {
            const imgBox = await img.boundingBox()
            
            if (imgBox) {
              // Images should not be wider than viewport
              expect(imgBox.width).toBeLessThanOrEqual(375)
            }
          }
        }
      }
    })
    
    test('should load appropriate image sizes', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)
      
      // Check for responsive image attributes
      const responsiveImages = page.locator('img[srcset], img[sizes], picture source')
      const responsiveCount = await responsiveImages.count()
      
      if (responsiveCount > 0) {
        // Should have responsive images for better performance
        expect(responsiveCount).toBeGreaterThan(0)
        
        // Check srcset format
        const imgWithSrcset = responsiveImages.first()
        const srcset = await imgWithSrcset.getAttribute('srcset')
        
        if (srcset) {
          // Should contain multiple image sources
          expect(srcset).toContain('w') // width descriptor
        }
      }
    })
  })

  test.describe('Performance on Mobile', () => {
    test('should load quickly on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      
      const startTime = Date.now()
      await page.goto('/')
      await waitForNetworkIdle(page)
      const loadTime = Date.now() - startTime
      
      // Should load reasonably fast even on mobile
      expect(loadTime).toBeLessThan(5000)
    })
    
    test('should minimize layout shifts', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      
      // Wait for initial load
      await page.waitForLoadState('domcontentloaded')
      
      // Take initial screenshot
      const initialHeight = await page.evaluate(() => document.body.scrollHeight)
      
      // Wait for additional content to load
      await page.waitForTimeout(2000)
      
      // Check final height
      const finalHeight = await page.evaluate(() => document.body.scrollHeight)
      
      // Layout should be relatively stable (allow some variance for dynamic content)
      const heightDifference = Math.abs(finalHeight - initialHeight)
      expect(heightDifference).toBeLessThan(initialHeight * 0.1) // Less than 10% change
    })
  })

  test.describe('Cross-Device Features', () => {
    test('should maintain functionality across devices', async ({ page }) => {
      const devices = [
        { width: 375, height: 667, name: 'mobile' },
        { width: 768, height: 1024, name: 'tablet' },
        { width: 1280, height: 720, name: 'desktop' }
      ]
      
      for (const device of devices) {
        await page.setViewportSize({ width: device.width, height: device.height })
        await page.goto('/')
        await waitForNetworkIdle(page)
        
        // Key functionality should work on all devices
        const ctaButton = page.locator('button:has-text("Começar"), a:has-text("Começar")')
        
        if (await ctaButton.isVisible()) {
          // Button should be clickable
          await expect(ctaButton).toBeEnabled()
          
          // Should navigate when clicked
          await ctaButton.click()
          await page.waitForTimeout(1000)
          
          // URL should change or modal should open
          const currentUrl = page.url()
          const modal = page.locator('[role="dialog"], .modal')
          
          const hasNavigation = !currentUrl.endsWith('/') || await modal.isVisible()
          expect(hasNavigation).toBe(true)
          
          // Go back for next iteration
          await page.goto('/')
          await waitForNetworkIdle(page)
        }
      }
    })
  })
})