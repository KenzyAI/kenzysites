import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle, takeScreenshot } from '../utils/helpers'

test.describe('Visual Regression Tests', () => {
  test.describe('Homepage Visual Tests', () => {
    test('should match homepage design', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Wait for any animations or dynamic content
      await page.waitForTimeout(1000)

      // Take full page screenshot
      await expect(page).toHaveScreenshot('homepage-full.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should match homepage hero section', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Screenshot just the hero section
      const heroSection = page.locator('section').first()
      await expect(heroSection).toHaveScreenshot('homepage-hero.png')
    })

    test('should match features section', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Find features section
      const featuresSection = page.locator('text=/Tudo que Você Precisa/').locator('..')
      if (await featuresSection.isVisible()) {
        await expect(featuresSection).toHaveScreenshot('homepage-features.png')
      }
    })

    test('should match testimonials section', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Find testimonials section
      const testimonialsSection = page.locator('text=/O Que Nossos Clientes Dizem/').locator('..')
      if (await testimonialsSection.isVisible()) {
        await expect(testimonialsSection).toHaveScreenshot('homepage-testimonials.png')
      }
    })
  })

  test.describe('Authentication Pages Visual Tests', () => {
    test('should match login page design', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      await expect(page).toHaveScreenshot('login-page.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should match registration page design', async ({ page }) => {
      await page.goto('/register')
      await waitForNetworkIdle(page)

      await expect(page).toHaveScreenshot('register-page.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should show login form validation states', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Try to submit empty form to show validation
      const submitButton = page.locator('button[type="submit"]')
      if (await submitButton.isVisible()) {
        await submitButton.click()
        await page.waitForTimeout(500)

        // Screenshot with validation errors
        await expect(page).toHaveScreenshot('login-validation-errors.png')
      }
    })
  })

  test.describe('Theme and Dark Mode Tests', () => {
    test('should match light theme', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Ensure light theme
      await page.evaluate(() => {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      })
      await page.waitForTimeout(500)

      await expect(page).toHaveScreenshot('homepage-light-theme.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should match dark theme', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Enable dark theme
      await page.evaluate(() => {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      })
      await page.waitForTimeout(500)

      await expect(page).toHaveScreenshot('homepage-dark-theme.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should show theme toggle interaction', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Find theme toggle
      const themeToggle = page.locator('[data-testid="theme-toggle"], button[aria-label*="theme"]')
      
      if (await themeToggle.isVisible()) {
        // Screenshot with toggle highlighted
        await themeToggle.hover()
        await expect(themeToggle).toHaveScreenshot('theme-toggle-hover.png')
      }
    })
  })

  test.describe('Responsive Visual Tests', () => {
    test('should match mobile layout', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)

      await expect(page).toHaveScreenshot('homepage-mobile.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should match tablet layout', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 })
      await page.goto('/')
      await waitForNetworkIdle(page)

      await expect(page).toHaveScreenshot('homepage-tablet.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should match desktop layout', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 })
      await page.goto('/')
      await waitForNetworkIdle(page)

      await expect(page).toHaveScreenshot('homepage-desktop.png', {
        fullPage: true,
        animations: 'disabled'
      })
    })

    test('should match mobile navigation', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Open mobile menu if it exists
      const mobileMenuTrigger = page.locator('.mobile-menu-trigger, .hamburger, button[aria-label*="menu"]')
      
      if (await mobileMenuTrigger.isVisible()) {
        await mobileMenuTrigger.click()
        await page.waitForTimeout(500)

        await expect(page).toHaveScreenshot('mobile-navigation-open.png')
      }
    })
  })

  test.describe('Interactive Elements Visual Tests', () => {
    test('should show button hover states', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Test primary CTA button
      const ctaButton = page.locator('button:has-text("Começar Grátis"), a:has-text("Começar Grátis")')
      
      if (await ctaButton.isVisible()) {
        await ctaButton.hover()
        await expect(ctaButton).toHaveScreenshot('cta-button-hover.png')
      }
    })

    test('should show form focus states', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Focus on email input
      const emailInput = page.locator('input[type="email"], input[name="email"]')
      
      if (await emailInput.isVisible()) {
        await emailInput.focus()
        await expect(emailInput).toHaveScreenshot('email-input-focus.png')
      }
    })

    test('should show card hover effects', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Find feature cards
      const featureCard = page.locator('.card, [class*="card"]').first()
      
      if (await featureCard.isVisible()) {
        await featureCard.hover()
        await expect(featureCard).toHaveScreenshot('feature-card-hover.png')
      }
    })
  })

  test.describe('Error States Visual Tests', () => {
    test('should show form validation errors', async ({ page }) => {
      await page.goto('/register')
      await waitForNetworkIdle(page)

      // Fill invalid data
      const emailInput = page.locator('input[type="email"], input[name="email"]')
      const passwordInput = page.locator('input[type="password"], input[name="password"]')
      
      if (await emailInput.isVisible()) {
        await emailInput.fill('invalid-email')
      }
      
      if (await passwordInput.isVisible()) {
        await passwordInput.fill('weak')
      }

      // Submit to trigger validation
      const submitButton = page.locator('button[type="submit"]')
      if (await submitButton.isVisible()) {
        await submitButton.click()
        await page.waitForTimeout(500)

        await expect(page).toHaveScreenshot('form-validation-errors.png')
      }
    })

    test('should show loading states', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Fill valid login data
      const emailInput = page.locator('input[type="email"], input[name="email"]')
      const passwordInput = page.locator('input[type="password"], input[name="password"]')
      
      if (await emailInput.isVisible() && await passwordInput.isVisible()) {
        await emailInput.fill('test@example.com')
        await passwordInput.fill('password123')

        // Intercept the request to delay it
        await page.route('**/api/auth/login', async (route) => {
          await page.waitForTimeout(2000) // Simulate slow response
          await route.fulfill({
            status: 401,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Invalid credentials' })
          })
        })

        // Submit and capture loading state
        const submitButton = page.locator('button[type="submit"]')
        await submitButton.click()
        
        // Wait a bit for loading state to appear
        await page.waitForTimeout(100)
        
        // Screenshot the loading state
        await expect(submitButton).toHaveScreenshot('button-loading-state.png')
      }
    })

    test('should show 404 page', async ({ page }) => {
      await page.goto('/non-existent-page')
      await page.waitForTimeout(1000)

      // Only take screenshot if we actually get a 404 page
      const response = await page.goto('/non-existent-page')
      if (response && response.status() === 404) {
        await expect(page).toHaveScreenshot('404-page.png', {
          fullPage: true
        })
      }
    })
  })

  test.describe('Animation Tests', () => {
    test('should capture animation start state', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Look for animated elements
      const animatedElements = page.locator('[class*="animate"], [class*="fade"], [class*="slide"]')
      
      if (await animatedElements.count() > 0) {
        // Disable animations and capture static state
        await page.addStyleTag({
          content: `
            *, *::before, *::after {
              animation-duration: 0.01ms !important;
              animation-delay: -0.01ms !important;
              transition-duration: 0.01ms !important;
              transition-delay: -0.01ms !important;
            }
          `
        })
        
        await page.reload()
        await waitForNetworkIdle(page)
        
        await expect(page).toHaveScreenshot('homepage-no-animations.png', {
          fullPage: true
        })
      }
    })
  })

  test.describe('Component-Specific Visual Tests', () => {
    test('should match navigation component', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      const navigation = page.locator('nav, header nav')
      
      if (await navigation.isVisible()) {
        await expect(navigation).toHaveScreenshot('navigation-component.png')
      }
    })

    test('should match footer component', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      const footer = page.locator('footer')
      
      if (await footer.isVisible()) {
        await expect(footer).toHaveScreenshot('footer-component.png')
      }
    })

    test('should match stats section', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Find stats section with numbers like "10.000+"
      const statsSection = page.locator('text=/10.000+/').locator('..')
      
      if (await statsSection.isVisible()) {
        await expect(statsSection).toHaveScreenshot('stats-section.png')
      }
    })
  })

  test.describe('Cross-Browser Visual Tests', () => {
    test('should render consistently across browsers', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Take a screenshot that can be compared across different browser contexts
      await expect(page).toHaveScreenshot('cross-browser-test.png', {
        fullPage: true,
        animations: 'disabled',
        threshold: 0.3 // Allow for small browser differences
      })
    })
  })
})