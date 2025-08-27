#!/usr/bin/env tsx

// Script para buscar templates do Elementor no WordPress
async function getElementorTemplates() {
  console.log('📋 Buscando templates do Elementor...')
  console.log('')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  const appPassword = '4AM0t7AhFush3HAmnbfE3Vuq'
  const credentials = Buffer.from(`${username}:${appPassword}`).toString('base64')
  
  // Teste 1: Tentar endpoint do Elementor
  console.log('🎨 Teste 1: Endpoint Elementor templates...')
  try {
    const response = await fetch(`${baseUrl}/wp-json/elementor/v1/templates`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      const templates = await response.json()
      console.log(`   ✅ ${templates.length} templates encontrados!`)
      
      templates.forEach((template: any, index: number) => {
        console.log(`   ${index + 1}. ${template.title || 'Sem título'}`)
        console.log(`      - ID: ${template.id}`)
        console.log(`      - Tipo: ${template.type}`)
        console.log(`      - Status: ${template.status}`)
        if (template.template_type) {
          console.log(`      - Template Type: ${template.template_type}`)
        }
        console.log('')
      })
      
      return templates
    } else {
      console.log(`   ❌ Erro: ${response.status}`)
      const errorText = await response.text()
      console.log(`   ${errorText}`)
    }
  } catch (error) {
    console.log(`   💥 Erro: ${error}`)
  }
  
  console.log('')
  
  // Teste 2: Tentar via posts do tipo elementor_library
  console.log('📚 Teste 2: Posts do tipo elementor_library...')
  try {
    const response = await fetch(`${baseUrl}/wp-json/wp/v2/elementor_library?per_page=20`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      const templates = await response.json()
      console.log(`   ✅ ${templates.length} templates na biblioteca!`)
      
      templates.forEach((template: any, index: number) => {
        console.log(`   ${index + 1}. ${template.title?.rendered || 'Sem título'}`)
        console.log(`      - ID: ${template.id}`)
        console.log(`      - Status: ${template.status}`)
        console.log(`      - Data: ${template.date}`)
        console.log(`      - Link: ${template.link}`)
        console.log('')
      })
      
      // Se encontrou templates, vamos buscar os dados do primeiro
      if (templates.length > 0) {
        const firstTemplate = templates[0]
        console.log(`🔍 Buscando dados detalhados do template: ${firstTemplate.title?.rendered}`)
        
        try {
          const detailResponse = await fetch(`${baseUrl}/wp-json/wp/v2/elementor_library/${firstTemplate.id}`, {
            headers: {
              'Authorization': `Basic ${credentials}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (detailResponse.ok) {
            const details = await detailResponse.json()
            console.log(`   ✅ Dados obtidos!`)
            console.log(`   - Meta dados disponíveis: ${Object.keys(details.meta || {}).length}`)
            
            if (details.meta && details.meta._elementor_data) {
              console.log(`   - Elementor data encontrado: ${typeof details.meta._elementor_data}`)
              
              // Tentar parsear os dados
              try {
                let elementorData = details.meta._elementor_data
                if (typeof elementorData === 'string') {
                  elementorData = JSON.parse(elementorData)
                }
                
                console.log(`   - Seções no template: ${Array.isArray(elementorData) ? elementorData.length : 'não é array'}`)
                
                // Salvar template para uso
                const templateForAI = {
                  id: `custom-${firstTemplate.id}`,
                  title: firstTemplate.title?.rendered || 'Template Personalizado',
                  type: 'page',
                  category: ['custom', 'elementor'],
                  tags: ['custom', 'user-created'],
                  content: elementorData,
                  customizable: {
                    colors: true,
                    fonts: true,
                    content: true,
                    images: true
                  }
                }
                
                // Salvar arquivo
                const fs = require('fs')
                const path = require('path')
                const templatePath = path.join(process.cwd(), 'lib/ai-builder/templates/elementor/library', `custom-template-${firstTemplate.id}.json`)
                
                fs.writeFileSync(templatePath, JSON.stringify(templateForAI, null, 2))
                console.log(`   📁 Template salvo em: ${templatePath}`)
                
                return templateForAI
              } catch (parseError) {
                console.log(`   ❌ Erro ao parsear dados: ${parseError}`)
              }
            }
          }
        } catch (detailError) {
          console.log(`   💥 Erro ao buscar detalhes: ${detailError}`)
        }
      }
      
      return templates
    } else {
      console.log(`   ❌ Erro: ${response.status}`)
    }
  } catch (error) {
    console.log(`   💥 Erro: ${error}`)
  }
  
  console.log('')
  console.log('📋 Busca concluída!')
}

getElementorTemplates()