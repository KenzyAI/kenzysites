#!/bin/bash

# Script para criar um novo site no WordPress Multisite
# Uso: ./create-site.sh <slug> <title> <admin_email>

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar parâmetros
if [ "$#" -lt 3 ]; then
    echo -e "${RED}❌ Uso: $0 <slug> <title> <admin_email>${NC}"
    echo -e "${YELLOW}Exemplo: $0 restaurante 'Restaurante do João' joao@email.com${NC}"
    exit 1
fi

SITE_SLUG=$1
SITE_TITLE=$2
SITE_EMAIL=$3

# Função para executar comandos WP-CLI
wp_cli() {
    docker-compose exec -T wp-cli wp "$@"
}

echo -e "${YELLOW}🚀 Criando novo site: $SITE_TITLE${NC}"

# Criar o site
SITE_ID=$(wp_cli site create \
    --slug="$SITE_SLUG" \
    --title="$SITE_TITLE" \
    --email="$SITE_EMAIL" \
    --porcelain)

if [ -z "$SITE_ID" ]; then
    echo -e "${RED}❌ Erro ao criar o site${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Site criado com sucesso! ID: $SITE_ID${NC}"

# Configurar o novo site
echo -e "${YELLOW}⚙️ Configurando o site...${NC}"

# Mudar para o contexto do novo site
wp_cli --url="http://localhost:8080/$SITE_SLUG" option update timezone_string 'America/Sao_Paulo'
wp_cli --url="http://localhost:8080/$SITE_SLUG" option update date_format 'd/m/Y'
wp_cli --url="http://localhost:8080/$SITE_SLUG" option update time_format 'H:i'

# Configurar permalinks
wp_cli --url="http://localhost:8080/$SITE_SLUG" rewrite structure '/%postname%/'
wp_cli --url="http://localhost:8080/$SITE_SLUG" rewrite flush

# Remover conteúdo padrão
wp_cli --url="http://localhost:8080/$SITE_SLUG" post delete 1 --force 2>/dev/null

# Criar página inicial
HOME_PAGE_ID=$(wp_cli --url="http://localhost:8080/$SITE_SLUG" post create \
    --post_type=page \
    --post_title='Início' \
    --post_status=publish \
    --post_content='Bem-vindo ao seu novo site!' \
    --porcelain)

# Definir como página inicial
wp_cli --url="http://localhost:8080/$SITE_SLUG" option update show_on_front 'page'
wp_cli --url="http://localhost:8080/$SITE_SLUG" option update page_on_front "$HOME_PAGE_ID"

echo -e "${GREEN}✅ Site configurado!${NC}"

# Criar usuário admin para o site
SITE_PASSWORD=$(openssl rand -base64 12)
wp_cli --url="http://localhost:8080/$SITE_SLUG" user create \
    "admin_$SITE_SLUG" \
    "$SITE_EMAIL" \
    --role=administrator \
    --user_pass="$SITE_PASSWORD" \
    2>/dev/null || true

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Site criado com sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Informações do Site:${NC}"
echo -e "ID: ${GREEN}$SITE_ID${NC}"
echo -e "URL: ${GREEN}http://localhost:8080/$SITE_SLUG${NC}"
echo -e "Admin: ${GREEN}http://localhost:8080/$SITE_SLUG/wp-admin${NC}"
echo ""
echo -e "${YELLOW}🔑 Credenciais:${NC}"
echo -e "Usuário: ${GREEN}admin_$SITE_SLUG${NC}"
echo -e "Senha: ${GREEN}$SITE_PASSWORD${NC}"
echo -e "Email: ${GREEN}$SITE_EMAIL${NC}"
echo ""

# Retornar JSON para integração com Python
echo "JSON_OUTPUT:"
echo "{\"site_id\": $SITE_ID, \"url\": \"http://localhost:8080/$SITE_SLUG\", \"admin_url\": \"http://localhost:8080/$SITE_SLUG/wp-admin\", \"username\": \"admin_$SITE_SLUG\", \"password\": \"$SITE_PASSWORD\"}"