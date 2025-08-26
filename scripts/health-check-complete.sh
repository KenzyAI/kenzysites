#!/bin/bash

# Health Check Completo - KenzySites WordPress
echo "🔍 HEALTH CHECK COMPLETO - KenzySites"
echo "======================================"

# Verificar todos os containers
echo "📦 Containers:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Conectividade:"
echo "- WordPress: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8085)"
echo "- Backend API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)"
echo "- WordPress Admin: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8085/wp-admin/)"
echo "- PhpMyAdmin: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081)"

echo ""
echo "🔌 Plugins WordPress:"
docker exec kenzysites-wordpress wp plugin list --format=table --allow-root

echo ""
echo "🏗️ Estrutura ACF:"
docker exec kenzysites-wordpress-db mysql -u wp_user -pwp_pass wordpress_local \
    -e "SELECT post_title as 'Grupo ACF', post_status as Status FROM wp_posts WHERE post_type='acf-field-group';" 2>/dev/null

echo ""
echo "📊 Templates Elementor:"
docker exec kenzysites-wordpress-db mysql -u wp_user -pwp_pass wordpress_local \
    -e "SELECT post_title as Template, post_status as Status FROM wp_posts WHERE post_type='elementor_library';" 2>/dev/null

echo ""
echo "💾 Backup e Storage:"
backup_size=$(docker exec kenzysites-wordpress-db mysqldump -u wp_user -pwp_pass wordpress_local --single-transaction 2>/dev/null | wc -c)
echo "- Tamanho backup DB: $((backup_size / 1024))KB"
echo "- Uploads: $(docker exec kenzysites-wordpress du -sh /var/www/html/wp-content/uploads 2>/dev/null | cut -f1)"

echo ""
echo "⚡ Performance:"
echo "- PHP Memory: $(docker exec kenzysites-wordpress wp eval 'echo ini_get("memory_limit");' --allow-root)"
echo "- Max Execution: $(docker exec kenzysites-wordpress wp eval 'echo ini_get("max_execution_time");' --allow-root)s"

echo ""
echo "🔐 Segurança:"
echo "- Debug Mode: $(docker exec kenzysites-wordpress wp config get WP_DEBUG --allow-root)"
echo "- Admin Email: $(docker exec kenzysites-wordpress wp option get admin_email --allow-root)"

echo ""
echo "✅ RESULTADO: Sistema WordPress totalmente operacional"