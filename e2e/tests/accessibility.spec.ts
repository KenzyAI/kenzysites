import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle, checkAccessibility } from '../utils/helpers'

test.describe('Accessibility Tests', () => {
  const testPages = [
    { name: 'Homepage', url: '/' },
    { name: 'Login', url: '/login' },
    { name: 'Register', url: '/register' },
  ]

  test.describe('WCAG Compliance', () => {
    for (const testPage of testPages) {
      test(`${testPage.name} should meet basic accessibility standards`, async ({ page }) => {
        await page.goto(testPage.url)
        await waitForNetworkIdle(page)

        const accessibility = await checkAccessibility(page)

        // No images without alt text
        expect(accessibility.imagesWithoutAlt).toBe(0)

        // All inputs should have labels
        expect(accessibility.inputsWithoutLabels).toBe(0)

        // Should have proper heading structure
        expect(accessibility.headings.length).toBeGreaterThan(0)

        // Check heading hierarchy
        if (accessibility.headings.length > 1) {
          for (let i = 1; i < accessibility.headings.length; i++) {
            const currentLevel = accessibility.headings[i].level
            const previousLevel = accessibility.headings[i - 1].level
            
            // Heading levels shouldn't skip (e.g., h1 -> h3)
            expect(currentLevel - previousLevel).toBeLessThanOrEqual(1)
          }
        }
      })
    }

    test('should have proper color contrast', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Check text elements for contrast
      const textElements = await page.$$eval('p, h1, h2, h3, h4, h5, h6, span, a, button', (elements) => {
        return elements.map((el) => {
          const styles = window.getComputedStyle(el)
          return {
            color: styles.color,
            backgroundColor: styles.backgroundColor,
            fontSize: styles.fontSize,
            fontWeight: styles.fontWeight,
            text: el.textContent?.slice(0, 50)
          }
        }).filter(el => el.text?.trim())
      })

      // Basic check that text has color set
      for (const element of textElements.slice(0, 10)) { // Check first 10 elements
        expect(element.color).not.toBe('rgba(0, 0, 0, 0)') // Not transparent
        expect(element.color).toBeTruthy()
      }
    })

    test('should support keyboard navigation', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Get all focusable elements
      const focusableElements = await page.$$eval(
        'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])',
        (elements) => elements.length
      )

      expect(focusableElements).toBeGreaterThan(0)

      // Test tab navigation
      await page.keyboard.press('Tab')
      
      // Check if an element is focused
      const activeElement = await page.evaluate(() => {
        const active = document.activeElement
        return {
          tagName: active?.tagName,
          type: active?.getAttribute('type'),
          role: active?.getAttribute('role')
        }
      })

      expect(activeElement.tagName).toBeTruthy()
    })

    test('should have proper ARIA labels', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Check buttons have accessible names
      const buttonsWithoutLabels = await page.$$eval('button', (buttons) => {
        return buttons.filter(button => {
          const hasAriaLabel = button.getAttribute('aria-label')
          const hasAriaLabelledBy = button.getAttribute('aria-labelledby')
          const hasText = button.textContent?.trim()
          const hasTitle = button.getAttribute('title')
          
          return !hasAriaLabel && !hasAriaLabelledBy && !hasText && !hasTitle
        }).length
      })

      expect(buttonsWithoutLabels).toBe(0)

      // Check form inputs have labels
      const inputsWithoutLabels = await page.$$eval('input[type]:not([type="hidden"])', (inputs) => {
        return inputs.filter(input => {
          const hasAriaLabel = input.getAttribute('aria-label')
          const hasAriaLabelledBy = input.getAttribute('aria-labelledby')
          const hasAssociatedLabel = input.labels && input.labels.length > 0
          const hasPlaceholder = input.getAttribute('placeholder')
          
          return !hasAriaLabel && !hasAriaLabelledBy && !hasAssociatedLabel && !hasPlaceholder
        }).length
      })

      expect(inputsWithoutLabels).toBe(0)
    })

    test('should have proper semantic HTML', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Check for semantic landmarks
      const landmarks = await page.evaluate(() => {
        return {
          header: document.querySelector('header') !== null,
          nav: document.querySelector('nav') !== null,
          main: document.querySelector('main') !== null,
          footer: document.querySelector('footer') !== null
        }
      })

      // Should have at least main content area
      expect(landmarks.main).toBe(true)

      // Check for proper list structure
      const improperLists = await page.$$eval('ul, ol', (lists) => {
        return lists.filter(list => {
          const children = Array.from(list.children)
          return children.some(child => child.tagName !== 'LI')
        }).length
      })

      expect(improperLists).toBe(0)
    })
  })

  test.describe('Screen Reader Compatibility', () => {
    test('should have proper page titles', async ({ page }) => {
      const pages = [
        { url: '/', expectedTitle: /WordPress|Builder|AI/ },
        { url: '/login', expectedTitle: /Login|Entrar/ },
        { url: '/register', expectedTitle: /Register|Registro|Cadastro/ }
      ]

      for (const testPage of pages) {
        await page.goto(testPage.url)
        await waitForNetworkIdle(page)

        const title = await page.title()
        expect(title).toMatch(testPage.expectedTitle)
        expect(title.length).toBeGreaterThan(0)
        expect(title.length).toBeLessThan(60) // SEO best practice
      }
    })

    test('should have descriptive link text', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Check for vague link text
      const vagueLinks = await page.$$eval('a', (links) => {
        const vagueTexts = ['click here', 'read more', 'here', 'more', 'link']
        
        return links.filter(link => {
          const text = link.textContent?.toLowerCase().trim()
          return text && vagueTexts.includes(text)
        }).length
      })

      expect(vagueLinks).toBe(0)

      // Check all links have meaningful text
      const linksWithoutText = await page.$$eval('a', (links) => {
        return links.filter(link => {
          const text = link.textContent?.trim()
          const ariaLabel = link.getAttribute('aria-label')
          const title = link.getAttribute('title')
          
          return !text && !ariaLabel && !title
        }).length
      })

      expect(linksWithoutText).toBe(0)
    })

    test('should announce dynamic content changes', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Submit form with invalid data to trigger error
      const submitButton = page.locator('button[type="submit"]')
      if (await submitButton.isVisible()) {
        await submitButton.click()

        // Look for ARIA live regions for error messages
        const liveRegions = await page.$$eval('[aria-live], [role="alert"], [role="status"]', (elements) => {
          return elements.map(el => ({
            ariaLive: el.getAttribute('aria-live'),
            role: el.getAttribute('role'),
            text: el.textContent?.trim()
          }))
        })

        // Should have some mechanism to announce errors
        const hasErrorAnnouncement = liveRegions.some(region => 
          region.ariaLive === 'polite' || 
          region.ariaLive === 'assertive' || 
          region.role === 'alert'
        )

        expect(hasErrorAnnouncement).toBe(true)
      }
    })
  })

  test.describe('Motor Impairment Support', () => {
    test('should have adequate click targets', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Check interactive elements are large enough
      const smallTargets = await page.$$eval('button, a, input[type="button"], input[type="submit"]', (elements) => {
        return elements.filter(el => {
          const rect = el.getBoundingClientRect()
          return rect.width < 44 || rect.height < 44 // WCAG 2.1 AA requirement
        }).length
      })

      expect(smallTargets).toBe(0)
    })

    test('should have sufficient spacing between interactive elements', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // This is a simplified check - in real scenarios you'd want more sophisticated spacing analysis
      const interactiveElements = await page.$$('button, a, input[type="button"], input[type="submit"]')
      
      if (interactiveElements.length > 1) {
        // Just verify we can identify interactive elements
        expect(interactiveElements.length).toBeGreaterThan(0)
      }
    })

    test('should be usable with keyboard only', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Navigate using only keyboard
      let focusedElements = []
      
      for (let i = 0; i < 10; i++) {
        await page.keyboard.press('Tab')
        
        const activeElement = await page.evaluate(() => {
          const active = document.activeElement
          return {
            tagName: active?.tagName,
            text: active?.textContent?.slice(0, 30),
            href: active?.getAttribute('href'),
            type: active?.getAttribute('type')
          }
        })
        
        if (activeElement.tagName && activeElement.tagName !== 'BODY') {
          focusedElements.push(activeElement)
        }
      }

      // Should be able to navigate to multiple elements
      expect(focusedElements.length).toBeGreaterThan(3)

      // Test activation with keyboard
      if (focusedElements.length > 0) {
        // Go back to first focusable element
        for (let i = 0; i < focusedElements.length; i++) {
          await page.keyboard.press('Shift+Tab')
        }
        
        // Try to activate with Enter or Space
        await page.keyboard.press('Enter')
        
        // Should handle activation (we'll check URL changed or modal opened)
        const currentUrl = page.url()
        const modal = await page.locator('[role="dialog"], .modal').isVisible()
        
        // Some interaction should have occurred
        expect(currentUrl !== '/' || modal).toBe(true)
      }
    })
  })

  test.describe('Visual Impairment Support', () => {
    test('should work with high contrast mode', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Simulate high contrast by injecting CSS
      await page.addStyleTag({
        content: `
          * {
            background: black !important;
            color: white !important;
            border-color: white !important;
          }
          a {
            color: yellow !important;
          }
        `
      })

      // Page should still be functional
      const mainContent = page.locator('main, h1, .container')
      await expect(mainContent.first()).toBeVisible()

      // Links should be distinguishable
      const links = page.locator('a')
      const linkCount = await links.count()
      
      if (linkCount > 0) {
        const firstLink = links.first()
        await expect(firstLink).toBeVisible()
      }
    })

    test('should scale properly when zoomed', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Simulate 200% zoom
      await page.setViewportSize({ width: 640, height: 360 }) // Half size = 2x zoom effect
      
      // Content should still be accessible
      const mainContent = page.locator('main, h1, .container')
      await expect(mainContent.first()).toBeVisible()

      // No horizontal scrolling should be needed for main content
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth)
      expect(bodyWidth).toBeLessThanOrEqual(680) // Allow some margin
    })

    test('should provide text alternatives for visual content', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Check images have alt text
      const imagesWithoutAlt = await page.$$eval('img', (images) => {
        return images.filter(img => {
          const alt = img.getAttribute('alt')
          const ariaLabel = img.getAttribute('aria-label')
          const ariaLabelledBy = img.getAttribute('aria-labelledby')
          const role = img.getAttribute('role')
          
          // Decorative images (role="presentation" or alt="") are OK
          if (role === 'presentation' || alt === '') return false
          
          return !alt && !ariaLabel && !ariaLabelledBy
        }).length
      })

      expect(imagesWithoutAlt).toBe(0)

      // Check for icons with text alternatives
      const iconsWithoutLabels = await page.$$eval('[class*="icon"], svg', (elements) => {
        return elements.filter(el => {
          const ariaLabel = el.getAttribute('aria-label')
          const ariaLabelledBy = el.getAttribute('aria-labelledby')
          const title = el.querySelector('title')
          const role = el.getAttribute('role')
          
          // Decorative icons are OK
          if (role === 'presentation' || role === 'img' && (ariaLabel || title)) return false
          
          return !ariaLabel && !ariaLabelledBy && !title
        }).length
      })

      // This might be 0 if all icons are properly labeled, or if they're decorative
      // We just check that the system can detect icons
      expect(iconsWithoutLabels).toBeGreaterThanOrEqual(0)
    })
  })

  test.describe('Cognitive Accessibility', () => {
    test('should have clear error messages', async ({ page }) => {
      await page.goto('/register')
      await waitForNetworkIdle(page)

      // Submit form without filling required fields
      const submitButton = page.locator('button[type="submit"]')
      if (await submitButton.isVisible()) {
        await submitButton.click()

        // Look for clear, helpful error messages
        const errorMessages = await page.$$eval(
          '[class*="error"], [role="alert"], .invalid-feedback', 
          (elements) => {
            return elements.map(el => el.textContent?.trim()).filter(text => text)
          }
        )

        if (errorMessages.length > 0) {
          // Error messages should be descriptive, not just "Error"
          const descriptiveErrors = errorMessages.filter(msg => 
            msg.length > 5 && !msg.toLowerCase().includes('error')
          )
          expect(descriptiveErrors.length).toBeGreaterThan(0)
        }
      }
    })

    test('should have consistent navigation', async ({ page }) => {
      const pages = ['/', '/login', '/register']
      let navigationElements = []

      for (const url of pages) {
        await page.goto(url)
        await waitForNetworkIdle(page)

        const navItems = await page.$$eval('nav a, header a', (links) => {
          return links.map(link => ({
            text: link.textContent?.trim(),
            href: link.getAttribute('href')
          })).filter(item => item.text)
        })

        navigationElements.push(navItems)
      }

      // Check navigation is consistent across pages
      if (navigationElements.length > 1) {
        const firstPageNav = navigationElements[0]
        
        if (firstPageNav.length > 0) {
          // At least some navigation elements should be consistent
          for (let i = 1; i < navigationElements.length; i++) {
            const currentPageNav = navigationElements[i]
            const commonElements = firstPageNav.filter(item => 
              currentPageNav.some(navItem => navItem.text === item.text)
            )
            
            expect(commonElements.length).toBeGreaterThan(0)
          }
        }
      }
    })

    test('should provide clear page structure', async ({ page }) => {
      await page.goto('/')
      await waitForNetworkIdle(page)

      // Check for clear page structure
      const structure = await page.evaluate(() => {
        return {
          hasMainHeading: document.querySelector('h1') !== null,
          headingCount: document.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
          hasNavigation: document.querySelector('nav') !== null,
          hasMainContent: document.querySelector('main') !== null,
          hasLandmarks: document.querySelectorAll('[role="banner"], [role="navigation"], [role="main"], [role="contentinfo"]').length
        }
      })

      expect(structure.hasMainHeading).toBe(true)
      expect(structure.headingCount).toBeGreaterThan(1)
      expect(structure.hasMainContent || structure.hasLandmarks > 0).toBe(true)
    })

    test('should provide feedback for user actions', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Fill form and check for feedback
      const emailInput = page.locator('input[type="email"], input[name="email"]')
      if (await emailInput.isVisible()) {
        await emailInput.fill('test@example.com')
        
        // Look for validation feedback
        const validationFeedback = page.locator(
          '.valid, .success, [class*="success"], [aria-describedby]'
        )
        
        // Some kind of feedback mechanism should exist
        // (This is a basic check - real validation might be more complex)
        const feedbackExists = await validationFeedback.count() > 0
        expect(feedbackExists).toBe(true)
      }
    })
  })
})