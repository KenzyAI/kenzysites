# KenzySites Converter Plugin

Plugin WordPress para converter landing pages Elementor em templates ACF para o sistema KenzySites.

## 🎯 **Objetivo**

Permite monetizar um portfólio de 10 anos de landing pages Elementor convertendo-as automaticamente para templates ACF personalizáveis no sistema KenzySites.

## 🚀 **Funcionalidades**

### **📋 Escaneamento Inteligente**
- ✅ Detecta todas as páginas Elementor do site
- ✅ Analisa estrutura e complexidade de cada página
- ✅ Sugere tipo de landing page baseado no conteúdo
- ✅ Calcula score de conversão (0-100%)
- ✅ Identifica elementos dinâmicos e CTAs

### **⚙️ Conversão Automática**
- ✅ Converte Elementor para campos ACF
- ✅ Preserva design original (modo híbrido)
- ✅ Cria grupos de campos personalizados
- ✅ Extrai conteúdo dinâmico automaticamente
- ✅ Suporte a 10+ tipos de landing page

### **🔄 Sincronização com KenzySites**
- ✅ Envia templates automaticamente via API
- ✅ Sincronização em tempo real
- ✅ Sistema de retry para falhas
- ✅ Logs detalhados de operações
- ✅ Status de sincronização em dashboard

### **📊 Dashboard Completo**
- ✅ Estatísticas em tempo real
- ✅ Progresso de conversões
- ✅ Status de sincronização
- ✅ Atividade recente
- ✅ Saúde do sistema

## 📦 **Instalação**

### **Requisitos**
- WordPress 5.0+
- PHP 7.4+
- Plugin Elementor ativo
- Sistema KenzySites configurado

### **Passos**
1. Faça upload do plugin para `/wp-content/plugins/kenzysites-converter/`
2. Ative o plugin no painel WordPress
3. Acesse **KenzySites** no menu admin
4. Configure a API em **Configurações**

## ⚙️ **Configuração**

### **1. Configurar API**
```
Configurações → KenzySites
- URL da API: http://seu-kenzysites.com/api
- API Key: sua_chave_secreta
```

### **2. Testar Conexão**
```
Dashboard → Testar Conexão KenzySites
```

### **3. Primeira Conversão**
```
Converter → Escanear Páginas Elementor → Selecionar → Converter
```

## 📖 **Como Usar**

### **Conversão Individual**
1. Vá em **KenzySites → Converter**
2. Clique em **"Escanear Páginas Elementor"**
3. Escolha uma página da lista
4. Selecione o tipo de landing page
5. Clique em **"Converter"**
6. Template será sincronizado automaticamente

### **Conversão em Lote**
1. Acesse aba **"Conversão em Lote"**
2. Configure tipo padrão e filtros
3. Clique em **"Iniciar Conversão em Lote"**
4. Acompanhe o progresso em tempo real

### **Gerenciar Templates**
1. Vá em **"Templates Convertidos"**
2. Visualize todos os templates criados
3. Sincronize templates pendentes
4. Veja detalhes e estatísticas

## 🔧 **API do KenzySites**

O plugin se comunica com os seguintes endpoints:

```bash
# Teste de conexão
GET /api/health

# Conversão de template
POST /api/templates/elementor/convert

# Status do template
GET /api/templates/landing-pages/{id}

# Tipos de landing page
GET /api/templates/landing-pages/types
```

## 📋 **Tipos de Landing Page**

| Tipo | Descrição | Campos ACF Incluídos |
|------|-----------|---------------------|
| **Lead Generation** | Captura de leads | Hero, Form, Testimonials |
| **Service Showcase** | Apresenta serviços | Hero, Services, Testimonials, Form |
| **Product Launch** | Lançamento de produto | Hero, Features, Pricing |
| **Event Promotion** | Promoção de evento | Hero, Event Info, Form |
| **Webinar** | Inscrições webinar | Hero, Video, Form, Testimonials |
| **Coming Soon** | Em breve | Hero, Form |
| **Thank You** | Agradecimento | Hero, Message |
| **Download** | Download material | Hero, Download, Form |

## 📊 **Campos ACF Gerados**

### **Básicos (Todos os tipos)**
- Hero Section (título, subtítulo, CTA)
- Informações de Contato
- Configurações SEO
- Analytics e Tracking

### **Específicos por Tipo**
- **Serviços**: Lista de serviços com ícones
- **Depoimentos**: Carrossel de testimonials
- **Formulários**: Campos customizáveis
- **Pricing**: Tabelas de preços
- **Eventos**: Data, local, palestrantes

## 🐛 **Troubleshooting**

### **Plugin não encontra páginas Elementor**
```bash
# Verifique se Elementor está ativo
wp plugin list | grep elementor

# Verifique se há páginas com Elementor
wp db query "SELECT COUNT(*) FROM wp_postmeta WHERE meta_key = '_elementor_edit_mode'"
```

### **Erro de conexão com API**
1. Verifique URL e API Key
2. Teste conexão manual: `curl -H "Authorization: Bearer SUA_API_KEY" http://api-url/health`
3. Verifique logs: `wp debug.log`

### **Templates não sincronizam**
1. Vá em **Templates Convertidos**
2. Clique em **"Sincronizar"** no template com erro
3. Verifique mensagem de erro
4. Teste conexão API novamente

## 📁 **Estrutura do Plugin**

```
kenzysites-converter/
├── kenzysites-converter.php          # Arquivo principal
├── includes/
│   ├── class-elementor-scanner.php   # Escaneia páginas Elementor
│   ├── class-acf-converter.php       # Converte para ACF
│   ├── class-api-client.php          # Comunica com KenzySites
│   └── class-admin-page.php          # Interface admin
├── admin/
│   ├── views/
│   │   ├── dashboard.php             # Dashboard principal
│   │   ├── converter.php             # Tela de conversão
│   │   └── settings.php              # Configurações
│   ├── css/admin-style.css           # Estilos admin
│   └── js/admin-script.js            # JavaScript admin
└── README.md
```

## 🔧 **Desenvolvimento**

### **Hooks Disponíveis**
```php
// Antes da conversão
do_action('kenzysites_before_conversion', $page_id, $landing_page_type);

// Depois da conversão
do_action('kenzysites_after_conversion', $template_id, $result);

// Antes da sincronização
do_action('kenzysites_before_sync', $template_id);

// Depois da sincronização
do_action('kenzysites_after_sync', $template_id, $result);
```

### **Filtros Disponíveis**
```php
// Modificar dados antes do envio
$data = apply_filters('kenzysites_template_data', $data, $template_id);

// Modificar grupos de campos ACF
$field_groups = apply_filters('kenzysites_acf_field_groups', $field_groups, $landing_page_type);

// Customizar análise de página
$analysis = apply_filters('kenzysites_page_analysis', $analysis, $page_id);
```

## 📈 **Analytics e Logs**

### **Dashboard Analytics**
- Total de páginas escaneadas
- Templates convertidos vs páginas totais
- Taxa de sincronização
- Atividade recente

### **Logs do Sistema**
```bash
# Ver logs WordPress
tail -f wp-content/debug.log | grep "KenzySites"

# Logs do plugin (se WP_DEBUG = true)
```

## 🚀 **Roadmap**

### **Versão 1.1**
- [ ] Suporte a Custom Post Types
- [ ] Templates de e-commerce (WooCommerce)
- [ ] Importação de templates externos
- [ ] Backup automático antes conversão

### **Versão 1.2**
- [ ] Editor visual de campos ACF
- [ ] Conversão reversa (ACF → Elementor)
- [ ] Integração com Page Builders alternativos
- [ ] API para developers externos

## 📞 **Suporte**

Para suporte e dúvidas:

1. **GitHub Issues**: Para bugs e melhorias
2. **Documentação**: README.md completo
3. **Logs**: Ative WP_DEBUG para logs detalhados

## 📝 **Changelog**

### **v1.0.0**
- ✅ Conversão Elementor para ACF
- ✅ Sincronização automática com KenzySites
- ✅ Dashboard com estatísticas
- ✅ 10+ tipos de landing page
- ✅ Conversão em lote
- ✅ Interface admin completa

---

**Desenvolvido para monetizar 10 anos de experiência em Elementor através do sistema KenzySites.**