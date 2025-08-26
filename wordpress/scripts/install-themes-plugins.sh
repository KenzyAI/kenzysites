#!/bin/bash

# Script para instalar temas e plugins para geração de sites
# KenzySites - WordPress AI Generator

echo "🎨 KenzySites - Instalando Temas e Plugins..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para executar comandos WP-CLI
wp_cli() {
    docker-compose exec -T wp-cli wp "$@"
}

# Instalar Temas
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🎨 Instalando Temas...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"

# Temas principais para geração de sites
THEMES=(
    "astra"              # Tema base principal - leve e rápido
    "kadence"           # Alternativa ao Astra
    "generatepress"     # Tema minimalista
    "neve"             # Tema versátil
    "blocksy"          # Tema moderno com blocos
)

for theme in "${THEMES[@]}"; do
    echo -e "${YELLOW}📦 Instalando tema $theme...${NC}"
    wp_cli theme install "$theme" --activate-network 2>/dev/null || {
        echo -e "${RED}  ⚠️  Erro ao instalar $theme${NC}"
    }
done

# Ativar Astra como tema padrão
wp_cli theme enable astra --network
wp_cli theme enable astra --activate

echo -e "${GREEN}✅ Temas instalados!${NC}"

# Instalar Plugins
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🔌 Instalando Plugins Essenciais...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"

# Plugins de Page Building e Blocks
echo -e "${YELLOW}📐 Page Builders e Blocks...${NC}"
PAGE_BUILDERS=(
    "ultimate-addons-for-gutenberg"  # Spectra - Blocos avançados
    "generateblocks"                  # GenerateBlocks - Alternativa
    "kadence-blocks"                  # Kadence Blocks
    "stackable-ultimate-gutenberg-blocks" # Stackable
    "otter-blocks"                    # Otter Blocks
    "gutentor"                        # Gutentor - Template Library
)

for plugin in "${PAGE_BUILDERS[@]}"; do
    echo -e "${YELLOW}  Installing $plugin...${NC}"
    wp_cli plugin install "$plugin" --activate-network 2>/dev/null || true
done

# Starter Templates e Pattern Libraries
echo -e "${YELLOW}📚 Template Libraries...${NC}"
TEMPLATE_PLUGINS=(
    "astra-sites"                  # Biblioteca de templates Astra
    "starter-templates"            # Starter Templates
    "kubio"                       # Kubio Page Builder com AI
    "extendify"                   # Extendify - Pattern library
)

for plugin in "${TEMPLATE_PLUGINS[@]}"; do
    echo -e "${YELLOW}  Installing $plugin...${NC}"
    wp_cli plugin install "$plugin" --activate-network 2>/dev/null || true
done

# Plugins de Otimização e Performance
echo -e "${YELLOW}⚡ Performance e Otimização...${NC}"
PERFORMANCE_PLUGINS=(
    "autoptimize"                 # Otimização de CSS/JS
    "wp-fastest-cache"           # Cache
    "imagify"                    # Otimização de imagens
    "lazy-load-by-wp-rocket"     # Lazy load
)

for plugin in "${PERFORMANCE_PLUGINS[@]}"; do
    echo -e "${YELLOW}  Installing $plugin...${NC}"
    wp_cli plugin install "$plugin" --activate-network 2>/dev/null || true
done

# Plugins de SEO e Marketing
echo -e "${YELLOW}📈 SEO e Marketing...${NC}"
SEO_PLUGINS=(
    "wordpress-seo"              # Yoast SEO
    "all-in-one-seo-pack"       # Alternative SEO
    "schema"                     # Schema markup
    "google-site-kit"           # Google integration
)

for plugin in "${SEO_PLUGINS[@]}"; do
    echo -e "${YELLOW}  Installing $plugin...${NC}"
    wp_cli plugin install "$plugin" 2>/dev/null || true
done

# Plugins de Conteúdo e AI
echo -e "${YELLOW}🤖 AI e Geração de Conteúdo...${NC}"
AI_PLUGINS=(
    "ai-engine"                  # AI Engine - ChatGPT integration
    "gpt-ai-power"              # AI Power - Content generator
)

for plugin in "${AI_PLUGINS[@]}"; do
    echo -e "${YELLOW}  Installing $plugin...${NC}"
    wp_cli plugin install "$plugin" 2>/dev/null || true
done

# Configurar Astra Settings
echo -e "${YELLOW}⚙️ Configurando tema Astra...${NC}"

# Configurações globais do Astra
wp_cli option update astra-settings '{
    "container-layout": "content-boxed",
    "site-content-width": 1200,
    "header-main-layout-width": "content",
    "footer-layout-width": "content",
    "blog-post-structure": ["image","title-meta"],
    "blog-meta": ["author","date","category"],
    "single-post-structure": ["single-image","single-title-meta"],
    "font-family-body": "Inter, sans-serif",
    "font-family-heading": "Inter, sans-serif",
    "font-weight-body": 400,
    "font-weight-heading": 700,
    "responsive-header-breakpoint": 921
}' --format=json

echo -e "${GREEN}✅ Astra configurado!${NC}"

# Configurar Spectra (Ultimate Addons for Gutenberg)
echo -e "${YELLOW}⚙️ Configurando Spectra Blocks...${NC}"

# Habilitar todos os blocos do Spectra
wp_cli option update uagb_blocks_activation '{
    "advanced-heading": "yes",
    "info-box": "yes",
    "buttons": "yes",
    "testimonial": "yes",
    "team": "yes",
    "social-share": "yes",
    "google-map": "yes",
    "icon-list": "yes",
    "price-list": "yes",
    "contact-form": "yes",
    "marketing-button": "yes",
    "call-to-action": "yes",
    "section": "yes",
    "columns": "yes",
    "post-carousel": "yes",
    "post-masonry": "yes",
    "post-grid": "yes",
    "faq": "yes",
    "inline-notice": "yes",
    "how-to": "yes",
    "review": "yes"
}' --format=json

echo -e "${GREEN}✅ Spectra configurado!${NC}"

# Criar página de demonstração com blocos
echo -e "${YELLOW}📄 Criando página de demonstração...${NC}"

DEMO_CONTENT='<!-- wp:uagb/section {"block_id":"demo-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"demo-heading"} -->
<h2 class="wp-block-uagb-advanced-heading">Site Gerado com KenzySites AI</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/info-box {"block_id":"demo-info"} -->
<div class="wp-block-uagb-info-box">
<p>Este site foi gerado automaticamente usando inteligência artificial.</p>
</div>
<!-- /wp:uagb/info-box -->

<!-- wp:uagb/buttons {"block_id":"demo-buttons"} -->
<div class="wp-block-uagb-buttons">
<a href="#" class="wp-block-button__link">Saiba Mais</a>
</div>
<!-- /wp:uagb/buttons -->
</section>
<!-- /wp:uagb/section -->'

DEMO_PAGE_ID=$(wp_cli post create \
    --post_type=page \
    --post_title='Demo KenzySites' \
    --post_content="$DEMO_CONTENT" \
    --post_status=publish \
    --porcelain)

echo -e "${GREEN}✅ Página de demonstração criada! ID: $DEMO_PAGE_ID${NC}"

# Resumo final
echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Instalação Completa!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📦 Temas Instalados:${NC}"
echo -e "  • Astra (Principal)"
echo -e "  • Kadence"
echo -e "  • GeneratePress"
echo -e "  • Neve"
echo -e "  • Blocksy"
echo ""
echo -e "${BLUE}🔌 Page Builders:${NC}"
echo -e "  • Spectra (Ultimate Addons for Gutenberg)"
echo -e "  • GenerateBlocks"
echo -e "  • Kadence Blocks"
echo -e "  • Stackable"
echo ""
echo -e "${BLUE}📚 Template Libraries:${NC}"
echo -e "  • Astra Sites"
echo -e "  • Starter Templates"
echo -e "  • Extendify"
echo ""
echo -e "${YELLOW}💡 Próximos passos:${NC}"
echo -e "  1. Acesse http://localhost:8080/wp-admin"
echo -e "  2. Vá em Aparência > Astra Options"
echo -e "  3. Configure as Starter Templates"
echo -e "  4. Teste os blocos do Spectra no editor"
echo ""