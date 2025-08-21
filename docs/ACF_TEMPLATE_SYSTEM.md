# Sistema de Templates WordPress com ACF

## Visão Geral

O sistema implementado permite a criação, gestão e sincronização de templates WordPress com campos ACF (Advanced Custom Fields) personalizados para diferentes indústrias brasileiras.

## Arquitetura

### Componentes Principais

1. **ACF Service** (`app/services/acf_integration.py`)
   - Geração automática de campos ACF por indústria
   - Personalização de campos com dados do negócio
   - Exportação de configurações ACF para WordPress

2. **Template Repository** (`app/services/template_repository.py`)
   - Armazenamento centralizado de templates
   - Cache em memória com TTL
   - Sincronização com WordPress Master

3. **WordPress Sync Service** (`app/services/wordpress_sync_service.py`)
   - Sincronização em tempo real via webhooks
   - Sync programado (padrão: 30 minutos)
   - Queue de eventos com retry automático

4. **APIs REST** (`app/api/routers/templates.py`)
   - CRUD completo de templates
   - Endpoints de sincronização
   - Webhooks do WordPress

## Configuração

### Variáveis de Ambiente

```bash
# WordPress Master
WORDPRESS_MASTER_URL=https://master.kenzysites.com
WP_MASTER_USER=admin
WP_MASTER_PASSWORD=seu_password_seguro

# Webhooks
WP_WEBHOOK_SECRET=sua_chave_secreta_webhook

# Sync Configuration
SYNC_INTERVAL_MINUTES=30
SYNC_MAX_RETRIES=3

# ACF Pro License
ACF_PRO_LICENSE=sua_licenca_acf_pro
```

### WordPress Master Setup

1. **Instalar Plugins Obrigatórios:**
   - Advanced Custom Fields Pro
   - JWT Authentication for WP-API
   - Custom Post Type UI (para templates)

2. **Configurar Custom Post Type:**
   ```php
   // No functions.php do tema ou plugin
   register_post_type('kz_template', [
       'public' => true,
       'show_in_rest' => true,
       'supports' => ['title', 'editor', 'excerpt', 'custom-fields']
   ]);
   ```

3. **Configurar Webhooks:**
   ```php
   // Adicionar ao functions.php
   add_action('save_post', 'notify_kenzysites_webhook');
   
   function notify_kenzysites_webhook($post_id) {
       if (get_post_type($post_id) !== 'kz_template') return;
       
       $webhook_url = 'https://api.kenzysites.com/templates/sync/webhook';
       $data = [
           'event_type' => 'post_updated',
           'post_id' => $post_id,
           'timestamp' => current_time('c')
       ];
       
       wp_remote_post($webhook_url, [
           'body' => json_encode($data),
           'headers' => [
               'Content-Type' => 'application/json',
               'X-Signature' => hash_hmac('sha256', json_encode($data), WP_WEBHOOK_SECRET)
           ]
       ]);
   }
   ```

## Indústrias Brasileiras Suportadas

### Templates Disponíveis

1. **Restaurante e Alimentação**
   - Campos: Tipo de culinária, delivery, reservas
   - Features: WhatsApp, PIX, áreas de entrega

2. **Saúde e Bem-estar**
   - Campos: Especialidade, CRM, planos de saúde
   - Features: Agendamento, LGPD, CPF

3. **E-commerce**
   - Campos: Categoria, formas de pagamento
   - Features: PIX, CNPJ, link da loja

4. **Educação**
   - Campos: Tipo de ensino, cursos, duração
   - Features: Portal do aluno, CPF

5. **Advocacia**
   - Campos: Áreas de atuação, OAB
   - Features: Consulta gratuita, CPF

### Campos ACF Automáticos

Cada indústria recebe automaticamente:

- **Campos Básicos:** Nome, descrição, logo, slogan
- **Contato:** Telefone, email, endereço, WhatsApp
- **Serviços:** Lista de serviços/produtos
- **Brasil:** CNPJ, PIX, LGPD, CPF (quando aplicável)
- **Específicos:** Campos únicos por indústria

## Uso da API

### Listar Templates por Indústria

```bash
GET /api/templates/repository/templates?industry=restaurante&limit=10
```

### Criar Template

```bash
POST /api/templates/repository/templates
{
  "id": "rest_001",
  "name": "Restaurante Italiano Moderno",
  "description": "Template para restaurantes italianos",
  "category": "restaurant",
  "industry": "restaurante",
  "style": "modern",
  "features": ["delivery", "reservas", "cardapio_digital"]
}
```

### Sincronizar com WordPress Master

```bash
POST /api/templates/repository/sync
```

### Obter Campos ACF de uma Indústria

```bash
GET /api/templates/industries/brazilian-enhanced
```

### Webhook do WordPress

```bash
POST /api/templates/sync/webhook
{
  "event_type": "post_updated",
  "post_id": 123,
  "timestamp": "2025-01-20T12:00:00Z"
}
```

## Fluxo de Trabalho

### 1. Criação de Templates no WordPress Master

1. Acesse `/wp-admin/post-new.php?post_type=kz_template`
2. Crie o template com título e conteúdo
3. Configure os campos ACF:
   - `template_category`: Categoria do template
   - `template_industry`: Indústria (usar chaves do BRAZILIAN_INDUSTRIES)
   - `template_style`: Estilo visual
   - `preview_url`: URL de preview
   - `thumbnail_url`: URL da thumbnail
4. Publique o template

### 2. Sincronização Automática

1. Webhook é disparado automaticamente
2. Sistema processa o evento na queue
3. Template é sincronizado para o repositório
4. Campos ACF são gerados automaticamente

### 3. Customização para Cliente

1. Cliente escolhe template via API ou UI
2. Sistema gera campos ACF personalizados
3. IA preenche campos com dados do negócio
4. Template é aplicado ao site WordPress do cliente

## Monitoramento

### Status do Serviço de Sync

```bash
GET /api/templates/sync/status
```

Retorna:
- Status do serviço (running/stopped)
- Tamanho da queue de eventos
- Último sync completo
- Eventos pendentes

### Health Check

```bash
GET /api/templates/sync/health
```

### Estatísticas do Repositório

```bash
GET /api/templates/repository/stats
```

## Troubleshooting

### Sync Não Funciona

1. Verificar variáveis de ambiente
2. Testar conectividade com WordPress Master
3. Verificar logs do serviço de sync
4. Verificar configuração de webhooks

### Templates Não Aparecem

1. Verificar se foram publicados no WordPress Master
2. Forçar sync manual: `POST /api/templates/sync/manual/full`
3. Verificar logs de processamento de eventos

### Campos ACF Não Gerados

1. Verificar se indústria está em BRAZILIAN_INDUSTRIES
2. Verificar logs do ACF Service
3. Regenerar campos: `POST /api/templates/repository/templates/{id}/generate-acf`

## Próximos Passos

1. **Interface de Administração:** Criar UI para gerenciar templates
2. **Preview em Tempo Real:** Sistema de preview dinâmico
3. **Versionamento:** Controle de versões de templates
4. **Analytics:** Métricas de uso e performance de templates
5. **A/B Testing:** Testes de conversão entre templates