#!/usr/bin/env tsx

// Teste REAL de substituição de texto no template do usuário
import { readFileSync, writeFileSync } from 'fs'
import { join } from 'path'

async function testRealTextReplacement() {
  console.log('🔍 Analisando SEU template e substituindo textos REAIS...')
  console.log('')
  
  // Carregar seu template
  const templatePath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library/custom-22.json')
  const template = JSON.parse(readFileSync(templatePath, 'utf-8'))
  
  console.log(`📋 Template: ${template.title}`)
  console.log(`   Seções: ${template.content.length}`)
  console.log('')
  
  // Função para encontrar e listar todos os textos
  function extractAllTexts(elements: any[], level = 0): any[] {
    const texts: any[] = []
    const indent = '  '.repeat(level)
    
    elements.forEach((element, index) => {
      if (element.settings) {
        // Campos de texto comuns no Elementor
        const textFields = ['title', 'text', 'editor', 'content', 'caption', 'description', 'button_text']
        
        textFields.forEach(field => {
          if (element.settings[field] && typeof element.settings[field] === 'string') {
            const text = element.settings[field].trim()
            if (text.length > 0) {
              texts.push({
                elementId: element.id,
                elementType: element.elType,
                widgetType: element.widgetType,
                field: field,
                originalText: text,
                path: `${level}-${index}`,
                element: element
              })
              console.log(`${indent}📝 ${element.widgetType || element.elType} (${field}): "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`)
            }
          }
        })
      }
      
      // Recursivo para elementos filhos
      if (element.elements) {
        texts.push(...extractAllTexts(element.elements, level + 1))
      }
    })
    
    return texts
  }
  
  // Extrair todos os textos
  console.log('🔎 Textos encontrados no template:')
  const allTexts = extractAllTexts(template.content)
  
  console.log('')
  console.log(`📊 Total de textos encontrados: ${allTexts.length}`)
  console.log('')
  
  // Criar versão personalizada para médica
  const medicalBusinessInfo = {
    name: 'Dra. Mariana Silva',
    specialty: 'Dermatologia',
    services: ['Consultas', 'Tratamentos Estéticos', 'Botox', 'Preenchimento'],
    phone: '(11) 99999-9999',
    email: 'contato@dramariana.com.br'
  }
  
  console.log('🩺 Personalizando para médica dermatologista...')
  
  // Substituições inteligentes baseadas no contexto
  const customizedTemplate = JSON.parse(JSON.stringify(template)) // Deep clone
  
  let replacementCount = 0
  
  function replaceInElements(elements: any[]) {
    elements.forEach(element => {
      if (element.settings) {
        const textFields = ['title', 'text', 'editor', 'content', 'caption', 'description', 'button_text']
        
        textFields.forEach(field => {
          if (element.settings[field] && typeof element.settings[field] === 'string') {
            let text = element.settings[field]
            const originalText = text
            
            // Substituições específicas (você pode personalizar baseado no seu template)
            
            // Nomes genéricos
            text = text.replace(/Dr\.\s*Mariana/gi, medicalBusinessInfo.name)
            text = text.replace(/Mariana/gi, 'Dra. Mariana Silva')
            
            // Especialidades
            text = text.replace(/dermatolog(ia|ista)/gi, 'Dermatologia Avançada')
            
            // Serviços
            if (text.toLowerCase().includes('serviç') || text.toLowerCase().includes('tratament')) {
              text = text.replace(/tratamentos?\s+\w+/gi, 'Tratamentos Dermatológicos')
            }
            
            // Contatos
            text = text.replace(/\(\d{2}\)\s*\d{4,5}-?\d{4}/g, medicalBusinessInfo.phone)
            text = text.replace(/\w+@\w+\.\w+/g, medicalBusinessInfo.email)
            
            // CTAs
            text = text.replace(/agendar?\s+consulta/gi, 'Agendar Consulta Dermatológica')
            text = text.replace(/entre\s+em\s+contato/gi, 'Agende sua Consulta')
            
            // Benefícios específicos de dermatologia
            if (text.toLowerCase().includes('pele') || text.toLowerCase().includes('rosto')) {
              text = text.replace(/cuidados?\s+\w+/gi, 'Cuidados Dermatológicos Especializados')
            }
            
            if (text !== originalText) {
              element.settings[field] = text
              replacementCount++
              console.log(`   ✅ Substituído (${element.widgetType || element.elType}):`)
              console.log(`      De: "${originalText.substring(0, 40)}..."`)
              console.log(`      Para: "${text.substring(0, 40)}..."`)
            }
          }
        })
      }
      
      if (element.elements) {
        replaceInElements(element.elements)
      }
    })
  }
  
  replaceInElements(customizedTemplate.content)
  
  console.log('')
  console.log(`📊 Total de substituições: ${replacementCount}`)
  
  if (replacementCount > 0) {
    // Salvar template personalizado
    const customizedPath = join(process.cwd(), 'lib/ai-builder/templates/elementor/library/custom-22-medical.json')
    writeFileSync(customizedPath, JSON.stringify(customizedTemplate, null, 2))
    
    console.log(`📁 Template personalizado salvo em: ${customizedPath}`)
    
    // Testar importação no WordPress
    console.log('')
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
          title: 'Teste REAL - Dra. Mariana (Personalizado)',
          content: customizedTemplate.content,
          status: 'draft'
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ Template personalizado importado!')
        console.log(`   URL: ${result.page_url}`)
        console.log(`   ID: ${result.page_id}`)
        console.log('')
        console.log('🎯 Agora compare:')
        console.log(`   Original: https://aikenzy.com.br/?elementor_library=lp-dr-mariana-2`)
        console.log(`   Personalizado: ${result.page_url}`)
      } else {
        console.log('❌ Erro na importação:', await response.text())
      }
    } catch (error) {
      console.log('💥 Erro:', error)
    }
    
  } else {
    console.log('⚠️  Nenhuma substituição foi feita. Talvez precise ajustar as regras de substituição.')
    console.log('💡 Dica: Analise os textos listados acima e ajuste as regex no código.')
  }
}

testRealTextReplacement()