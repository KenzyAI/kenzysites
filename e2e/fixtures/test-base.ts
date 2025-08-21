import { test as base, expect } from '@playwright/test'

// Define custom fixtures
type CustomFixtures = {
  apiUrl: string
  testUser: {
    email: string
    password: string
    name: string
  }
}

// Extend base test with custom fixtures
export const test = base.extend<CustomFixtures>({
  apiUrl: async ({}, use) => {
    const url = process.env.API_URL || 'http://localhost:8000'
    await use(url)
  },
  
  testUser: async ({}, use) => {
    const user = {
      email: `test.user.${Date.now()}@example.com`,
      password: 'TestPassword123!',
      name: 'Test User'
    }
    await use(user)
  },
})

export { expect }