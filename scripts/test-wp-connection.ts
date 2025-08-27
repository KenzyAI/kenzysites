#!/usr/bin/env tsx

// Script para testar conexão com WordPress hospedado
import { testHostedWordPressConnection } from '../lib/wordpress/connection-test'

async function main() {
  console.log('🚀 Iniciando teste de conexão com WordPress hospedado...')
  console.log('📡 URL: https://aikenzy.com.br')
  console.log('👤 Usuário: dkenzy')
  console.log('')
  
  const result = await testHostedWordPressConnection()
  
  if (result.success) {
    console.log('')
    console.log('🎉 Conexão configurada e funcionando!')
    console.log('✨ Pronto para implementar o AI Builder!')
  } else {
    console.log('')
    console.log('⚠️  Problemas encontrados:')
    console.log(`   ${result.error}`)
    console.log('')
    console.log('💡 Possíveis soluções:')
    console.log('   1. Verificar se a senha de aplicativo está correta')
    console.log('   2. Confirmar se o usuário tem permissões adequadas')  
    console.log('   3. Verificar se o WordPress REST API está habilitado')
    console.log('   4. Confirmar se há plugins de segurança bloqueando')
  }
  
  process.exit(result.success ? 0 : 1)
}

main().catch(error => {
  console.error('💥 Erro fatal:', error)
  process.exit(1)
})