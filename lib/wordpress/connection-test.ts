// Test connection with hosted WordPress
import { createHostedWordPressClient } from './hosted-client'

export async function testHostedWordPressConnection() {
  console.log('🔄 Testando conexão com WordPress hospedado...')
  
  const client = createHostedWordPressClient()
  
  try {
    const result = await client.testHostedConnection()
    
    if (result.success) {
      console.log('✅ Conexão estabelecida com sucesso!')
      console.log('📋 Informações do site:')
      console.log(`   - Nome: ${result.siteInfo?.name}`)
      console.log(`   - URL: ${result.siteInfo?.url}`)
      console.log(`   - Versão WP: ${result.siteInfo?.gmt_offset}`)
      console.log(`   - Multisite: ${result.isMultisite ? 'Sim' : 'Não'}`)
      console.log(`   - Elementor: ${result.elementorActive ? 'Ativo ✅' : 'Inativo ❌'}`)
      console.log(`   - Usuário: ${result.currentUser?.name} (@${result.currentUser?.username})`)
      console.log(`   - Roles: ${result.currentUser?.roles?.join(', ')}`)
      
      // Test Elementor info
      const elementorInfo = await client.getElementorInfo()
      if (elementorInfo.active) {
        console.log('🎨 Informações do Elementor:')
        console.log(`   - Versão: ${elementorInfo.version}`)
        console.log(`   - Elementor Pro: ${elementorInfo.proActive ? 'Sim' : 'Não'}`)
        console.log(`   - Templates: ${elementorInfo.templates?.length || 0}`)
      }
      
      // If multisite, list sites
      if (result.isMultisite) {
        const networkSites = await client.listNetworkSites()
        if (networkSites.success && networkSites.sites) {
          console.log('🌐 Sites na rede:')
          networkSites.sites.forEach(site => {
            console.log(`   - ${site.blogname} (${site.domain}${site.path})`)
          })
        }
      }
      
      return {
        success: true,
        client,
        info: result
      }
    } else {
      console.error('❌ Falha na conexão:', result.message)
      return {
        success: false,
        error: result.message
      }
    }
  } catch (error) {
    console.error('💥 Erro inesperado:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Erro desconhecido'
    }
  }
}

// Quick test function for development
export async function quickConnectionTest(): Promise<boolean> {
  const result = await testHostedWordPressConnection()
  return result.success
}