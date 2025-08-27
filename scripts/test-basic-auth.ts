#!/usr/bin/env tsx

// Teste com autenticação básica (senha normal)
async function testBasicAuth() {
  console.log('🔐 Teste com autenticação básica...')
  console.log('')
  
  const baseUrl = 'https://aikenzy.com.br'
  const username = 'dkenzy'
  
  console.log('⚠️  ATENÇÃO: Este script vai pedir sua senha do WordPress!')
  console.log('👤 Usuário:', username)
  console.log('🌐 Site:', baseUrl)
  console.log('')
  
  // Para teste, vou usar uma senha fictícia
  // SUBSTITUA pela sua senha real do WordPress
  const password = 'SUA_SENHA_WORDPRESS_AQUI'
  
  const credentials = Buffer.from(`${username}:${password}`).toString('base64')
  
  try {
    const response = await fetch(`${baseUrl}/wp-json/wp/v2/users/me`, {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log(`Status: ${response.status}`)
    
    if (response.ok) {
      const user = await response.json()
      console.log('✅ Sucesso com autenticação básica!')
      console.log(`- Nome: ${user.name}`)
      console.log(`- Roles: ${user.roles?.join(', ')}`)
      console.log('')
      console.log('🔧 PRÓXIMO PASSO:')
      console.log('1. Acesse: https://aikenzy.com.br/wp-admin/profile.php')
      console.log('2. Role até "Application Passwords"')  
      console.log('3. Crie nova senha com nome "KenzySites"')
      console.log('4. Use a senha gerada no código')
    } else {
      const error = await response.text()
      console.log('❌ Falhou mesmo com senha normal')
      console.log('Erro:', error)
    }
  } catch (error) {
    console.log('💥 Erro:', error)
  }
}

testBasicAuth()