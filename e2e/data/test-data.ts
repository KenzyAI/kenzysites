/**
 * Test data for E2E tests
 */

export const testSites = [
  {
    name: 'Tech Blog',
    description: 'A modern tech blog about AI and development',
    template: 'blog',
    features: ['SEO', 'Analytics', 'Newsletter'],
  },
  {
    name: 'E-commerce Store',
    description: 'Online store for digital products',
    template: 'ecommerce',
    features: ['Payment', 'Inventory', 'Shipping'],
  },
  {
    name: 'Portfolio Site',
    description: 'Creative portfolio for designer',
    template: 'portfolio',
    features: ['Gallery', 'Contact Form', 'About'],
  },
]

export const testUsers = {
  admin: {
    email: 'admin@example.com',
    password: 'AdminPass123!',
    role: 'admin',
  },
  regular: {
    email: 'user@example.com',
    password: 'UserPass123!',
    role: 'user',
  },
  premium: {
    email: 'premium@example.com',
    password: 'PremiumPass123!',
    role: 'premium',
  },
}

export const aiPrompts = [
  'Create a professional blog about sustainable technology',
  'Build an online store for handmade crafts',
  'Design a portfolio site for a photographer',
  'Create a landing page for a SaaS product',
  'Build a restaurant website with menu and reservations',
]

export const expectedContent = {
  homepage: {
    title: 'WordPress AI Builder',
    description: 'Plataforma SaaS para criação de sites WordPress com Inteligência Artificial',
    cta: 'Começar Grátis',
  },
  dashboard: {
    title: 'Dashboard',
    sections: ['Sites', 'Analytics', 'Settings'],
  },
  features: [
    'Criação com IA',
    'WordPress Nativo',
    'Design Inteligente',
    'Analytics Avançado',
    'Segurança Total',
    'Automação Completa',
  ],
}

export const apiEndpoints = {
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',
  },
  sites: {
    list: '/api/sites',
    create: '/api/sites',
    update: '/api/sites/:id',
    delete: '/api/sites/:id',
  },
  ai: {
    generate: '/api/ai/generate',
    credits: '/api/ai/credits',
  },
}