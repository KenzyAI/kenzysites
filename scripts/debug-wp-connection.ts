#!/usr/bin/env tsx

// Script para debugar conexão com WordPress hospedado
async function debugConnection() {
  console.log('🔍 Debugando conexão com WordPress...')
  console.log('')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  const appPassword = 'xHqa1N5dxRaIDPr5CGqh7PrKd'
  
  // Teste 1: Verificar se REST API está disponível
  console.log('📡 Teste 1: Verificando disponibilidade da REST API...')
  try {
    const response = await fetch(`${baseUrl}/wp-json/wp/v2/`)
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      const data = await response.json()
      console.log(`   ✅ REST API disponível`)
      console.log(`   - Nome: ${data.name}`)
      console.log(`   - Descrição: ${data.description}`)
      console.log(`   - URL: ${data.url}`)
    } else {
      console.log(`   ❌ REST API não disponível (${response.status})`)
      const text = await response.text()
      console.log(`   Resposta: ${text.substring(0, 200)}...`)
    }
  } catch (error) {
    console.log(`   💥 Erro: ${error}`)
  }
  
  console.log('')
  
  // Teste 2: Tentar autenticação
  console.log('🔐 Teste 2: Testando autenticação...')
  const credentials = Buffer.from(`${username}:${appPassword}`).toString('base64')
  console.log(`   Usuário: ${username}`)
  console.log(`   Senha: ${appPassword.substring(0, 4)}...`)
  console.log(`   Credentials: ${credentials.substring(0, 20)}...`)
  
  try {
    const response = await fetch(`${baseUrl}/wp-json/wp/v2/users/me`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      const user = await response.json()
      console.log(`   ✅ Autenticação bem-sucedida!`)
      console.log(`   - ID: ${user.id}`)
      console.log(`   - Nome: ${user.name}`)
      console.log(`   - Email: ${user.email}`)
      console.log(`   - Roles: ${user.roles?.join(', ')}`)
    } else {
      const errorText = await response.text()
      console.log(`   ❌ Falha na autenticação`)
      console.log(`   Erro: ${errorText}`)
    }
  } catch (error) {
    console.log(`   💥 Erro: ${error}`)
  }
  
  console.log('')
  
  // Teste 3: Verificar plugins endpoint
  console.log('🔌 Teste 3: Verificando endpoint de plugins...')
  try {
    const response = await fetch(`${baseUrl}/wp-json/wp/v2/plugins`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      const plugins = await response.json()
      console.log(`   ✅ Plugins endpoint acessível`)
      console.log(`   - Total de plugins: ${plugins.length}`)
      
      const elementor = plugins.find((p: any) => p.name === 'Elementor')
      if (elementor) {
        console.log(`   - Elementor: ${elementor.status} (v${elementor.version})`)
      } else {
        console.log(`   - Elementor: Não encontrado`)
      }
    } else {
      console.log(`   ❌ Plugins endpoint não acessível`)
      const errorText = await response.text()
      console.log(`   Erro: ${errorText}`)
    }
  } catch (error) {
    console.log(`   💥 Erro: ${error}`)
  }
  
  console.log('')
  
  // Teste 4: Verificar Elementor API
  console.log('🎨 Teste 4: Verificando Elementor API...')
  try {
    const response = await fetch(`${baseUrl}/wp-json/elementor/v1/globals`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`   Status: ${response.status}`)
    
    if (response.ok) {
      console.log(`   ✅ Elementor API disponível`)
    } else {
      console.log(`   ❌ Elementor API não disponível`)
    }
  } catch (error) {
    console.log(`   💥 Erro: ${error}`)
  }
  
  console.log('')
  console.log('📋 Relatório completo gerado!')
}

debugConnection().catch(console.error)