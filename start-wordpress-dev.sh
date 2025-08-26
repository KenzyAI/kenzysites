#!/bin/bash

# KenzySites - Start WordPress Development Environment

echo "🚀 Starting KenzySites WordPress Development Environment"
echo "========================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start containers
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.wordpress-dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check if WordPress is accessible
echo "🔍 Checking WordPress status..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8090 | grep -q "200\|302"; then
    echo "✅ WordPress is running!"
else
    echo "⚠️ WordPress is starting up. Running setup..."
    ./scripts/setup-wordpress-dev.sh
fi

# Display status
echo ""
echo "✅ Development Environment Ready!"
echo "================================="
echo ""
echo "🌐 WordPress: http://localhost:8090"
echo "🔧 Admin Panel: http://localhost:8090/wp-admin"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🗄️ PHPMyAdmin: http://localhost:8091"
echo "   Username: wordpress"
echo "   Password: wordpress_pass"
echo ""
echo "📋 Available Commands:"
echo "  • Stop environment: docker-compose -f docker-compose.wordpress-dev.yml down"
echo "  • View logs: docker-compose -f docker-compose.wordpress-dev.yml logs -f"
echo "  • Run WP-CLI: docker-compose -f docker-compose.wordpress-dev.yml run --rm wp-cli <command>"
echo ""
echo "🎨 Ready to create templates with Elementor!"