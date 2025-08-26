#!/bin/bash

# Script para iniciar o sistema completo KenzySites
# WordPress Multisite + Frontend Next.js + Backend Python

echo "🚀 KenzySites - Iniciando Sistema Completo"
echo "=========================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Iniciar WordPress Multisite
echo -e "${YELLOW}📦 Iniciando WordPress Multisite...${NC}"
cd wordpress
docker-compose up -d

# Aguardar containers subirem
echo -e "${YELLOW}⏳ Aguardando containers...${NC}"
sleep 10

# Configurar WordPress (se primeira vez)
if [ ! -f ".wordpress-configured" ]; then
    echo -e "${YELLOW}🔧 Configurando WordPress Multisite (primeira execução)...${NC}"
    docker-compose exec wordpress bash /scripts/setup-multisite.sh
    docker-compose exec wordpress bash /scripts/install-themes-plugins.sh
    touch .wordpress-configured
    echo -e "${GREEN}✅ WordPress configurado!${NC}"
else
    echo -e "${GREEN}✅ WordPress já configurado!${NC}"
fi

cd ..

# URLs do sistema
echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Sistema KenzySites Pronto!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📋 URLs de Acesso:${NC}"
echo -e "Frontend Next.js:     ${GREEN}http://localhost:3000${NC}"
echo -e "Gerador de Sites:     ${GREEN}http://localhost:3000/generator${NC}"
echo -e "WordPress Admin:      ${GREEN}http://localhost:8080/wp-admin${NC}"
echo -e "phpMyAdmin:          ${GREEN}http://localhost:8081${NC}"
echo ""
echo -e "${BLUE}🔑 Credenciais WordPress:${NC}"
echo -e "Usuário: ${GREEN}admin${NC}"
echo -e "Senha:   ${GREEN}Admin@2024!${NC}"
echo ""
echo -e "${YELLOW}💡 Comandos úteis:${NC}"
echo -e "Criar novo site:      ${GREEN}cd wordpress && ./scripts/create-site.sh <slug> <titulo> <email>${NC}"
echo -e "Ver logs:            ${GREEN}cd wordpress && docker-compose logs -f${NC}"
echo -e "Parar sistema:       ${GREEN}cd wordpress && docker-compose down${NC}"
echo ""
echo -e "${YELLOW}📚 Próximos passos:${NC}"
echo -e "1. Acesse ${GREEN}http://localhost:3000/generator${NC}"
echo -e "2. Preencha as informações do negócio"
echo -e "3. Clique em 'Gerar Site com IA'"
echo -e "4. Escolha uma das 3 variações"
echo -e "5. Site WordPress pronto em 60 segundos!"
echo ""