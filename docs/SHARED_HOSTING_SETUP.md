# Setup WordPress Multisite em Hospedagem Compartilhada

## ✅ **Resumo: Sistema Agora Suporta Ambos os Modos!**

Seu sistema KenzySites agora pode funcionar em:

1. **🏢 Hospedagem Compartilhada** (sua hospedagem atual)
2. **☸️ Kubernetes** (Hetzner ou outros)

## 🎯 **Pré-requisitos para Hospedagem Compartilhada**

### **Essencial:**
- ✅ **Subdomínios ilimitados** (ou vários subdomínios)
- ✅ **WordPress** instalado/instalável
- ✅ **PHP 7.4+** e MySQL 5.7+
- ✅ **Acesso ao painel** (cPanel/Plesk)

### **Recomendado:**
- ✅ **SSH/Terminal** (para WP-CLI)
- ✅ **WP-CLI instalado** 
- ✅ **ACF Pro** (ou usar versão Free)
- ✅ **Backup automático**

### **Opcional:**
- ⚪ **API do painel** (para automação)
- ⚪ **SSL automático** (Let's Encrypt)

## 🛠️ **Setup Passo a Passo**

### **Passo 1: Preparar Hospedagem**

#### **1.1. Verificar Recursos:**
```bash
# Via SSH (se disponível)
php -v                    # Versão PHP
mysql --version          # Versão MySQL
wp --version             # WP-CLI disponível?
```

#### **1.2. Instalar WordPress Multisite:**
```bash
# 1. Baixar WordPress
cd /public_html/
mkdir multisite
cd multisite
wp core download --locale=pt_BR

# 2. Criar wp-config.php
wp config create \
  --dbname=seu_banco \
  --dbuser=seu_usuario \
  --dbpass=sua_senha \
  --dbhost=localhost

# 3. Instalar WordPress
wp core install \
  --url=https://seudominio.com/multisite \
  --title="KenzySites Network" \
  --admin_user=admin \
  --admin_password=senha_forte \
  --admin_email=admin@seudominio.com

# 4. Habilitar Multisite
wp core multisite-convert --subdomains
```

#### **1.3. Configurar wp-config.php:**
```php
// Adicionar no wp-config.php
define('WP_ALLOW_MULTISITE', true);
define('MULTISITE', true);
define('SUBDOMAIN_INSTALL', true);
define('DOMAIN_CURRENT_SITE', 'seudominio.com');
define('PATH_CURRENT_SITE', '/multisite/');
define('SITE_ID_CURRENT_SITE', 1);
define('BLOG_ID_CURRENT_SITE', 1);
```

#### **1.4. Configurar .htaccess:**
```apache
# WordPress Multisite .htaccess
RewriteEngine On
RewriteBase /multisite/
RewriteRule ^index\.php$ - [L]

# add a trailing slash to /wp-admin
RewriteRule ^wp-admin$ wp-admin/ [R=301,L]

RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]
RewriteRule ^(wp-(content|admin|includes).*) $1 [L]
RewriteRule ^(.*\.php)$ $1 [L]
RewriteRule . index.php [L]
```

### **Passo 2: Configurar Sistema KenzySites**

#### **2.1. Variáveis de Ambiente:**
```bash
# .env
PROVISIONING_MODE=shared_hosting

# Hosting Configuration
HOSTING_TYPE=cpanel
HOSTING_URL=https://seudominio.com:2083
HOSTING_USER=seu_cpanel_user
HOSTING_PASSWORD=sua_senha

# Multisite Configuration
MULTISITE_DOMAIN=seudominio.com
MULTISITE_PATH=/public_html/multisite/
WP_CLI_PATH=/usr/local/bin/wp

# SSH (se disponível)
SSH_HOST=seudominio.com
SSH_USER=seu_usuario
SSH_KEY_PATH=/path/to/ssh/key
```

#### **2.2. Instalar Plugins Essenciais:**
```bash
# Na rede WordPress
wp plugin install advanced-custom-fields-pro --activate-network
wp plugin install wordpress-seo --activate-network
wp plugin install wordfence --activate-network
```

### **Passo 3: Testar o Sistema**

#### **3.1. Verificar APIs:**
```bash
# Testar modos de provisioning
curl http://localhost:8000/api/templates/provision/modes

# Provisionar site de teste
curl -X POST http://localhost:8000/api/templates/provision/shared-hosting \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Pizzaria Teste",
    "industry": "restaurante",
    "plan": "basic"
  }'
```

#### **3.2. Verificar Site Criado:**
```bash
# Listar sites na rede
wp site list

# Ver status de um site
wp site list --site_id=2
```

## 🔧 **Troubleshooting**

### **❌ Subdomínio não funciona:**
```bash
# Verificar DNS
nslookup teste.seudominio.com

# Criar subdomínio manual no cPanel
# Painel cPanel > Subdomains > Create
```

### **❌ WP-CLI não encontrado:**
```bash
# Instalar WP-CLI
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

# Ou usar caminho local
WP_CLI_PATH=/home/usuario/wp-cli.phar
```

### **❌ Plugins não ativam:**
```bash
# Verificar permissões
wp plugin list --status=active

# Ativar manualmente
wp plugin activate advanced-custom-fields-pro --url=site-id
```

### **❌ SSL não funciona:**
```bash
# Forçar HTTPS no WordPress
wp option update home 'https://cliente.seudominio.com' --url=2
wp option update siteurl 'https://cliente.seudominio.com' --url=2
```

## 📊 **Comparação de Custos (Exemplo Real)**

### **Hospedagem Compartilhada:**
```
💰 Custo Mensal:
├── Hospedagem atual: R$ 50-200/mês
├── Domínio: R$ 40/ano
├── ACF Pro: R$ 200/ano (opcional)
└── SSL: Incluído (Let's Encrypt)

TOTAL: R$ 50-200/mês para até 50+ sites
Custo por site: R$ 1-4/mês
```

### **vs Kubernetes (Hetzner):**
```
💰 Custo Mensal:
├── 2 servidores: R$ 270/mês
├── Storage: R$ 30/mês
├── Load Balancer: R$ 30/mês
└── Backup: R$ 25/mês

TOTAL: R$ 355/mês para até 15 sites
Custo por site: R$ 24/mês
```

## 🎯 **Recomendações por Caso**

### **🏠 Use Hospedagem Compartilhada se:**
- ✅ **Começando o negócio** (baixo investimento)
- ✅ **Clientes pequenos** (< 1.000 visitas/mês)
- ✅ **Budget limitado** (< R$ 500/mês infra)
- ✅ **Prototipando/testando** mercado

### **☸️ Migre para Kubernetes quando:**
- ✅ **10+ clientes ativos**
- ✅ **Sites com tráfego** (> 5.000 visitas/mês)
- ✅ **SLA exigido** (99.9% uptime)
- ✅ **Diferenciação necessária** vs concorrentes

## 🚀 **Roadmap de Crescimento**

### **Fase 1: MVP (Hospedagem Compartilhada)**
```
👥 0-10 clientes
💰 Investimento: R$ 100/mês
⏱️ Setup: 1-2 dias
📈 Foco: Validar mercado
```

### **Fase 2: Crescimento (Híbrido)**
```
👥 10-30 clientes
💰 Investimento: R$ 400/mês
⏱️ Migration: 1 semana
📈 Foco: Qualidade + escala
```

### **Fase 3: Escala (Full Kubernetes)**
```
👥 30+ clientes
💰 Investimento: R$ 800/mês
⏱️ Full migration: 2 semanas
📈 Foco: Diferenciação + SLA
```

## 📋 **Próximos Passos**

1. **⚡ Teste agora:** Configure .env para sua hospedagem
2. **🔧 Setup Multisite:** Siga o passo a passo acima  
3. **🧪 Provisione teste:** Use a API para criar um site
4. **📈 Valide mercado:** Lance MVP com hospedagem atual
5. **🚀 Escale depois:** Migre para Kubernetes quando justificar

**Seu sistema agora é flexível e pode começar com ZERO investimento adicional em infraestrutura!** ✨