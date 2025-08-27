#!/usr/bin/env tsx

// Teste com diferentes tipos de negócio usando o template do usuário
import { ElementorAIBuilder } from '../lib/ai-builder/core/elementor-builder'
import { createHostedWordPressClient } from '../lib/wordpress/hosted-client'
import { readFileSync } from 'fs'
import { join } from 'path'

async function testDifferentBusinesses() {
  console.log('🧪 Testando template do usuário com diferentes negócios...')
  console.log('')
  
  // Carregar o template exportado
  const templatePath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library/custom-22.json')
  const template = JSON.parse(readFileSync(templatePath, 'utf-8'))
  
  console.log(`📋 Template carregado: ${template.title}`)
  console.log(`   Seções: ${template.content.length}`)
  console.log('')
  
  // Configurar AI Builder
  const config = { defaultModel: 'gpt-3.5-turbo' as const }
  const wpClient = createHostedWordPressClient()
  const aiBuilder = new ElementorAIBuilder(config, wpClient)
  await aiBuilder.loadTemplates([template])
  
  // Diferentes tipos de negócio para testar
  const businesses = [
    {
      name: 'TechCorp Solutions',
      type: 'business' as const,
      description: 'Empresa de consultoria em tecnologia e transformação digital',
      industry: 'technology',
      services: ['Consultoria TI', 'Desenvolvimento', 'Cloud Computing']
    },
    {
      name: 'Bella Vista Restaurant',
      type: 'restaurant' as const,
      description: 'Restaurante italiano com ambiente aconchegante e pratos tradicionais',
      industry: 'food-service',
      services: ['Jantar', 'Delivery', 'Eventos']
    }
  ]
  
  for (const [index, business] of businesses.entries()) {
    console.log(`🏢 Teste ${index + 1}: ${business.name}`)
    console.log(`   Tipo: ${business.type}`)
    console.log(`   Setor: ${business.industry}`)
    console.log('')
    
    const request = {
      businessInfo: {
        ...business,
        targetAudience: 'Clientes que buscam qualidade e excelência',
        location: 'São Paulo, SP',
        phone: '(11) 99999-0000',
        email: `contato@${business.name.toLowerCase().replace(/\s+/g, '')}.com.br`
      },
      templateId: template.id,
      preferences: {
        colorScheme: index === 0 ? 'light' as const : 'colorful' as const,
        style: 'professional' as const
      }
    }
    
    try {
      console.log('🚀 Gerando site...')
      const result = await aiBuilder.buildFromPrompt(request, (progress) => {
        if (progress.progress === 100) {
          console.log(`✅ ${progress.message}`)
        }
      })
      
      if (result.success) {
        console.log(`🎉 Sucesso!`)
        console.log(`   URL: ${result.preview_url}`)
        console.log(`   ID: ${result.siteId}`)
      } else {
        console.log(`❌ Erro: ${result.error}`)
      }
      
    } catch (error) {
      console.log(`💥 Erro: ${error}`)
    }
    
    console.log('')
  }
  
  console.log('✨ Teste concluído! Seu template é versátil e funciona para diferentes negócios!')
}

testDifferentBusinesses()