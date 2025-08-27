# 🎯 Guia Completo: Como Criar Landing Pages com Placeholders Inteligentes

## Por que usar Placeholders?

Ao invés de criar templates genéricos e tentar "adivinhar" o que mudar, você cria templates com **marcadores específicos** que serão substituídos por conteúdo personalizado gerado por IA.

## ✅ MÉTODO CORRETO: Templates com Placeholders

### 1. Estrutura de Placeholders

Use a sintaxe: `{{NOME_DO_PLACEHOLDER}}`

```
{{BUSINESS_NAME}} - Nome do negócio
{{BUSINESS_SPECIALTY}} - Especialidade
{{MAIN_HEADLINE}} - Título principal
{{PRIMARY_CTA}} - Botão principal
{{PHONE}} - Telefone
{{EMAIL}} - Email
```

### 2. Categorias de Placeholders

#### 📋 **Negócio (Business)**
```
{{BUSINESS_NAME}} - "Dra. Mariana Silva"
{{BUSINESS_SPECIALTY}} - "Dermatologia Avançada" 
{{MAIN_DESCRIPTION}} - "Especialista em cuidados com a pele"
{{EXPERIENCE_YEARS}} - "15"
{{LOCATION}} - "São Paulo, SP"
{{WEBSITE}} - "dramariana.com.br"
```

#### 📞 **Contato (Contact)**
```
{{PHONE}} - "(11) 99999-9999"
{{EMAIL}} - "contato@dramariana.com.br"
{{WHATSAPP}} - "(11) 99999-9999"
{{ADDRESS}} - "Rua das Flores, 123 - Centro"
```

#### 🛍️ **Serviços (Services)**
```
{{SERVICES_LIST}} - "Consultas, Tratamentos Estéticos, Botox"
{{SERVICE_1}} - "Consultas Dermatológicas"
{{SERVICE_2}} - "Tratamentos Estéticos" 
{{SERVICE_3}} - "Botox e Preenchimento"
{{SERVICE_1_DESC}} - "Avaliação completa da pele"
```

#### 🚀 **Call-to-Actions (CTA)**
```
{{PRIMARY_CTA}} - "Agendar Consulta"
{{SECONDARY_CTA}} - "Marcar Avaliação" 
{{CONTACT_CTA}} - "Fale Conosco"
{{WHATSAPP_CTA}} - "Chamar no WhatsApp"
```

#### 🌟 **Benefícios/Features**
```
{{BENEFIT_1}} - "Atendimento personalizado"
{{BENEFIT_2}} - "Equipamentos modernos"
{{BENEFIT_3}} - "Resultados comprovados"
{{USP}} - "Única clínica com certificação X na região"
```

#### 💬 **Testemunhos (Testimonials)**
```
{{TESTIMONIAL_1_TEXT}} - "Excelente profissional, muito atenciosa"
{{TESTIMONIAL_1_AUTHOR}} - "Ana Silva"
{{TESTIMONIAL_1_ROLE}} - "Paciente há 2 anos"
```

## 🎨 Como Aplicar no Elementor

### 1. **Título Principal (Heading Widget)**
```
Ao invés de: "Dra. Mariana Silva - Dermatologia"
Use: "{{BUSINESS_NAME}} - {{BUSINESS_SPECIALTY}}"
```

### 2. **Texto Descritivo (Text Editor)**
```
Ao invés de: "Cuidados especializados para sua pele com 15 anos de experiência"
Use: "{{MAIN_DESCRIPTION}} com {{EXPERIENCE_YEARS}} anos de experiência"
```

### 3. **Botões (Button Widget)**
```
Ao invés de: "Agendar Consulta"
Use: "{{PRIMARY_CTA}}"
```

### 4. **Lista de Serviços**
```
Ao invés de: "Consultas • Botox • Preenchimento"
Use: "{{SERVICE_1}} • {{SERVICE_2}} • {{SERVICE_3}}"
```

### 5. **Informações de Contato**
```
Telefone: {{PHONE}}
Email: {{EMAIL}}
Localização: {{LOCATION}}
```

## 🤖 Como os Agentes Inteligentes Funcionam

### 1. **Análise Semântica**
O agente analisa:
- Tipo de negócio (médico, restaurante, empresa)
- Contexto da seção (hero, sobre, serviços)
- Tom de voz (profissional, casual, urgente)

### 2. **Geração Contextual**
Para um cardiologista, o agente gera:
```
{{BUSINESS_SPECIALTY}} → "Cardiologia Intervencionista"
{{PRIMARY_CTA}} → "Agendar Consulta Cardiológica"  
{{BENEFIT_1}} → "Diagnóstico preciso e rápido"
```

Para um restaurante:
```
{{BUSINESS_SPECIALTY}} → "Culinária Italiana Autêntica"
{{PRIMARY_CTA}} → "Fazer Reserva"
{{BENEFIT_1}} → "Ingredientes frescos e importados"
```

## 📝 Exemplo Prático Completo

### Template Original (ERRADO):
```html
<h1>Dra. Mariana Silva</h1>
<h2>Dermatologista</h2>
<p>Tratamentos especializados para sua pele</p>
<button>Agendar Consulta</button>
<span>(11) 99999-9999</span>
```

### Template com Placeholders (CORRETO):
```html
<h1>{{BUSINESS_NAME}}</h1>
<h2>{{BUSINESS_SPECIALTY}}</h2>
<p>{{MAIN_DESCRIPTION}}</p>
<button>{{PRIMARY_CTA}}</button>
<span>{{PHONE}}</span>
```

### Resultado Personalizado para Cardiologista:
```html
<h1>Dr. Carlos Mendes</h1>
<h2>Cardiologia Intervencionista</h2>
<p>Tratamentos cardiovasculares de alta precisão</p>
<button>Agendar Consulta Cardiológica</button>
<span>(21) 98888-7777</span>
```

## 🔧 Implementação no Seu Workflow

### Passo 1: Converter Templates Existentes
1. Abra seu template no Elementor
2. Substitua textos específicos por placeholders
3. Exporte o template
4. Salve na biblioteca do AI Builder

### Passo 2: Definir Mapeamentos
```typescript
const placeholderMappings = {
  'medical': {
    'BUSINESS_SPECIALTY': 'Especialidade médica',
    'PRIMARY_CTA': 'Agendar Consulta',
    'BENEFIT_1': 'Atendimento especializado'
  },
  'restaurant': {
    'BUSINESS_SPECIALTY': 'Tipo de culinária', 
    'PRIMARY_CTA': 'Fazer Reserva',
    'BENEFIT_1': 'Ambiente aconchegante'
  }
}
```

### Passo 3: Usar no AI Builder
```typescript
const result = await aiBuilder.buildFromPrompt({
  businessInfo: {
    name: 'Dr. João',
    type: 'medical',
    specialty: 'Cardiologia'
  },
  templateId: 'medical-placeholder-template',
  placeholders: true // Usar sistema de placeholders
})
```

## 🎯 Vantagens do Sistema de Placeholders

### ✅ **Controle Total**
- Você define exatamente o que será personalizado
- Mantém layout e design intactos
- Previsibilidade nos resultados

### ✅ **Escalabilidade** 
- Um template funciona para múltiplos negócios
- Fácil manutenção e atualizações
- Reutilização eficiente

### ✅ **Qualidade**
- Conteúdo contextual e relevante
- Mantém consistência visual
- Evita alterações indesejadas

### ✅ **Flexibilidade**
- Diferentes níveis de personalização
- Fallbacks para campos não preenchidos
- Validação de conteúdo

## 🚀 Próximos Passos

1. **Converta seus melhores templates** para usar placeholders
2. **Teste com diferentes tipos de negócio** para validar versatilidade  
3. **Integre com API da OpenAI/Claude** para geração mais inteligente
4. **Crie interface visual** para preview em tempo real

---

💡 **DICA IMPORTANTE**: Comece convertendo 1-2 templates que você mais usa. Teste bem antes de expandir para toda sua biblioteca.

🎯 **RESULTADO**: Landing pages verdadeiramente personalizadas que mantêm sua qualidade de design e são 100% relevantes para cada cliente.