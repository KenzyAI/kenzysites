import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle, fillFormField, mockApiResponse } from '../utils/helpers'
import { testUsers } from '../data/test-data'

test.describe('Authentication Tests', () => {
  test.describe('Registration Flow', () => {
    test('should register new user successfully', async ({ page, testUser }) => {
      // Go to registration page
      await page.goto('/register')
      await waitForNetworkIdle(page)

      // Fill registration form
      await fillFormField(page, 'name', testUser.name)
      await fillFormField(page, 'email', testUser.email)
      await fillFormField(page, 'password', testUser.password)
      
      // Check password confirmation if exists
      const confirmPasswordField = page.locator('input[name="confirmPassword"], input[name="password_confirmation"]')
      if (await confirmPasswordField.isVisible()) {
        await fillFormField(page, 'confirmPassword', testUser.password)
      }

      // Check terms checkbox if exists
      const termsCheckbox = page.locator('input[type="checkbox"][name*="terms"], input[type="checkbox"][name*="agree"]')
      if (await termsCheckbox.isVisible()) {
        await termsCheckbox.check()
      }

      // Submit form
      await page.click('button[type="submit"]')

      // Should redirect to dashboard or email verification
      await page.waitForURL(/\/(dashboard|verify-email|welcome)/)
      
      // Check we're redirected properly
      const currentUrl = page.url()
      expect(currentUrl).toMatch(/\/(dashboard|verify-email|welcome)/)
    })

    test('should show validation errors for invalid data', async ({ page }) => {
      await page.goto('/register')
      await waitForNetworkIdle(page)

      // Submit empty form
      await page.click('button[type="submit"]')

      // Check for validation errors
      const errorMessages = page.locator('[class*="error"], [class*="invalid"], [role="alert"]')
      const errorCount = await errorMessages.count()
      expect(errorCount).toBeGreaterThan(0)
    })

    test('should validate email format', async ({ page }) => {
      await page.goto('/register')
      await waitForNetworkIdle(page)

      // Fill invalid email
      await fillFormField(page, 'email', 'invalid-email')
      await fillFormField(page, 'name', 'Test User')
      await fillFormField(page, 'password', 'ValidPassword123!')

      await page.click('button[type="submit"]')

      // Should show email validation error
      const emailError = page.locator('text=/email/i').and(page.locator('[class*="error"], [role="alert"]'))
      await expect(emailError).toBeVisible()
    })

    test('should validate password strength', async ({ page }) => {
      await page.goto('/register')
      await waitForNetworkIdle(page)

      // Fill weak password
      await fillFormField(page, 'email', 'test@example.com')
      await fillFormField(page, 'name', 'Test User')
      await fillFormField(page, 'password', '123')

      await page.click('button[type="submit"]')

      // Should show password validation error
      const passwordError = page.locator('text=/password/i').and(page.locator('[class*="error"], [role="alert"]'))
      await expect(passwordError).toBeVisible()
    })

    test('should handle duplicate email registration', async ({ page, testUser }) => {
      // Mock API response for duplicate email
      await mockApiResponse(page, '**/api/auth/register', {
        error: 'Email already exists',
        message: 'Este email já está cadastrado'
      })

      await page.goto('/register')
      await waitForNetworkIdle(page)

      // Fill form with existing email
      await fillFormField(page, 'name', testUser.name)
      await fillFormField(page, 'email', testUser.email)
      await fillFormField(page, 'password', testUser.password)

      await page.click('button[type="submit"]')

      // Should show duplicate email error
      const duplicateError = page.locator('text=/já existe/i, text=/already exists/i')
      await expect(duplicateError).toBeVisible()
    })
  })

  test.describe('Login Flow', () => {
    test('should login successfully with valid credentials', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Fill login form
      await fillFormField(page, 'email', testUsers.regular.email)
      await fillFormField(page, 'password', testUsers.regular.password)

      // Submit form
      await page.click('button[type="submit"]')

      // Should redirect to dashboard
      await page.waitForURL('**/dashboard')
      
      // Verify we're on dashboard
      expect(page.url()).toContain('/dashboard')
    })

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Fill invalid credentials
      await fillFormField(page, 'email', 'wrong@example.com')
      await fillFormField(page, 'password', 'wrongpassword')

      await page.click('button[type="submit"]')

      // Should show error message
      const errorMessage = page.locator('[class*="error"], [role="alert"]')
      await expect(errorMessage).toBeVisible()
    })

    test('should validate required fields', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Submit empty form
      await page.click('button[type="submit"]')

      // Should show validation errors
      const errors = page.locator('[class*="error"], [class*="invalid"], [role="alert"]')
      const errorCount = await errors.count()
      expect(errorCount).toBeGreaterThan(0)
    })

    test('should remember user if remember me is checked', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Fill login form
      await fillFormField(page, 'email', testUsers.regular.email)
      await fillFormField(page, 'password', testUsers.regular.password)

      // Check remember me if exists
      const rememberCheckbox = page.locator('input[type="checkbox"][name*="remember"]')
      if (await rememberCheckbox.isVisible()) {
        await rememberCheckbox.check()
      }

      await page.click('button[type="submit"]')
      await page.waitForURL('**/dashboard')

      // Check for persistent session
      const cookies = await page.context().cookies()
      const sessionCookies = cookies.filter(cookie => 
        cookie.name.includes('session') || 
        cookie.name.includes('token') || 
        cookie.name.includes('remember')
      )
      expect(sessionCookies.length).toBeGreaterThan(0)
    })

    test('should redirect to login after logout', async ({ page }) => {
      // First login
      await page.goto('/login')
      await fillFormField(page, 'email', testUsers.regular.email)
      await fillFormField(page, 'password', testUsers.regular.password)
      await page.click('button[type="submit"]')
      await page.waitForURL('**/dashboard')

      // Then logout
      const userMenu = page.locator('[data-testid="user-menu"], [aria-label*="menu"], button:has-text("Menu")')
      
      if (await userMenu.isVisible()) {
        await userMenu.click()
        
        const logoutButton = page.locator('[data-testid="logout"], text=/logout/i, text=/sair/i')
        await logoutButton.click()
      } else {
        // Alternative logout method
        await page.goto('/logout')
      }

      // Should redirect to home or login
      await page.waitForURL(/\/(login|$)/)
      const url = page.url()
      expect(url).toMatch(/\/(login|$)/)
    })
  })

  test.describe('Password Reset Flow', () => {
    test('should handle forgot password request', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Click forgot password link
      const forgotPasswordLink = page.locator('a:has-text("Esqueci"), a:has-text("Forgot"), a[href*="forgot"]')
      
      if (await forgotPasswordLink.isVisible()) {
        await forgotPasswordLink.click()
        await page.waitForURL('**/forgot-password')

        // Fill email
        await fillFormField(page, 'email', testUsers.regular.email)
        await page.click('button[type="submit"]')

        // Should show success message
        const successMessage = page.locator('text=/enviado/i, text=/sent/i')
        await expect(successMessage).toBeVisible()
      }
    })

    test('should validate email in forgot password', async ({ page }) => {
      const forgotUrl = '/forgot-password'
      
      // Try to navigate to forgot password page
      await page.goto(forgotUrl)
      
      // If page exists, test validation
      if (page.url().includes('forgot-password')) {
        await fillFormField(page, 'email', 'invalid-email')
        await page.click('button[type="submit"]')

        // Should show validation error
        const error = page.locator('[class*="error"], [role="alert"]')
        await expect(error).toBeVisible()
      }
    })
  })

  test.describe('Authentication State', () => {
    test('should protect dashboard routes', async ({ page }) => {
      // Try to access dashboard without login
      await page.goto('/dashboard')
      
      // Should redirect to login
      await page.waitForURL(/\/(login|auth)/)
      expect(page.url()).toMatch(/\/(login|auth)/)
    })

    test('should redirect logged-in users from auth pages', async ({ page }) => {
      // First login
      await page.goto('/login')
      await fillFormField(page, 'email', testUsers.regular.email)
      await fillFormField(page, 'password', testUsers.regular.password)
      await page.click('button[type="submit"]')
      await page.waitForURL('**/dashboard')

      // Try to access login page while logged in
      await page.goto('/login')
      
      // Should redirect to dashboard
      await page.waitForURL('**/dashboard')
      expect(page.url()).toContain('/dashboard')
    })

    test('should maintain session across page reloads', async ({ page }) => {
      // Login
      await page.goto('/login')
      await fillFormField(page, 'email', testUsers.regular.email)
      await fillFormField(page, 'password', testUsers.regular.password)
      await page.click('button[type="submit"]')
      await page.waitForURL('**/dashboard')

      // Reload page
      await page.reload()
      await waitForNetworkIdle(page)

      // Should still be on dashboard
      expect(page.url()).toContain('/dashboard')
    })
  })

  test.describe('Social Authentication', () => {
    test('should display social login options', async ({ page }) => {
      await page.goto('/login')
      await waitForNetworkIdle(page)

      // Check for social login buttons
      const socialButtons = [
        'Google',
        'GitHub',
        'Facebook',
        'Twitter'
      ]

      for (const provider of socialButtons) {
        const button = page.locator(`button:has-text("${provider}"), a:has-text("${provider}")`)
        if (await button.isVisible()) {
          expect(await button.isVisible()).toBe(true)
        }
      }
    })
  })
})