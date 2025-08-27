# KenzySites AI Builder - WordPress Plugin

Plugin para integração do AI Builder do KenzySites com WordPress e Elementor.

## Instalação

### 1. Upload do Plugin
1. Baixe o arquivo `kenzysites-ai-builder.php`
2. Acesse seu WordPress Admin: `https://aikenzy.com.br/wp-admin`
3. Vá em **Plugins > Adicionar Novo > Fazer upload do plugin**
4. Envie o arquivo e **ative o plugin**

### 2. Instalar Elementor (Obrigatório)
1. Em **Plugins > Adicionar Novo**
2. Procure por **"Elementor"**
3. **Instale e ative** o Elementor Website Builder
4. Configure as opções básicas do Elementor

## Funcionalidades

### API Endpoints

O plugin cria os seguintes endpoints REST API:

#### 1. Status do Elementor
```
GET /wp-json/kenzysites/v1/elementor/status
```

Retorna informações sobre o status do Elementor:
```json
{
  "elementor_active": true,
  "elementor_version": "3.x.x",
  "elementor_pro_active": false,
  "wordpress_version": "6.x",
  "php_version": "8.x",
  "can_import": true
}
```

#### 2. Importar Template Elementor
```
POST /wp-json/kenzysites/v1/elementor/import
```

Payload:
```json
{
  "title": "Nome da Página",
  "content": [/* Dados do template Elementor */],
  "type": "page",
  "status": "publish"
}
```

Resposta:
```json
{
  "success": true,
  "page_id": 123,
  "page_url": "https://aikenzy.com.br/pagina",
  "edit_url": "https://aikenzy.com.br/wp-admin/post.php?post=123&action=elementor",
  "message": "Template imported successfully"
}
```

#### 3. Criar Site (Multisite)
```
POST /wp-json/kenzysites/v1/site/create
```

Payload:
```json
{
  "domain": "cliente.aikenzy.com.br",
  "title": "Site do Cliente",
  "path": "/"
}
```

## Autenticação

Use **Application Passwords** para autenticação:

```javascript
// Headers necessários
{
  "Authorization": "Basic " + base64(username + ":" + applicationPassword),
  "Content-Type": "application/json"
}
```

## Teste Manual

### 1. Testar Status
```bash
curl -H "Authorization: Basic <sua-credencial>" \
     https://aikenzy.com.br/wp-json/kenzysites/v1/elementor/status
```

### 2. Testar Importação
```bash
curl -X POST \
     -H "Authorization: Basic <sua-credencial>" \
     -H "Content-Type: application/json" \
     -d '{"title":"Teste AI","content":[]}' \
     https://aikenzy.com.br/wp-json/kenzysites/v1/elementor/import
```

## Troubleshooting

### Erro: "Elementor plugin is not active"
- Verifique se o Elementor está instalado e ativo
- Vá em Plugins e confirme que Elementor está ativo

### Erro: "You do not have permission"
- Confirme que o usuário tem permissões de `edit_posts`
- Use Application Password válida

### Erro: "No route was found"
- Confirme que o plugin está ativo
- Teste o endpoint de status primeiro

## Integração com KenzySites

O plugin será usado automaticamente pelo AI Builder do KenzySites quando:

1. WordPress hospedado estiver configurado
2. Plugin estiver ativo
3. Elementor estiver instalado
4. Credenciais válidas forem fornecidas

## Suporte

Para suporte, verifique:
1. Se todos os plugins necessários estão ativos
2. Se as credenciais estão corretas
3. Se os endpoints respondem corretamente