#!/usr/bin/env tsx

// Teste detalhado da autenticação
async function testAuthDetails() {
  console.log('🔍 Teste detalhado da autenticação...')
  console.log('')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  const appPassword = 'xHqa 1N5d xRaI DPr5 CGqh 7PrKd'
  
  console.log('📋 Dados sendo testados:')
  console.log(`- URL: ${baseUrl}`)
  console.log(`- Usuário: ${username}`)
  console.log(`- Senha original: "${appPassword}"`)
  
  // Teste 1: Senha sem espaços
  const passwordNoSpaces = appPassword.replace(/\s/g, '')
  console.log(`- Senha sem espaços: "${passwordNoSpaces}"`)
  
  // Teste 2: Credentials base64
  const credentials = Buffer.from(`${username}:${passwordNoSpaces}`).toString('base64')
  console.log(`- Base64: ${credentials}`)
  
  console.log('')
  console.log('🔐 Testando autenticação...')
  
  try {
    const response = await fetch(`${baseUrl}/wp-json/wp/v2/users/me`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    
    console.log(`Status: ${response.status}`)
    console.log('Headers enviados:')
    console.log(`- Authorization: Basic ${credentials.substring(0, 20)}...`)
    console.log(`- Content-Type: application/json`)
    
    if (response.ok) {
      const user = await response.json()
      console.log('')
      console.log('✅ SUCESSO! Autenticação funcionou!')
      console.log(`- ID: ${user.id}`)
      console.log(`- Nome: ${user.name}`)
      console.log(`- Username: ${user.username}`)
      console.log(`- Email: ${user.email}`)
      console.log(`- Roles: ${user.roles?.join(', ')}`)
      console.log(`- Capabilities: ${Object.keys(user.capabilities || {}).slice(0, 5).join(', ')}...`)
    } else {
      console.log('')
      console.log('❌ Falha na autenticação')
      
      const responseHeaders: Record<string, string> = {}
      response.headers.forEach((value, key) => {
        responseHeaders[key] = value
      })
      
      console.log('Response Headers:', JSON.stringify(responseHeaders, null, 2))
      
      try {
        const errorData = await response.json()
        console.log('Erro JSON:', JSON.stringify(errorData, null, 2))
      } catch {
        const errorText = await response.text()
        console.log('Erro Text:', errorText.substring(0, 500))
      }
      
      console.log('')
      console.log('💡 Próximas ações:')
      console.log('1. Verifique se a senha Application Password está correta')
      console.log('2. Acesse: https://aikenzy.com.br/wp-admin/profile.php')
      console.log('3. Na seção "Application Passwords", crie uma nova')
      console.log('4. Use exatamente a senha gerada (com espaços)')
      console.log('5. Verifique se não há plugins de segurança bloqueando')
    }
  } catch (error) {
    console.log('')
    console.log('💥 Erro de rede:', error)
  }
  
  console.log('')
  console.log('🧪 Teste alternativo com senha original (com espaços):')
  
  try {
    const credentialsWithSpaces = Buffer.from(`${username}:${appPassword}`).toString('base64')
    const response2 = await fetch(`${baseUrl}/wp-json/wp/v2/users/me`, {
      headers: {
        'Authorization': `Basic ${credentialsWithSpaces}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`Status com espaços: ${response2.status}`)
    
    if (response2.ok) {
      console.log('✅ Funcionou com espaços!')
    } else {
      console.log('❌ Também falhou com espaços')
    }
  } catch (error) {
    console.log('💥 Erro com espaços:', error)
  }
}

testAuthDetails()