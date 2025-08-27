import { Page } from '@playwright/test'

/**
 * Wait for network to be idle
 */
export async function waitForNetworkIdle(page: Page, timeout = 3000) {
  await page.waitForLoadState('networkidle', { timeout })
}

/**
 * Login helper
 */
export async function login(page: Page, email: string, password: string) {
  await page.goto('/login')
  await page.fill('input[name="email"]', email)
  await page.fill('input[name="password"]', password)
  await page.click('button[type="submit"]')
  await page.waitForURL('**/dashboard')
}

/**
 * Logout helper
 */
export async function logout(page: Page) {
  await page.click('[data-testid="user-menu"]')
  await page.click('[data-testid="logout-button"]')
  await page.waitForURL('/')
}

/**
 * Check if element is visible with retry
 */
export async function isElementVisible(page: Page, selector: string, timeout = 5000) {
  try {
    await page.waitForSelector(selector, { state: 'visible', timeout })
    return true
  } catch {
    return false
  }
}

/**
 * Take screenshot with timestamp
 */
export async function takeScreenshot(page: Page, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  await page.screenshot({
    path: `test-results/screenshots/${name}-${timestamp}.png`,
    fullPage: true
  })
}

/**
 * Fill form field with validation
 */
export async function fillFormField(page: Page, fieldName: string, value: string) {
  const selector = `input[name="${fieldName}"], textarea[name="${fieldName}"], select[name="${fieldName}"]`
  await page.fill(selector, value)
  // Wait for any validation to complete
  await page.waitForTimeout(100)
}

/**
 * Check accessibility
 */
export async function checkAccessibility(page: Page) {
  // Check for proper heading hierarchy
  const headings = await page.$$eval('h1, h2, h3, h4, h5, h6', (elements) =>
    elements.map((el) => ({
      level: parseInt(el.tagName[1]),
      text: el.textContent,
    }))
  )
  
  // Check for alt text on images
  const imagesWithoutAlt = await page.$$eval('img:not([alt])', (imgs) => imgs.length)
  
  // Check for form labels
  const inputsWithoutLabels = await page.$$eval(
    'input:not([aria-label]):not([aria-labelledby])',
    (inputs) => inputs.filter((input) => !(input as HTMLInputElement).labels?.length).length
  )
  
  return {
    headings,
    imagesWithoutAlt,
    inputsWithoutLabels,
  }
}

/**
 * Mock API response
 */
export async function mockApiResponse(page: Page, url: string, response: any) {
  await page.route(url, (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(response),
    })
  })
}