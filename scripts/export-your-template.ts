#!/usr/bin/env tsx

// Script para exportar templates do usuário e testá-los no AI Builder
import { writeFileSync } from 'fs'
import { join } from 'path'

async function exportUserTemplates() {
  console.log('📥 Exportando seus templates do Elementor...')
  console.log('')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  const appPassword = '4AM0t7AhFush3HAmnbfE3Vuq'
  const credentials = Buffer.from(`${username}:${appPassword}`).toString('base64')
  
  // Listar templates disponíveis
  console.log('📋 Buscando templates disponíveis...')
  try {
    const response = await fetch(`${baseUrl}/wp-json/kenzysites/v1/elementor/templates`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      console.log('❌ Erro ao buscar templates. Você instalou o plugin atualizado?')
      console.log('💡 AÇÃO: Reinstale o kenzysites-ai-builder.zip atualizado')
      return
    }
    
    const data = await response.json()
    console.log(`✅ ${data.total} templates encontrados!`)
    console.log('')
    
    data.templates.forEach((template: any, index: number) => {
      console.log(`${index + 1}. ${template.title}`)
      console.log(`   - ID: ${template.id}`)
      console.log(`   - Tipo: ${template.type}`)
      console.log(`   - Modificado: ${new Date(template.modified).toLocaleDateString()}`)
      console.log('')
    })
    
    // Exportar o primeiro template (LP Dr Mariana 2)
    const firstTemplate = data.templates[0]
    if (firstTemplate) {
      console.log(`🔄 Exportando template: ${firstTemplate.title}`)
      
      const exportResponse = await fetch(`${baseUrl}/wp-json/kenzysites/v1/elementor/export/${firstTemplate.id}`, {
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (exportResponse.ok) {
        const exportData = await exportResponse.json()
        const template = exportData.template
        
        console.log('✅ Template exportado com sucesso!')
        console.log(`   - ID AI: ${template.id}`)
        console.log(`   - Título: ${template.title}`)
        console.log(`   - Seções: ${template.content?.length || 'N/A'}`)
        console.log(`   - Categorias: ${template.category.join(', ')}`)
        
        // Salvar template para usar no AI Builder
        const templatePath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library', `${template.id}.json`)
        writeFileSync(templatePath, JSON.stringify(template, null, 2))
        
        console.log(`📁 Salvo em: ${templatePath}`)
        console.log('')
        
        // Testar com AI Builder
        await testTemplateWithAI(template)
        
      } else {
        console.log('❌ Erro ao exportar template')
        const errorText = await exportResponse.text()
        console.log(`   ${errorText}`)
      }
    }
    
  } catch (error) {
    console.log(`💥 Erro: ${error}`)
  }
}

async function testTemplateWithAI(template: any) {
  console.log('🤖 Testando template com AI Builder...')
  
  // Importar o AI Builder
  const { ElementorAIBuilder } = await import('../lib/ai-builder/core/elementor-builder')
  const { createHostedWordPressClient } = await import('../lib/wordpress/hosted-client')
  
  const config = {
    defaultModel: 'gpt-3.5-turbo' as const,
    maxTokens: 1000,
    temperature: 0.7
  }
  
  const wpClient = createHostedWordPressClient()
  const aiBuilder = new ElementorAIBuilder(config, wpClient)
  
  // Carregar seu template
  await aiBuilder.loadTemplates([template])
  
  // Negócio de teste para sua landing page médica
  const businessInfo = {
    name: 'Dra. Mariana Silva',
    type: 'business' as const,
    description: 'Médica especialista em dermatologia com foco em tratamentos estéticos e cuidados com a pele',
    industry: 'healthcare',
    services: ['Consultas Dermatológicas', 'Tratamentos Estéticos', 'Cuidados com a Pele'],
    targetAudience: 'Pessoas que buscam cuidados especializados com a pele e tratamentos estéticos',
    location: 'São Paulo, SP',
    phone: '(11) 99999-9999',
    email: 'contato@dramariana.com.br'
  }
  
  console.log('')
  console.log('👩‍⚕️ Informações do Negócio (Médica):')
  console.log(`   Nome: ${businessInfo.name}`)
  console.log(`   Especialidade: ${businessInfo.description}`)
  console.log(`   Serviços: ${businessInfo.services.join(', ')}`)
  
  // Gerar site com seu template
  const request = {
    businessInfo,
    templateId: template.id, // Usar especificamente seu template
    preferences: {
      colorScheme: 'light' as const,
      style: 'corporate' as const,
      layout: 'single-page' as const
    }
  }
  
  console.log('')
  console.log('🚀 Gerando site com SEU template...')
  
  const progressCallback = (progress: any) => {
    const bar = '█'.repeat(Math.floor(progress.progress / 5)) + '░'.repeat(20 - Math.floor(progress.progress / 5))
    console.log(`[${bar}] ${progress.progress}% - ${progress.message}`)
    
    if (progress.details?.template_selected) {
      console.log(`   📋 Template: ${progress.details.template_selected}`)
    }
  }
  
  try {
    const result = await aiBuilder.buildFromPrompt(request, progressCallback)
    
    console.log('')
    if (result.success) {
      console.log('🎉 Site gerado com SEU template!')
      console.log(`   ID: ${result.siteId}`)
      console.log(`   URL: ${result.preview_url}`)
      console.log(`   Template usado: ${result.template_used}`)
      
      if (result.pages) {
        console.log('   Páginas criadas:')
        result.pages.forEach(page => {
          console.log(`     - ${page.title}: ${page.url}`)
        })
      }
    } else {
      console.log('❌ Erro na geração:')
      console.log(`   ${result.error}`)
    }
    
  } catch (error) {
    console.log('💥 Erro no teste:', error)
  }
}

exportUserTemplates()