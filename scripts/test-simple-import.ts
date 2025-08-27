#!/usr/bin/env tsx

// Teste simples e direto de importação
async function testSimpleImport() {
  console.log('🧪 Teste simples de importação...')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  const appPassword = '4AM0t7AhFush3HAmnbfE3Vuq'
  const credentials = Buffer.from(`${username}:${appPassword}`).toString('base64')
  
  // Template muito simples para testar
  const simpleTemplate = {
    title: 'Teste Simples AI - ' + Date.now(),
    content: [
      {
        id: 'simple-section',
        elType: 'section',
        settings: {},
        elements: [
          {
            id: 'simple-column',
            elType: 'column',
            settings: { width: '100' },
            elements: [
              {
                id: 'simple-heading',
                elType: 'widget',
                widgetType: 'heading',
                settings: {
                  title: 'Hello KenzySites AI!'
                }
              }
            ]
          }
        ]
      }
    ],
    status: 'draft'
  }
  
  console.log('📤 Enviando template simples...')
  console.log(`   Título: ${simpleTemplate.title}`)
  console.log(`   Seções: ${simpleTemplate.content.length}`)
  console.log(`   Status: ${simpleTemplate.status}`)
  
  try {
    const response = await fetch(`${baseUrl}/wp-json/kenzysites/v1/elementor/import`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(simpleTemplate)
    })
    
    console.log(`📡 Resposta: ${response.status}`)
    
    const responseText = await response.text()
    
    try {
      const responseData = JSON.parse(responseText)
      
      if (response.ok) {
        console.log('🎉 SUCESSO! Template importado!')
        console.log(`   ID: ${responseData.page_id}`)
        console.log(`   URL: ${responseData.page_url}`)
        console.log(`   Editar: ${responseData.edit_url}`)
      } else {
        console.log('❌ Erro na importação:')
        console.log(`   Código: ${responseData.code}`)
        console.log(`   Mensagem: ${responseData.message}`)
      }
    } catch (parseError) {
      console.log('📜 Resposta (texto):', responseText)
    }
    
  } catch (error) {
    console.log('💥 Erro de rede:', error)
  }
}

testSimpleImport()