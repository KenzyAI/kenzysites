#!/usr/bin/env tsx

// Teste específico dos endpoints do plugin KenzySites
async function testPluginEndpoints() {
  console.log('🔌 Testando endpoints do plugin KenzySites...')
  console.log('')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  const appPassword = '4AM0t7AhFush3HAmnbfE3Vuq'
  
  const credentials = Buffer.from(`${username}:${appPassword}`).toString('base64')
  
  // Teste 1: Status do Elementor via plugin
  console.log('📊 Teste 1: Status do Elementor (plugin KenzySites)...')
  try {
    const response = await fetch(`${baseUrl}/wp-json/kenzysites/v1/elementor/status`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      const data = await response.json()
      console.log('   ✅ Plugin KenzySites funcionando!')
      console.log(`   - Elementor ativo: ${data.elementor_active}`)
      console.log(`   - Versão Elementor: ${data.elementor_version}`)
      console.log(`   - Elementor Pro: ${data.elementor_pro_active}`)
      console.log(`   - WordPress: ${data.wordpress_version}`)
      console.log(`   - PHP: ${data.php_version}`)
      console.log(`   - Pode importar: ${data.can_import}`)
    } else {
      const errorText = await response.text()
      if (response.status === 404) {
        console.log('   ❌ Plugin KenzySites NÃO está instalado/ativo')
        console.log('   💡 AÇÃO: Instale o plugin kenzysites-ai-builder.zip')
      } else {
        console.log(`   ❌ Erro: ${errorText}`)
      }
    }
  } catch (error) {
    console.log(`   💥 Erro de rede: ${error}`)
  }
  
  console.log('')
  
  // Teste 2: Importação de template (só se status funcionou)
  console.log('📥 Teste 2: Importação de template de teste...')
  try {
    const testTemplate = {
      title: 'Teste AI Builder - ' + new Date().toLocaleString(),
      content: [
        {
          id: 'test-section',
          elType: 'section',
          settings: {
            background_background: 'classic',
            background_color: '#f0f0f0'
          },
          elements: [
            {
              id: 'test-column',
              elType: 'column',
              settings: { width: '100' },
              elements: [
                {
                  id: 'test-heading',
                  elType: 'widget',
                  widgetType: 'heading',
                  settings: {
                    title: 'Teste do KenzySites AI Builder',
                    align: 'center'
                  }
                }
              ]
            }
          ]
        }
      ],
      type: 'page',
      status: 'draft' // Draft para não atrapalhar o site
    }
    
    const response = await fetch(`${baseUrl}/wp-json/kenzysites/v1/elementor/import`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testTemplate)
    })
    
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      const data = await response.json()
      console.log('   ✅ Template importado com sucesso!')
      console.log(`   - ID da Página: ${data.page_id}`)
      console.log(`   - URL: ${data.page_url}`)
      console.log(`   - Editar: ${data.edit_url}`)
      console.log(`   - Mensagem: ${data.message}`)
    } else {
      const errorText = await response.text()
      console.log(`   ❌ Falha na importação: ${errorText}`)
    }
  } catch (error) {
    console.log(`   💥 Erro: ${error}`)
  }
  
  console.log('')
  console.log('📋 Resumo:')
  console.log('- Se status funcionou: Plugin está ativo ✅')
  console.log('- Se status falhou (404): Instale o plugin primeiro')
  console.log('- Se importação funcionou: Sistema completo funcionando! 🎉')
}

testPluginEndpoints()