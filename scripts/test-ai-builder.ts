#!/usr/bin/env tsx

// Script para testar o AI Builder completo
import { ElementorAIBuilder } from '../lib/ai-builder/core/elementor-builder'
import { createHostedWordPressClient } from '../lib/wordpress/hosted-client'
import type { BusinessInfo, SiteGenerationRequest, ElementorTemplate } from '../lib/ai-builder/types'
import { readFileSync } from 'fs'
import { join } from 'path'

async function testAIBuilder() {
  console.log('🤖 Testando AI Builder do KenzySites...')
  console.log('')

  // Configuração do AI Builder
  const config = {
    defaultModel: 'gpt-3.5-turbo' as const,
    maxTokens: 1000,
    temperature: 0.7
  }

  // Cliente WordPress (opcional para teste)
  const wpClient = createHostedWordPressClient()

  // Inicializar AI Builder
  const aiBuilder = new ElementorAIBuilder(config, wpClient)

  // Carregar template de exemplo
  console.log('📁 Carregando template de exemplo...')
  try {
    const templatePath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library/business-template.json')
    const templateData = JSON.parse(readFileSync(templatePath, 'utf-8')) as ElementorTemplate
    
    await aiBuilder.loadTemplates([templateData])
    console.log(`✅ Template "${templateData.title}" carregado com sucesso!`)
  } catch (error) {
    console.error('❌ Erro ao carregar template:', error)
    return
  }

  // Informações de negócio de teste
  const businessInfo: BusinessInfo = {
    name: 'TechSolutions Pro',
    type: 'business',
    description: 'Uma empresa de consultoria em tecnologia que ajuda pequenas e médias empresas a modernizar seus sistemas e processos.',
    industry: 'technology',
    services: ['Consultoria em TI', 'Desenvolvimento de Software', 'Suporte Técnico'],
    targetAudience: 'Pequenas e médias empresas que precisam modernizar sua infraestrutura tecnológica',
    location: 'São Paulo, SP',
    phone: '(11) 9999-8888',
    email: 'contato@techsolutions.com.br',
    website: 'https://techsolutions.com.br'
  }

  // Solicitação de geração do site
  const request: SiteGenerationRequest = {
    businessInfo,
    preferences: {
      colorScheme: 'light',
      style: 'modern',
      layout: 'multi-page',
      includePages: ['home', 'about', 'services', 'contact']
    },
    customization: {
      primaryColor: '#007cba',
      secondaryColor: '#005a87'
    }
  }

  console.log('')
  console.log('🏢 Informações do Negócio:')
  console.log(`   Nome: ${businessInfo.name}`)
  console.log(`   Tipo: ${businessInfo.type}`)
  console.log(`   Setor: ${businessInfo.industry}`)
  console.log(`   Serviços: ${businessInfo.services?.join(', ')}`)
  console.log(`   Localização: ${businessInfo.location}`)

  console.log('')
  console.log('🚀 Iniciando geração do site...')

  // Progresso da geração
  const progressCallback = (progress: any) => {
    const progressBar = '█'.repeat(Math.floor(progress.progress / 5)) + '░'.repeat(20 - Math.floor(progress.progress / 5))
    console.log(`[${progressBar}] ${progress.progress}% - ${progress.message}`)
    
    if (progress.details) {
      if (progress.details.template_selected) {
        console.log(`   📋 Template: ${progress.details.template_selected}`)
      }
      if (progress.details.content_generated) {
        console.log(`   ✍️  Conteúdo: Gerado`)
      }
      if (progress.details.deployment_started) {
        console.log(`   🚀 Deploy: Iniciado`)
      }
    }
  }

  try {
    // Gerar site
    const result = await aiBuilder.buildFromPrompt(request, progressCallback)

    console.log('')
    if (result.success) {
      console.log('🎉 Site gerado com sucesso!')
      console.log('')
      console.log('📊 Resultados:')
      console.log(`   ID do Site: ${result.siteId}`)
      console.log(`   Template Usado: ${result.template_used}`)
      console.log(`   Tempo de Geração: ${result.generation_time}ms`)
      
      if (result.preview_url) {
        console.log(`   URL de Preview: ${result.preview_url}`)
      }
      
      if (result.pages && result.pages.length > 0) {
        console.log(`   Páginas Criadas:`)
        result.pages.forEach(page => {
          console.log(`     - ${page.title} (${page.type}): ${page.url}`)
        })
      }

      if (result.warnings && result.warnings.length > 0) {
        console.log('')
        console.log('⚠️  Avisos:')
        result.warnings.forEach(warning => console.log(`   - ${warning}`))
      }
    } else {
      console.log('❌ Falha na geração do site!')
      console.log(`   Erro: ${result.error}`)
    }

  } catch (error) {
    console.error('💥 Erro durante a geração:', error)
  }

  console.log('')
  console.log('📈 Estatísticas do AI Builder:')
  
  const templates = aiBuilder.getAvailableTemplates()
  console.log(`   Templates Carregados: ${templates.length}`)
  
  const businessTemplates = aiBuilder.getTemplatesByCategory('business')
  console.log(`   Templates de Negócio: ${businessTemplates.length}`)

  // Teste de busca
  const searchResults = aiBuilder.searchTemplates('modern')
  console.log(`   Templates "modern": ${searchResults.length}`)

  console.log('')
  console.log('✨ Teste do AI Builder concluído!')
}

// Executar teste
testAIBuilder().catch(error => {
  console.error('💥 Erro fatal no teste:', error)
  process.exit(1)
})