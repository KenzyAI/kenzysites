#!/bin/bash

# Script para configurar WordPress Multisite automaticamente
# KenzySites - WordPress AI Generator

echo "🚀 KenzySites - Configurando WordPress Multisite..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurações
WP_URL="http://localhost:8080"
WP_TITLE="KenzySites Platform"
WP_ADMIN_USER="admin"
WP_ADMIN_PASSWORD="Admin@2024!"
WP_ADMIN_EMAIL="admin@kenzysites.local"

# Função para executar comandos WP-CLI
wp_cli() {
    docker-compose exec -T wp-cli wp "$@"
}

# Aguardar MySQL estar pronto
echo -e "${YELLOW}⏳ Aguardando banco de dados...${NC}"
until docker-compose exec -T db mysql -u root -proot_password -e "SELECT 1" &> /dev/null; do
    sleep 2
done
echo -e "${GREEN}✅ Banco de dados pronto!${NC}"

# Aguardar WordPress estar acessível
echo -e "${YELLOW}⏳ Aguardando WordPress...${NC}"
until $(curl --output /dev/null --silent --head --fail $WP_URL); do
    sleep 2
done
echo -e "${GREEN}✅ WordPress acessível!${NC}"

# Instalar WordPress se não estiver instalado
echo -e "${YELLOW}📦 Instalando WordPress...${NC}"
if ! wp_cli core is-installed 2>/dev/null; then
    wp_cli core install \
        --url="$WP_URL" \
        --title="$WP_TITLE" \
        --admin_user="$WP_ADMIN_USER" \
        --admin_password="$WP_ADMIN_PASSWORD" \
        --admin_email="$WP_ADMIN_EMAIL" \
        --skip-email
    echo -e "${GREEN}✅ WordPress instalado!${NC}"
else
    echo -e "${GREEN}✅ WordPress já está instalado!${NC}"
fi

# Configurar Multisite
echo -e "${YELLOW}🔧 Configurando Multisite...${NC}"
wp_cli core multisite-convert --base="/"
echo -e "${GREEN}✅ Multisite configurado!${NC}"

# Configurações básicas
echo -e "${YELLOW}⚙️ Aplicando configurações básicas...${NC}"

# Timezone e idioma
wp_cli option update timezone_string 'America/Sao_Paulo'
wp_cli option update date_format 'd/m/Y'
wp_cli option update time_format 'H:i'

# Permalinks
wp_cli rewrite structure '/%postname%/'
wp_cli rewrite flush

# Desabilitar comentários por padrão
wp_cli option update default_comment_status 'closed'
wp_cli option update default_ping_status 'closed'

# Remover conteúdo padrão
wp_cli post delete 1 --force 2>/dev/null
wp_cli post delete 2 --force 2>/dev/null
wp_cli post delete 3 --force 2>/dev/null

echo -e "${GREEN}✅ Configurações aplicadas!${NC}"

# Instalar plugins essenciais
echo -e "${YELLOW}🔌 Instalando plugins essenciais...${NC}"

# Plugins gratuitos essenciais
PLUGINS=(
    "wordpress-seo"           # Yoast SEO
    "redis-cache"            # Cache com Redis
    "disable-comments"       # Desabilitar comentários
    "duplicate-post"         # Duplicar posts/páginas
    "custom-post-type-ui"    # Custom Post Types
    "advanced-custom-fields" # ACF (versão gratuita)
    "contact-form-7"        # Formulários
    "wp-mail-smtp"          # SMTP
    "updraftplus"           # Backup
)

for plugin in "${PLUGINS[@]}"; do
    echo -e "${YELLOW}  Installing $plugin...${NC}"
    wp_cli plugin install "$plugin" --activate-network 2>/dev/null || true
done

# Configurar Redis Cache
if wp_cli plugin is-installed redis-cache; then
    wp_cli redis enable 2>/dev/null || true
    echo -e "${GREEN}✅ Redis Cache habilitado!${NC}"
fi

echo -e "${GREEN}✅ Plugins instalados!${NC}"

# Criar Application Password para API
echo -e "${YELLOW}🔑 Criando credenciais de API...${NC}"
APP_PASSWORD=$(wp_cli user application-password create $WP_ADMIN_USER "KenzySites API" --porcelain)
echo -e "${GREEN}✅ Application Password criado!${NC}"

# Criar primeiro site de exemplo
echo -e "${YELLOW}🌐 Criando site de exemplo...${NC}"
SITE_ID=$(wp_cli site create --slug=exemplo --title="Site Exemplo" --email="exemplo@kenzysites.local" --porcelain)
echo -e "${GREEN}✅ Site de exemplo criado! ID: $SITE_ID${NC}"

# Salvar credenciais
echo -e "\n${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ WordPress Multisite configurado com sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Credenciais de Acesso:${NC}"
echo -e "URL Admin: ${GREEN}$WP_URL/wp-admin${NC}"
echo -e "Usuário: ${GREEN}$WP_ADMIN_USER${NC}"
echo -e "Senha: ${GREEN}$WP_ADMIN_PASSWORD${NC}"
echo ""
echo -e "${YELLOW}🔑 API Credentials:${NC}"
echo -e "Username: ${GREEN}$WP_ADMIN_USER${NC}"
echo -e "App Password: ${GREEN}$APP_PASSWORD${NC}"
echo ""
echo -e "${YELLOW}🌐 Sites:${NC}"
echo -e "Principal: ${GREEN}$WP_URL${NC}"
echo -e "Exemplo: ${GREEN}$WP_URL/exemplo${NC}"
echo ""

# Salvar credenciais em arquivo
cat > ../wordpress-credentials.txt << EOF
WordPress Multisite Credentials
================================
Admin URL: $WP_URL/wp-admin
Username: $WP_ADMIN_USER
Password: $WP_ADMIN_PASSWORD

API Access:
Username: $WP_ADMIN_USER
App Password: $APP_PASSWORD

Sites:
Main: $WP_URL
Example: $WP_URL/exemplo
EOF

echo -e "${GREEN}Credenciais salvas em: wordpress-credentials.txt${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"