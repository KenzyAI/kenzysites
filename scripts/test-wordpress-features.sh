#!/bin/bash

# Script de verificação completa das funcionalidades WordPress do KenzySites
# Este script testa todas as integrações e funcionalidades essenciais

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
WP_URL="http://localhost:8085"
WP_ADMIN_USER="admin"
WP_ADMIN_PASS="admin123"
DB_HOST="127.0.0.1"
DB_PORT="3307"
DB_NAME="wordpress_local"
DB_USER="wp_user"
DB_PASS="wp_pass"

echo "========================================="
echo "  KenzySites - Teste de Funcionalidades"
echo "========================================="
echo ""

# Função para exibir resultados
show_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        return 1
    fi
}

# Função para testar endpoint
test_endpoint() {
    local endpoint=$1
    local expected_code=$2
    local description=$3
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")
    if [ "$response" = "$expected_code" ]; then
        show_result 0 "$description"
    else
        show_result 1 "$description (Código: $response, Esperado: $expected_code)"
    fi
}

echo "1. VERIFICANDO INFRAESTRUTURA"
echo "------------------------------"

# Verificar containers
echo -n "Verificando containers Docker... "
if docker compose ps | grep -q "Up"; then
    show_result 0 "Containers em execução"
else
    show_result 1 "Containers não estão rodando"
    exit 1
fi

# Verificar conectividade WordPress
test_endpoint "$WP_URL" "200" "WordPress acessível"
test_endpoint "$WP_URL/wp-admin/" "302" "WordPress Admin redirecionando"
test_endpoint "$WP_URL/wp-json/wp/v2/posts" "200" "API REST disponível"

echo ""
echo "2. VERIFICANDO BANCO DE DADOS"
echo "------------------------------"

# Testar conexão MySQL
echo -n "Testando conexão MySQL... "
if mysql -h 127.0.0.1 -P $DB_PORT -u$DB_USER -p$DB_PASS -e "SELECT 1" &>/dev/null; then
    show_result 0 "Conexão MySQL funcionando"
else
    show_result 1 "Falha na conexão MySQL"
fi

# Verificar tabelas essenciais
echo -n "Verificando tabelas WordPress... "
table_count=$(mysql -h 127.0.0.1 -P $DB_PORT -u$DB_USER -p$DB_PASS $DB_NAME -e "SHOW TABLES;" 2>/dev/null | wc -l)
if [ $table_count -gt 10 ]; then
    show_result 0 "Tabelas WordPress presentes ($table_count tabelas)"
else
    show_result 1 "Tabelas WordPress incompletas"
fi

echo ""
echo "3. VERIFICANDO PLUGINS ESSENCIAIS"
echo "----------------------------------"

# Verificar plugins via WP-CLI no container
echo -n "Verificando Advanced Custom Fields (ACF)... "
if docker exec kenzysites-wordpress wp plugin is-installed advanced-custom-fields --allow-root 2>/dev/null; then
    if docker exec kenzysites-wordpress wp plugin is-active advanced-custom-fields --allow-root 2>/dev/null; then
        show_result 0 "ACF instalado e ativo"
    else
        show_result 1 "ACF instalado mas inativo"
    fi
else
    show_result 1 "ACF não instalado"
fi

echo -n "Verificando Elementor... "
if docker exec kenzysites-wordpress wp plugin is-installed elementor --allow-root 2>/dev/null; then
    if docker exec kenzysites-wordpress wp plugin is-active elementor --allow-root 2>/dev/null; then
        show_result 0 "Elementor instalado e ativo"
    else
        show_result 1 "Elementor instalado mas inativo"
    fi
else
    show_result 1 "Elementor não instalado"
fi

echo -n "Verificando KenzySites Converter... "
if docker exec kenzysites-wordpress wp plugin is-installed kenzysites-converter --allow-root 2>/dev/null; then
    if docker exec kenzysites-wordpress wp plugin is-active kenzysites-converter --allow-root 2>/dev/null; then
        show_result 0 "KenzySites Converter instalado e ativo"
    else
        show_result 1 "KenzySites Converter instalado mas inativo"
    fi
else
    show_result 1 "KenzySites Converter não instalado"
fi

echo ""
echo "4. VERIFICANDO CUSTOM POST TYPES"
echo "---------------------------------"

# Verificar CPT Sites
echo -n "Verificando Custom Post Type 'Sites'... "
response=$(curl -s "$WP_URL/wp-json/wp/v2/types/kenzysites_site" 2>/dev/null)
if echo "$response" | grep -q "kenzysites_site"; then
    show_result 0 "CPT Sites registrado"
else
    show_result 1 "CPT Sites não encontrado"
fi

echo ""
echo "5. VERIFICANDO CAMPOS ACF"
echo "--------------------------"

# Verificar grupos de campos ACF
echo -n "Verificando grupos de campos ACF... "
field_groups=$(mysql -h 127.0.0.1 -P $DB_PORT -u$DB_USER -p$DB_PASS $DB_NAME \
    -e "SELECT COUNT(*) FROM wp_posts WHERE post_type='acf-field-group' AND post_status='publish';" 2>/dev/null | tail -1)
if [ "$field_groups" -gt 0 ]; then
    show_result 0 "Grupos de campos ACF encontrados ($field_groups grupos)"
else
    show_result 1 "Nenhum grupo de campos ACF encontrado"
fi

echo ""
echo "6. VERIFICANDO SISTEMA DE TEMPLATES"
echo "------------------------------------"

# Verificar templates salvos
echo -n "Verificando templates salvos... "
templates=$(mysql -h 127.0.0.1 -P $DB_PORT -u$DB_USER -p$DB_PASS $DB_NAME \
    -e "SELECT COUNT(*) FROM wp_posts WHERE post_type='elementor_library' AND post_status='publish';" 2>/dev/null | tail -1)
if [ "$templates" -gt 0 ]; then
    show_result 0 "Templates Elementor encontrados ($templates templates)"
else
    echo -e "${YELLOW}⚠${NC} Nenhum template Elementor encontrado (normal em instalação nova)"
fi

echo ""
echo "7. VERIFICANDO INTEGRAÇÃO COM BACKEND"
echo "--------------------------------------"

# Testar conexão com backend Python
test_endpoint "http://localhost:8000/health" "200" "Backend Python respondendo"
test_endpoint "http://localhost:8000/docs" "200" "Documentação API disponível"

# Testar endpoint de sites
echo -n "Testando endpoint de sites... "
response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000/api/v1/sites" \
    -H "Content-Type: application/json")
if [ "$response" = "200" ] || [ "$response" = "401" ]; then
    show_result 0 "Endpoint de sites funcionando"
else
    show_result 1 "Endpoint de sites com problema (Código: $response)"
fi

echo ""
echo "8. VERIFICANDO SISTEMA DE ARQUIVOS"
echo "-----------------------------------"

# Verificar permissões de uploads
echo -n "Verificando diretório de uploads... "
if docker exec kenzysites-wordpress test -w /var/www/html/wp-content/uploads 2>/dev/null; then
    show_result 0 "Diretório uploads com permissão de escrita"
else
    show_result 1 "Problema de permissão no diretório uploads"
fi

# Verificar diretório de plugins
echo -n "Verificando diretório de plugins... "
if docker exec kenzysites-wordpress test -d /var/www/html/wp-content/plugins/kenzysites-converter 2>/dev/null; then
    show_result 0 "Plugin KenzySites presente no diretório correto"
else
    show_result 1 "Plugin KenzySites não encontrado"
fi

echo ""
echo "9. TESTANDO FUNCIONALIDADES CRÍTICAS"
echo "-------------------------------------"

# Testar criação de usuário
echo -n "Testando criação de usuário... "
test_user="test_$(date +%s)"
if docker exec kenzysites-wordpress wp user create $test_user "$test_user@test.com" \
    --role=subscriber --allow-root &>/dev/null; then
    show_result 0 "Criação de usuário funcionando"
    docker exec kenzysites-wordpress wp user delete $test_user --yes --allow-root &>/dev/null
else
    show_result 1 "Falha na criação de usuário"
fi

# Testar criação de post
echo -n "Testando criação de conteúdo... "
post_id=$(docker exec kenzysites-wordpress wp post create \
    --post_title="Teste $(date +%s)" \
    --post_status=draft \
    --porcelain \
    --allow-root 2>/dev/null)
if [ -n "$post_id" ]; then
    show_result 0 "Criação de posts funcionando"
    docker exec kenzysites-wordpress wp post delete $post_id --force --allow-root &>/dev/null
else
    show_result 1 "Falha na criação de posts"
fi

echo ""
echo "10. VERIFICANDO CONFIGURAÇÕES DE SEGURANÇA"
echo "-------------------------------------------"

# Verificar debug mode
echo -n "Verificando modo debug... "
debug_mode=$(docker exec kenzysites-wordpress wp config get WP_DEBUG --allow-root 2>/dev/null || echo "false")
if [ "$debug_mode" = "false" ] || [ "$debug_mode" = "0" ]; then
    show_result 0 "Debug mode desativado (produção)"
else
    echo -e "${YELLOW}⚠${NC} Debug mode ativo (desenvolvimento)"
fi

# Verificar HTTPS
echo -n "Verificando configuração SSL... "
if [ "$WP_URL" = "https://"* ]; then
    show_result 0 "SSL configurado"
else
    echo -e "${YELLOW}⚠${NC} SSL não configurado (desenvolvimento)"
fi

echo ""
echo "========================================="
echo "           RESUMO DOS TESTES"
echo "========================================="
echo ""

# Contar resultados
total_tests=25
passed_tests=$(grep -c "✓" /tmp/test_results 2>/dev/null || echo "0")
failed_tests=$(grep -c "✗" /tmp/test_results 2>/dev/null || echo "0")

echo -e "Testes executados: $total_tests"
echo -e "${GREEN}Passou:${NC} $passed_tests"
echo -e "${RED}Falhou:${NC} $failed_tests"
echo -e "${YELLOW}Avisos:${NC} $(grep -c "⚠" /tmp/test_results 2>/dev/null || echo "0")"

echo ""
echo "========================================="
echo "         PRÓXIMOS PASSOS"
echo "========================================="
echo ""
echo "1. Instalar plugins faltantes:"
echo "   - Advanced Custom Fields (ACF)"
echo "   - Elementor"
echo "   - Ativar KenzySites Converter"
echo ""
echo "2. Configurar Custom Post Types"
echo "3. Importar campos ACF do template"
echo "4. Testar fluxo completo de criação de site"
echo ""
echo "Para detalhes, consulte: MIGRATION_GUIDE.md"