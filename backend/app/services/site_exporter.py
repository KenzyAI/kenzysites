"""
Site Exporter Service
Handles exporting generated sites to various formats
"""

import json
import zipfile
import io
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from pathlib import Path
import yaml
import xml.etree.ElementTree as ET
from xml.dom import minidom

from app.services.template_personalizer_v2 import PersonalizedTemplate
from app.services.wordpress_generator import WordPressGenerator

logger = logging.getLogger(__name__)

class ExportFormat:
    """Supported export formats"""
    JSON = "json"
    WORDPRESS_XML = "wordpress_xml"
    HTML_STATIC = "html_static"
    ELEMENTOR_TEMPLATE = "elementor_template"
    ZIP_PACKAGE = "zip_package"
    DOCKER_COMPOSE = "docker_compose"

class SiteExporter:
    """
    Service for exporting generated sites to various formats
    """
    
    def __init__(self):
        self.wordpress_generator = WordPressGenerator()
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
        
    def export_site(
        self,
        personalized_template: PersonalizedTemplate,
        format: str = ExportFormat.ZIP_PACKAGE,
        include_assets: bool = True,
        include_database: bool = False
    ) -> bytes:
        """
        Export a personalized site to the specified format
        
        Args:
            personalized_template: The personalized template to export
            format: Export format (json, wordpress_xml, html_static, etc.)
            include_assets: Include images and other assets
            include_database: Include database dump (for WordPress)
            
        Returns:
            Exported data as bytes
        """
        
        logger.info(f"Exporting site {personalized_template.personalization_id} as {format}")
        
        if format == ExportFormat.JSON:
            return self._export_as_json(personalized_template)
        elif format == ExportFormat.WORDPRESS_XML:
            return self._export_as_wordpress_xml(personalized_template)
        elif format == ExportFormat.HTML_STATIC:
            return self._export_as_html_static(personalized_template, include_assets)
        elif format == ExportFormat.ELEMENTOR_TEMPLATE:
            return self._export_as_elementor_template(personalized_template)
        elif format == ExportFormat.ZIP_PACKAGE:
            return self._export_as_zip_package(personalized_template, include_assets, include_database)
        elif format == ExportFormat.DOCKER_COMPOSE:
            return self._export_as_docker_compose(personalized_template)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_as_json(self, template: PersonalizedTemplate) -> bytes:
        """Export as JSON configuration"""
        
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "exporter_version": "1.0.0",
                "personalization_id": template.personalization_id,
                "template_id": template.template_id,
                "template_name": template.template_name
            },
            "business_info": {
                "name": template.business_name,
                "industry": template.industry,
                "description": template.business_description
            },
            "template_data": template.template_data,
            "placeholder_values": template.placeholder_values,
            "seo_data": template.seo_data,
            "brazilian_features": template.brazilian_features,
            "wordpress_config": {
                "theme": "astra",
                "required_plugins": [
                    "elementor",
                    "advanced-custom-fields",
                    "wp-whatsapp-chat",
                    "yoast-seo",
                    "woocommerce-extra-checkout-fields-for-brazil"
                ],
                "settings": {
                    "timezone": "America/Sao_Paulo",
                    "date_format": "d/m/Y",
                    "time_format": "H:i",
                    "start_of_week": "0",
                    "language": "pt_BR"
                }
            }
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
    
    def _export_as_wordpress_xml(self, template: PersonalizedTemplate) -> bytes:
        """Export as WordPress WXR (WordPress eXtended RSS) format"""
        
        # Create root element
        root = ET.Element("rss", {
            "version": "2.0",
            "xmlns:excerpt": "http://wordpress.org/export/1.2/excerpt/",
            "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
            "xmlns:wfw": "http://wellformedweb.org/CommentAPI/",
            "xmlns:dc": "http://purl.org/dc/elements/1.1/",
            "xmlns:wp": "http://wordpress.org/export/1.2/"
        })
        
        channel = ET.SubElement(root, "channel")
        
        # Add metadata
        ET.SubElement(channel, "title").text = template.business_name
        ET.SubElement(channel, "link").text = f"https://{template.business_name.lower().replace(' ', '-')}.kenzysites.com"
        ET.SubElement(channel, "description").text = template.business_description
        ET.SubElement(channel, "language").text = "pt-BR"
        ET.SubElement(channel, "wp:wxr_version").text = "1.2"
        
        # Add pages from template
        for page_data in template.template_data.get("pages", []):
            item = ET.SubElement(channel, "item")
            
            ET.SubElement(item, "title").text = page_data.get("title", "")
            ET.SubElement(item, "link").text = page_data.get("slug", "")
            ET.SubElement(item, "wp:post_type").text = "page"
            ET.SubElement(item, "wp:status").text = "publish"
            
            # Add page content
            content = ET.SubElement(item, "content:encoded")
            content.text = self._generate_page_html(page_data, template.placeholder_values)
            
            # Add meta fields for Elementor
            if page_data.get("elementor_data"):
                postmeta = ET.SubElement(item, "wp:postmeta")
                ET.SubElement(postmeta, "wp:meta_key").text = "_elementor_data"
                ET.SubElement(postmeta, "wp:meta_value").text = json.dumps(page_data["elementor_data"])
        
        # Convert to string with pretty printing
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        return xml_str.encode('utf-8')
    
    def _export_as_html_static(self, template: PersonalizedTemplate, include_assets: bool) -> bytes:
        """Export as static HTML site"""
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add index.html
            index_html = self._generate_index_html(template)
            zip_file.writestr("index.html", index_html)
            
            # Add CSS
            css_content = self._generate_css(template)
            zip_file.writestr("assets/css/style.css", css_content)
            
            # Add JavaScript
            js_content = self._generate_javascript(template)
            zip_file.writestr("assets/js/main.js", js_content)
            
            # Add pages
            for page_data in template.template_data.get("pages", []):
                page_html = self._generate_page_html(page_data, template.placeholder_values)
                page_slug = page_data.get("slug", "page")
                zip_file.writestr(f"{page_slug}.html", page_html)
            
            # Add README
            readme_content = self._generate_readme(template)
            zip_file.writestr("README.md", readme_content)
            
            if include_assets:
                # Add placeholder for images
                zip_file.writestr("assets/images/.gitkeep", "")
        
        return zip_buffer.getvalue()
    
    def _export_as_elementor_template(self, template: PersonalizedTemplate) -> bytes:
        """Export as Elementor template JSON"""
        
        elementor_data = {
            "version": "1.0.0",
            "title": template.template_name,
            "type": "kit",
            "keywords": [template.industry, "kenzysites", "brazilian"],
            "site_settings": {
                "site_name": template.business_name,
                "site_description": template.business_description,
                "custom_colors": [
                    {
                        "title": "Primary",
                        "color": template.template_data.get("color_scheme", {}).get("primary", "#007cba")
                    },
                    {
                        "title": "Secondary",
                        "color": template.template_data.get("color_scheme", {}).get("secondary", "#002c5f")
                    },
                    {
                        "title": "Accent",
                        "color": template.template_data.get("color_scheme", {}).get("accent", "#ffc107")
                    }
                ],
                "custom_typography": [
                    {
                        "title": "Heading",
                        "typography": {
                            "font_family": template.template_data.get("typography", {}).get("heading_font", "Montserrat"),
                            "font_weight": "700"
                        }
                    },
                    {
                        "title": "Body",
                        "typography": {
                            "font_family": template.template_data.get("typography", {}).get("body_font", "Open Sans"),
                            "font_weight": "400"
                        }
                    }
                ]
            },
            "templates": []
        }
        
        # Add page templates
        for page_data in template.template_data.get("pages", []):
            elementor_data["templates"].append({
                "id": page_data.get("id", ""),
                "title": page_data.get("title", ""),
                "type": "page",
                "data": page_data.get("elementor_data", [])
            })
        
        return json.dumps(elementor_data, indent=2).encode('utf-8')
    
    def _export_as_zip_package(
        self,
        template: PersonalizedTemplate,
        include_assets: bool,
        include_database: bool
    ) -> bytes:
        """Export as complete ZIP package with all files"""
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add JSON configuration
            json_data = self._export_as_json(template)
            zip_file.writestr("config/site-config.json", json_data)
            
            # Add WordPress XML
            wordpress_xml = self._export_as_wordpress_xml(template)
            zip_file.writestr("wordpress/import.xml", wordpress_xml)
            
            # Add Elementor template
            elementor_template = self._export_as_elementor_template(template)
            zip_file.writestr("elementor/template.json", elementor_template)
            
            # Add Docker files
            docker_compose = self._export_as_docker_compose(template)
            zip_file.writestr("docker/docker-compose.yml", docker_compose)
            
            # Add installation script
            install_script = self._generate_install_script(template)
            zip_file.writestr("install.sh", install_script)
            
            # Add documentation
            readme = self._generate_detailed_readme(template)
            zip_file.writestr("README.md", readme)
            
            if include_assets:
                # Add placeholder directories
                zip_file.writestr("assets/images/.gitkeep", "")
                zip_file.writestr("assets/fonts/.gitkeep", "")
                zip_file.writestr("assets/videos/.gitkeep", "")
            
            if include_database:
                # Add database schema
                db_schema = self._generate_database_schema(template)
                zip_file.writestr("database/schema.sql", db_schema)
        
        return zip_buffer.getvalue()
    
    def _export_as_docker_compose(self, template: PersonalizedTemplate) -> bytes:
        """Export as Docker Compose configuration"""
        
        docker_config = {
            "version": "3.8",
            "services": {
                "wordpress": {
                    "image": "wordpress:latest",
                    "container_name": f"{template.business_name.lower().replace(' ', '_')}_wp",
                    "ports": ["8080:80"],
                    "environment": {
                        "WORDPRESS_DB_HOST": "db",
                        "WORDPRESS_DB_USER": "wordpress",
                        "WORDPRESS_DB_PASSWORD": "wordpress123",
                        "WORDPRESS_DB_NAME": "wordpress",
                        "WORDPRESS_DEBUG": "true",
                        "WORDPRESS_CONFIG_EXTRA": """
                            define('WP_MEMORY_LIMIT', '256M');
                            define('WP_MAX_MEMORY_LIMIT', '512M');
                            define('WPLANG', 'pt_BR');
                            define('WP_TIMEZONE', 'America/Sao_Paulo');
                        """
                    },
                    "volumes": [
                        "./wordpress:/var/www/html",
                        "./uploads:/var/www/html/wp-content/uploads"
                    ],
                    "networks": ["wp_network"],
                    "depends_on": ["db"]
                },
                "db": {
                    "image": "mysql:8.0",
                    "container_name": f"{template.business_name.lower().replace(' ', '_')}_db",
                    "environment": {
                        "MYSQL_ROOT_PASSWORD": "root123",
                        "MYSQL_DATABASE": "wordpress",
                        "MYSQL_USER": "wordpress",
                        "MYSQL_PASSWORD": "wordpress123"
                    },
                    "volumes": [
                        "./database:/var/lib/mysql"
                    ],
                    "networks": ["wp_network"]
                },
                "phpmyadmin": {
                    "image": "phpmyadmin:latest",
                    "container_name": f"{template.business_name.lower().replace(' ', '_')}_pma",
                    "ports": ["8081:80"],
                    "environment": {
                        "PMA_HOST": "db",
                        "PMA_USER": "root",
                        "PMA_PASSWORD": "root123"
                    },
                    "networks": ["wp_network"],
                    "depends_on": ["db"]
                }
            },
            "networks": {
                "wp_network": {
                    "driver": "bridge"
                }
            },
            "volumes": {
                "wordpress": {},
                "database": {},
                "uploads": {}
            }
        }
        
        return yaml.dump(docker_config, default_flow_style=False).encode('utf-8')
    
    def _generate_page_html(self, page_data: Dict[str, Any], placeholders: Dict[str, str]) -> str:
        """Generate HTML for a page"""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{page_data.get('title', 'Página')}</title>
            <link rel="stylesheet" href="assets/css/style.css">
        </head>
        <body>
            <div class="page-content">
                {self._replace_placeholders(page_data.get('content', ''), placeholders)}
            </div>
            <script src="assets/js/main.js"></script>
        </body>
        </html>
        """
        return html
    
    def _generate_index_html(self, template: PersonalizedTemplate) -> str:
        """Generate main index.html file"""
        
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{template.business_name}</title>
            <meta name="description" content="{template.business_description}">
            <link rel="stylesheet" href="assets/css/style.css">
        </head>
        <body>
            <header>
                <h1>{template.business_name}</h1>
                <nav>
                    <ul>
                        {''.join([f'<li><a href="{p.get("slug", "#")}.html">{p.get("title", "")}</a></li>' 
                                for p in template.template_data.get("pages", [])])}
                    </ul>
                </nav>
            </header>
            <main>
                <section class="hero">
                    <h2>{template.placeholder_values.get('{{hero_title}}', 'Bem-vindo')}</h2>
                    <p>{template.placeholder_values.get('{{hero_subtitle}}', template.business_description)}</p>
                </section>
            </main>
            <footer>
                <p>&copy; {datetime.now().year} {template.business_name}. Todos os direitos reservados.</p>
                <p>Criado com KenzySites</p>
            </footer>
            <script src="assets/js/main.js"></script>
        </body>
        </html>
        """
    
    def _generate_css(self, template: PersonalizedTemplate) -> str:
        """Generate CSS stylesheet"""
        
        colors = template.template_data.get("color_scheme", {})
        typography = template.template_data.get("typography", {})
        
        return f"""
        /* KenzySites Generated Stylesheet */
        :root {{
            --primary-color: {colors.get('primary', '#007cba')};
            --secondary-color: {colors.get('secondary', '#002c5f')};
            --accent-color: {colors.get('accent', '#ffc107')};
            --text-color: {colors.get('text', '#333333')};
            --bg-color: {colors.get('background', '#ffffff')};
            --heading-font: {typography.get('heading_font', 'Montserrat')}, sans-serif;
            --body-font: {typography.get('body_font', 'Open Sans')}, sans-serif;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: var(--body-font);
            color: var(--text-color);
            background-color: var(--bg-color);
            line-height: 1.6;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: var(--heading-font);
            color: var(--primary-color);
            margin-bottom: 1rem;
        }}
        
        a {{
            color: var(--accent-color);
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        header {{
            background: var(--primary-color);
            color: white;
            padding: 1rem 0;
        }}
        
        nav ul {{
            list-style: none;
            display: flex;
            gap: 2rem;
        }}
        
        nav a {{
            color: white;
        }}
        
        .hero {{
            padding: 4rem 0;
            text-align: center;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }}
        
        footer {{
            background: var(--secondary-color);
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 4rem;
        }}
        """
    
    def _generate_javascript(self, template: PersonalizedTemplate) -> str:
        """Generate JavaScript file"""
        
        return """
        // KenzySites Generated JavaScript
        document.addEventListener('DOMContentLoaded', function() {
            console.log('KenzySites site initialized');
            
            // WhatsApp button handler
            const whatsappBtn = document.querySelector('.whatsapp-float');
            if (whatsappBtn) {
                whatsappBtn.addEventListener('click', function() {
                    window.open('https://wa.me/55' + this.dataset.number, '_blank');
                });
            }
            
            // Smooth scroll for navigation
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth' });
                    }
                });
            });
            
            // LGPD Cookie consent
            if (!localStorage.getItem('lgpd-accepted')) {
                const banner = document.createElement('div');
                banner.className = 'lgpd-banner';
                banner.innerHTML = `
                    <p>Este site usa cookies. Ao continuar navegando, você concorda com nossa política de privacidade.</p>
                    <button onclick="localStorage.setItem('lgpd-accepted', 'true'); this.parentElement.remove();">Aceitar</button>
                `;
                document.body.appendChild(banner);
            }
        });
        """
    
    def _generate_readme(self, template: PersonalizedTemplate) -> str:
        """Generate basic README file"""
        
        return f"""
# {template.business_name}

Site gerado automaticamente pelo KenzySites.

## Informações

- **Indústria**: {template.industry}
- **Template**: {template.template_name}
- **Gerado em**: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Como usar

1. Extraia todos os arquivos
2. Abra o arquivo `index.html` em seu navegador
3. Para publicar, faça upload dos arquivos para seu servidor

## Suporte

Para suporte, visite [KenzySites](https://kenzysites.com)
        """
    
    def _generate_detailed_readme(self, template: PersonalizedTemplate) -> str:
        """Generate detailed README with installation instructions"""
        
        return f"""
# {template.business_name} - Pacote de Instalação

## 📋 Sobre

Site gerado automaticamente pelo KenzySites com as seguintes características:

- **Nome do Negócio**: {template.business_name}
- **Indústria**: {template.industry}
- **Template Base**: {template.template_name}
- **ID de Personalização**: {template.personalization_id}
- **Data de Geração**: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 🚀 Instalação Rápida

### Opção 1: Docker (Recomendado)

```bash
# 1. Entre na pasta docker
cd docker

# 2. Inicie os containers
docker-compose up -d

# 3. Acesse o site em http://localhost:8080
```

### Opção 2: Servidor WordPress Existente

1. Faça login no WordPress Admin
2. Vá em Ferramentas > Importar
3. Instale o importador WordPress
4. Faça upload do arquivo `wordpress/import.xml`
5. Importe o conteúdo

### Opção 3: Elementor

1. Instale e ative o Elementor
2. Vá em Elementor > Minhas Templates
3. Importe o arquivo `elementor/template.json`

## 📁 Estrutura do Pacote

```
├── config/
│   └── site-config.json     # Configuração completa do site
├── wordpress/
│   └── import.xml           # Arquivo de importação WordPress
├── elementor/
│   └── template.json        # Template Elementor
├── docker/
│   └── docker-compose.yml   # Configuração Docker
├── assets/                  # Recursos (imagens, fontes, etc)
├── database/                # Schema do banco de dados
├── install.sh              # Script de instalação automática
└── README.md               # Este arquivo
```

## ⚙️ Configurações

### Recursos Brasileiros Habilitados

{self._format_brazilian_features(template.brazilian_features)}

### SEO

- **Título**: {template.seo_data.get('title', '')}
- **Descrição**: {template.seo_data.get('description', '')}
- **Palavras-chave**: {', '.join(template.seo_data.get('keywords', []))}

## 🔧 Personalização

Para personalizar o site após a instalação:

1. **Cores**: Edite as variáveis CSS em `style.css`
2. **Conteúdo**: Use o editor WordPress ou Elementor
3. **Funcionalidades**: Ative/desative plugins conforme necessário

## 📞 Suporte

- **Documentação**: https://docs.kenzysites.com
- **Suporte**: suporte@kenzysites.com
- **WhatsApp**: +55 11 99999-9999

## 📝 Licença

Este site foi gerado pelo KenzySites. Todos os direitos do conteúdo pertencem a {template.business_name}.

---

Gerado com ❤️ pelo KenzySites - Criação de Sites com IA
        """
    
    def _generate_install_script(self, template: PersonalizedTemplate) -> str:
        """Generate installation bash script"""
        
        return f"""#!/bin/bash

# KenzySites - Script de Instalação Automática
# Site: {template.business_name}

echo "========================================="
echo "  KenzySites - Instalador Automático"
echo "  Site: {template.business_name}"
echo "========================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    echo "Visite: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    echo "Visite: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker encontrado"

# Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p wordpress database uploads

# Definir permissões
echo "🔐 Configurando permissões..."
chmod -R 755 wordpress uploads
chmod -R 700 database

# Iniciar containers
echo "🚀 Iniciando containers Docker..."
cd docker
docker-compose up -d

# Aguardar WordPress inicializar
echo "⏳ Aguardando WordPress inicializar (30 segundos)..."
sleep 30

# Verificar se está rodando
if docker ps | grep -q wordpress; then
    echo "✅ WordPress está rodando!"
    echo ""
    echo "========================================="
    echo "  INSTALAÇÃO CONCLUÍDA!"
    echo "========================================="
    echo ""
    echo "📌 Acesse seu site em:"
    echo "   http://localhost:8080"
    echo ""
    echo "📌 Acesse o admin em:"
    echo "   http://localhost:8080/wp-admin"
    echo "   Usuário: admin"
    echo "   Senha: (configure no primeiro acesso)"
    echo ""
    echo "📌 phpMyAdmin disponível em:"
    echo "   http://localhost:8081"
    echo ""
else
    echo "❌ Erro ao iniciar WordPress"
    echo "Execute 'docker-compose logs' para ver os erros"
    exit 1
fi
        """
    
    def _generate_database_schema(self, template: PersonalizedTemplate) -> str:
        """Generate database schema SQL"""
        
        return f"""
-- KenzySites Database Schema
-- Site: {template.business_name}
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

-- Custom tables for Brazilian features

-- WhatsApp messages table
CREATE TABLE IF NOT EXISTS `wp_kenzysites_whatsapp` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `phone` varchar(20) NOT NULL,
  `message` text NOT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PIX payments table
CREATE TABLE IF NOT EXISTS `wp_kenzysites_pix` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `transaction_id` varchar(100) NOT NULL,
  `pix_key` varchar(100) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `customer_name` varchar(100),
  `customer_cpf` varchar(14),
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `paid_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- LGPD consent log
CREATE TABLE IF NOT EXISTS `wp_kenzysites_lgpd` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) UNSIGNED,
  `ip_address` varchar(45),
  `consent_type` varchar(50),
  `consent_given` tinyint(1) DEFAULT 0,
  `consent_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Site analytics
CREATE TABLE IF NOT EXISTS `wp_kenzysites_analytics` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `page_url` varchar(255),
  `visitor_ip` varchar(45),
  `user_agent` text,
  `referrer` varchar(255),
  `visit_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `page_url` (`page_url`),
  KEY `visit_date` (`visit_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    
    def _replace_placeholders(self, content: str, placeholders: Dict[str, str]) -> str:
        """Replace placeholders in content"""
        
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, value)
        return content
    
    def _format_brazilian_features(self, features: Dict[str, Any]) -> str:
        """Format Brazilian features for README"""
        
        output = []
        if features.get("whatsapp_enabled"):
            output.append(f"- ✅ WhatsApp: {features.get('whatsapp_number', 'Não configurado')}")
        if features.get("pix_enabled"):
            output.append(f"- ✅ PIX: {features.get('pix_key', 'Não configurado')}")
        if features.get("lgpd_compliant"):
            output.append("- ✅ LGPD: Conformidade ativada")
        if features.get("brazilian_payment_methods"):
            output.append("- ✅ Métodos de pagamento brasileiros")
        if features.get("local_shipping"):
            output.append("- ✅ Frete para o Brasil")
            
        return '\n'.join(output) if output else "Nenhum recurso brasileiro configurado"

# Create singleton instance
site_exporter = SiteExporter()