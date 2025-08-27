#!/usr/bin/env tsx

// Cria um template exemplo com placeholders inteligentes

import { PlaceholderSystem } from '../lib/ai-builder/core/placeholder-system'
import { SemanticAnalysisAgent, ContentGenerationAgent } from '../lib/ai-builder/core/intelligent-agents'
import { writeFileSync, readFileSync } from 'fs'
import { join } from 'path'

async function createPlaceholderTemplate() {
  console.log('🎯 Criando template exemplo com placeholders inteligentes...')
  console.log('')
  
  // Carregar seu template existente
  const templatePath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library/custom-22.json')
  const originalTemplate = JSON.parse(readFileSync(templatePath, 'utf-8'))
  
  console.log(`📋 Template original: ${originalTemplate.title}`)
  console.log(`   Seções: ${originalTemplate.content.length}`)
  console.log('')
  
  // Criar versão com placeholders
  const placeholderTemplate = createTemplateWithPlaceholders(originalTemplate)
  
  // Salvar template com placeholders
  const placeholderPath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library/medical-placeholder-template.json')
  writeFileSync(placeholderPath, JSON.stringify(placeholderTemplate, null, 2))
  
  console.log(`📁 Template com placeholders salvo em: ${placeholderPath}`)
  console.log('')
  
  // Testar sistema de placeholders
  await testPlaceholderSystem(placeholderTemplate)
}

function createTemplateWithPlaceholders(originalTemplate: any): any {
  console.log('🔄 Convertendo template para usar placeholders...')
  
  const template = JSON.parse(JSON.stringify(originalTemplate))
  
  // Exemplos de substituições inteligentes baseadas no seu template médico
  const replacements = new Map([
    // Títulos principais
    ['Dra. Mariana Silva', '{{BUSINESS_NAME}}'],
    ['Dr. Mariana', '{{BUSINESS_NAME}}'],
    ['Mariana Silva', '{{BUSINESS_NAME}}'],
    
    // Especialidades
    ['Dermatologia', '{{BUSINESS_SPECIALTY}}'],
    ['Dermatologista', '{{BUSINESS_SPECIALTY}}'],
    ['especialista em dermatologia', '{{BUSINESS_SPECIALTY}}'],
    
    // Descrições principais
    ['Cuidados especializados para sua pele', '{{MAIN_DESCRIPTION}}'],
    ['Tratamentos dermatológicos avançados', '{{MAIN_DESCRIPTION}}'],
    
    // Serviços
    ['Consultas Dermatológicas', '{{SERVICES_LIST}}'],
    ['Tratamentos Estéticos', '{{SERVICE_1}}'],
    ['Botox e Preenchimento', '{{SERVICE_2}}'],
    ['Cuidados com a Pele', '{{SERVICE_3}}'],
    
    // Contatos
    ['(11) 99999-9999', '{{PHONE}}'],
    ['contato@dramariana.com.br', '{{EMAIL}}'],
    ['dramariana.com.br', '{{WEBSITE}}'],
    
    // CTAs
    ['Agendar Consulta', '{{PRIMARY_CTA}}'],
    ['Marcar Avaliação', '{{SECONDARY_CTA}}'],
    ['Entre em Contato', '{{CONTACT_CTA}}'],
    
    // Benefícios/Features
    ['Anos de experiência', '{{EXPERIENCE_YEARS}} anos de experiência'],
    ['Atendimento personalizado', '{{BENEFIT_1}}'],
    ['Equipamentos modernos', '{{BENEFIT_2}}'],
    ['Resultados comprovados', '{{BENEFIT_3}}'],
    
    // Localização
    ['São Paulo, SP', '{{LOCATION}}'],
    ['Região central', '{{LOCATION_DETAIL}}'],
    
    // Testemunhos (exemplos)
    ['Excelente profissional', '{{TESTIMONIAL_1_TEXT}}'],
    ['Ana Silva', '{{TESTIMONIAL_1_AUTHOR}}'],
    ['Paciente há 2 anos', '{{TESTIMONIAL_1_ROLE}}']
  ])
  
  // Aplicar substituições no template
  const templateString = JSON.stringify(template)
  let modifiedString = templateString
  let replacementCount = 0
  
  replacements.forEach((placeholder, original) => {
    const regex = new RegExp(escapeRegExp(original), 'g')
    const matches = modifiedString.match(regex)
    
    if (matches) {
      modifiedString = modifiedString.replace(regex, placeholder)
      replacementCount += matches.length
      console.log(`   ✅ "${original}" → "${placeholder}" (${matches.length} ocorrências)`)
    }
  })
  
  console.log('')
  console.log(`📊 Total de substituições: ${replacementCount}`)
  console.log('')
  
  const finalTemplate = JSON.parse(modifiedString)
  
  // Adicionar metadados sobre placeholders
  finalTemplate.placeholders = {
    version: '1.0',
    total: replacementCount,
    categories: {
      business: ['BUSINESS_NAME', 'BUSINESS_SPECIALTY', 'MAIN_DESCRIPTION'],
      contact: ['PHONE', 'EMAIL', 'WEBSITE', 'LOCATION'],
      services: ['SERVICES_LIST', 'SERVICE_1', 'SERVICE_2', 'SERVICE_3'],
      cta: ['PRIMARY_CTA', 'SECONDARY_CTA', 'CONTACT_CTA'],
      social_proof: ['TESTIMONIAL_1_TEXT', 'TESTIMONIAL_1_AUTHOR', 'TESTIMONIAL_1_ROLE']
    },
    required: ['BUSINESS_NAME', 'BUSINESS_SPECIALTY', 'PRIMARY_CTA', 'PHONE', 'EMAIL']
  }
  
  return finalTemplate
}

async function testPlaceholderSystem(template: any) {
  console.log('🧪 Testando sistema de placeholders...')
  console.log('')
  
  const placeholderSystem = new PlaceholderSystem()
  const semanticAgent = new SemanticAnalysisAgent()
  const contentAgent = new ContentGenerationAgent()
  
  // Extrair placeholders do template
  const placeholderMapping = placeholderSystem.extractPlaceholders(template)
  
  console.log('📝 Placeholders extraídos:')
  placeholderMapping.placeholders.forEach(p => {
    console.log(`   • ${p.key} (${p.type}) - ${p.context}`)
  })
  console.log('')
  
  // Dados de negócio para teste
  const businessInfo = {
    name: 'Dr. Carlos Mendes',
    type: 'business' as const,
    description: 'Cardiologista com 15 anos de experiência em tratamentos cardiovasculares',
    industry: 'healthcare',
    services: ['Consultas Cardiológicas', 'Ecocardiograma', 'Teste Ergométrico'],
    targetAudience: 'Pacientes com problemas cardiovasculares',
    location: 'Rio de Janeiro, RJ',
    phone: '(21) 98888-7777',
    email: 'contato@drcarlos.med.br'
  }
  
  console.log('👨‍⚕️ Negócio de teste (Cardiologista):')
  console.log(`   Nome: ${businessInfo.name}`)
  console.log(`   Especialidade: Cardiologia`)
  console.log(`   Serviços: ${businessInfo.services.join(', ')}`)
  console.log('')
  
  // Gerar valores para placeholders
  console.log('🤖 Gerando conteúdo personalizado...')
  const placeholderValues: Record<string, string> = {}
  
  for (const placeholder of placeholderMapping.placeholders) {
    // Análise semântica (simulada)
    const context = {
      businessInfo,
      templateContext: template.title,
      sectionType: 'hero' as const,
      existingContent: placeholder.context
    }
    
    const analysis = semanticAgent.analyzeContent(placeholder.context, context)
    
    // Geração de conteúdo
    const generatedContent = await contentAgent.generateContextualContent(
      placeholder.key,
      placeholder,
      businessInfo,
      analysis
    )
    
    placeholderValues[placeholder.key] = generatedContent
    console.log(`   ✅ ${placeholder.key}: "${generatedContent}"`)
  }
  
  console.log('')
  
  // Aplicar substituições
  const finalTemplate = placeholderSystem.replacePlaceholders(template, placeholderValues)
  
  // Salvar resultado final
  const finalPath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library/cardiologist-personalized.json')
  writeFileSync(finalPath, JSON.stringify(finalTemplate, null, 2))
  
  console.log(`💾 Template personalizado salvo: ${finalPath}`)
  console.log('')
  
  // Testar importação no WordPress
  await testWordPressImport(finalTemplate, 'Dr. Carlos - Template Personalizado (Placeholders)')
}

async function testWordPressImport(template: any, title: string) {
  console.log('🚀 Testando importação no WordPress...')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  const appPassword = '4AM0t7AhFush3HAmnbfE3Vuq'
  const credentials = Buffer.from(`${username}:${appPassword}`).toString('base64')
  
  try {
    const response = await fetch(`${baseUrl}/wp-json/kenzysites/v1/elementor/import`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: title,
        content: template.content,
        status: 'draft' // Criar como rascunho primeiro
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      console.log('✅ Template importado com sucesso!')
      console.log(`   URL: ${result.page_url}`)
      console.log(`   ID: ${result.page_id}`)
      console.log('')
      console.log('🎯 RESULTADO:')
      console.log('   • Sistema de placeholders funcionando')
      console.log('   • Conteúdo personalizado gerado automaticamente')
      console.log('   • Template adaptado para cardiologista')
      console.log('   • Pronto para ser editado no Elementor')
      
    } else {
      console.log('❌ Erro na importação:', await response.text())
    }
    
  } catch (error) {
    console.log('💥 Erro:', error)
  }
}

function escapeRegExp(string: string): string {
  return string.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')
}

createPlaceholderTemplate()