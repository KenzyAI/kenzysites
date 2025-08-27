#!/usr/bin/env tsx

// Analisa estrutura dos templates: Containers vs Sections

import { readFileSync } from 'fs'
import { glob } from 'glob'
import { join } from 'path'

interface TemplateAnalysis {
  file: string
  title: string
  hasContainers: boolean
  hasSections: boolean
  totalElements: number
  structure: 'containers' | 'sections' | 'mixed' | 'empty'
  performance: 'modern' | 'legacy'
}

async function analyzeTemplates() {
  console.log('🔍 Analisando estrutura dos templates Elementor...')
  console.log('')
  
  const templateFiles = await glob('lib/ai-builder/templates/**/*.json')
  const analyses: TemplateAnalysis[] = []
  
  for (const file of templateFiles) {
    try {
      const content = JSON.parse(readFileSync(file, 'utf8'))
      const jsonString = JSON.stringify(content)
      
      const hasContainers = jsonString.includes('"elType":"container"')
      const hasSections = jsonString.includes('"elType":"section"')
      const totalElements = content.content?.length || 0
      
      let structure: TemplateAnalysis['structure'] = 'empty'
      if (hasContainers && hasSections) structure = 'mixed'
      else if (hasContainers) structure = 'containers' 
      else if (hasSections) structure = 'sections'
      
      const performance = hasContainers ? 'modern' : 'legacy'
      
      const analysis: TemplateAnalysis = {
        file: file.replace(process.cwd() + '/', ''),
        title: content.title || 'Sem título',
        hasContainers,
        hasSections,
        totalElements,
        structure,
        performance
      }
      
      analyses.push(analysis)
      
    } catch (error) {
      console.log(`❌ Erro ao analisar ${file}: ${error}`)
    }
  }
  
  // Relatório resumido
  console.log('📊 RELATÓRIO DE ANÁLISE:')
  console.log('=' + '='.repeat(50))
  
  const modern = analyses.filter(a => a.performance === 'modern').length
  const legacy = analyses.filter(a => a.performance === 'legacy').length
  
  console.log(`🚀 Templates MODERNOS (Containers): ${modern}`)
  console.log(`🏗️  Templates LEGADOS (Sections): ${legacy}`)
  console.log(`📈 Performance Score: ${Math.round(modern / analyses.length * 100)}%`)
  console.log('')
  
  // Detalhamento
  console.log('📋 DETALHAMENTO POR TEMPLATE:')
  console.log('-' + '-'.repeat(70))
  
  analyses.forEach(analysis => {
    const icon = analysis.performance === 'modern' ? '✅' : '🏗️'
    const structure = analysis.structure.toUpperCase()
    
    console.log(`${icon} ${analysis.title}`)
    console.log(`   📁 ${analysis.file}`)
    console.log(`   🔧 Estrutura: ${structure} (${analysis.totalElements} elementos)`)
    console.log(`   ⚡ Performance: ${analysis.performance.toUpperCase()}`)
    console.log('')
  })
  
  // Recomendações
  console.log('🎯 RECOMENDAÇÕES:')
  console.log('-' + '-'.repeat(30))
  
  if (legacy > 0) {
    console.log(`🔄 ${legacy} templates precisam ser convertidos para Containers`)
    console.log('   Use: Elementor > Edit Section > Layout > Convert')
  }
  
  if (modern > 0) {
    console.log(`✅ ${modern} templates já estão otimizados para 2025`)
  }
  
  console.log('')
  console.log('💡 Templates com Containers têm melhor performance e flexibilidade!')
}

analyzeTemplates().catch(console.error)