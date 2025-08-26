#!/bin/bash

# Script to create a new WordPress site with Astra and Spectra configured
# Usage: ./create-site-with-astra.sh <subdomain> <title> <business_type>

SUBDOMAIN=$1
TITLE=$2
BUSINESS_TYPE=$3

if [ -z "$SUBDOMAIN" ] || [ -z "$TITLE" ]; then
    echo "Usage: $0 <subdomain> <title> [business_type]"
    exit 1
fi

echo "🚀 Creating new site: $SUBDOMAIN"

# Create the new site
wp site create \
    --slug="$SUBDOMAIN" \
    --title="$TITLE" \
    --email="site@kenzysites.com" \
    --allow-root

# Get the new site ID
SITE_ID=$(wp site list --field=blog_id --domain="$SUBDOMAIN.localhost" --allow-root)

echo "✅ Site created with ID: $SITE_ID"

# Switch to the new site and configure
wp --url="http://$SUBDOMAIN.localhost:8090" theme activate astra --allow-root

# Configure Astra based on business type
case "$BUSINESS_TYPE" in
    "restaurant")
        echo "🍴 Configuring for Restaurant..."
        wp --url="http://$SUBDOMAIN.localhost:8090" option update astra-settings '{
            "theme-color": "#d32f2f",
            "link-color": "#f57c00",
            "header-bg-color": "#ffffff",
            "footer-bg-color": "#2c2c2c",
            "site-layout": "ast-full-width-layout",
            "container-width": 1200
        }' --format=json --allow-root
        ;;
    
    "healthcare")
        echo "🏥 Configuring for Healthcare..."
        wp --url="http://$SUBDOMAIN.localhost:8090" option update astra-settings '{
            "theme-color": "#2196f3",
            "link-color": "#4caf50",
            "header-bg-color": "#ffffff",
            "footer-bg-color": "#f5f5f5",
            "site-layout": "ast-box-layout",
            "container-width": 1140
        }' --format=json --allow-root
        ;;
    
    "ecommerce")
        echo "🛒 Configuring for E-commerce..."
        wp --url="http://$SUBDOMAIN.localhost:8090" option update astra-settings '{
            "theme-color": "#673ab7",
            "link-color": "#ff5722",
            "header-bg-color": "#ffffff",
            "footer-bg-color": "#37474f",
            "site-layout": "ast-full-width-layout",
            "container-width": 1200
        }' --format=json --allow-root
        ;;
    
    *)
        echo "💼 Configuring default business theme..."
        wp --url="http://$SUBDOMAIN.localhost:8090" option update astra-settings '{
            "theme-color": "#0274be",
            "link-color": "#0274be",
            "header-bg-color": "#ffffff",
            "footer-bg-color": "#f8f9fa",
            "site-layout": "ast-box-layout",
            "container-width": 1140
        }' --format=json --allow-root
        ;;
esac

# Create sample pages with Spectra blocks
echo "📄 Creating pages with Spectra blocks..."

# Home page with Spectra blocks
wp --url="http://$SUBDOMAIN.localhost:8090" post create \
    --post_type=page \
    --post_title="Home" \
    --post_status=publish \
    --post_content='<!-- wp:uagb/section {"block_id":"hero-section"} -->
<div class="wp-block-uagb-section uagb-section__wrap">
    <!-- wp:uagb/container -->
    <div class="wp-block-uagb-container uagb-container__wrap">
        <!-- wp:heading {"level":1} -->
        <h1>Welcome to '"$TITLE"'</h1>
        <!-- /wp:heading -->
        
        <!-- wp:paragraph -->
        <p>Your success starts here. We provide exceptional services tailored to your needs.</p>
        <!-- /wp:paragraph -->
        
        <!-- wp:uagb/buttons -->
        <div class="wp-block-uagb-buttons">
            <!-- wp:uagb/buttons-child -->
            <div class="wp-block-uagb-buttons-child">
                <a class="uagb-button__link" href="#contact">Get Started</a>
            </div>
            <!-- /wp:uagb/buttons-child -->
        </div>
        <!-- /wp:uagb/buttons -->
    </div>
    <!-- /wp:uagb/container -->
</div>
<!-- /wp:uagb/section -->' \
    --allow-root

# About page
wp --url="http://$SUBDOMAIN.localhost:8090" post create \
    --post_type=page \
    --post_title="About" \
    --post_status=publish \
    --post_content='<!-- wp:uagb/info-box {"block_id":"about-info"} -->
<div class="wp-block-uagb-info-box">
    <div class="uagb-infobox__content-wrap">
        <h3 class="uagb-infobox__title">About '"$TITLE"'</h3>
        <p class="uagb-infobox__desc">We are dedicated to providing exceptional services and creating lasting value for our clients.</p>
    </div>
</div>
<!-- /wp:uagb/info-box -->' \
    --allow-root

# Services page with Spectra columns
wp --url="http://$SUBDOMAIN.localhost:8090" post create \
    --post_type=page \
    --post_title="Services" \
    --post_status=publish \
    --post_content='<!-- wp:uagb/columns {"block_id":"services-columns","columns":3} -->
<div class="wp-block-uagb-columns uagb-columns__wrap">
    <!-- wp:uagb/column -->
    <div class="wp-block-uagb-column uagb-column__wrap">
        <!-- wp:uagb/info-box -->
        <div class="wp-block-uagb-info-box">
            <h4>Service 1</h4>
            <p>Description of your first service offering.</p>
        </div>
        <!-- /wp:uagb/info-box -->
    </div>
    <!-- /wp:uagb/column -->
    
    <!-- wp:uagb/column -->
    <div class="wp-block-uagb-column uagb-column__wrap">
        <!-- wp:uagb/info-box -->
        <div class="wp-block-uagb-info-box">
            <h4>Service 2</h4>
            <p>Description of your second service offering.</p>
        </div>
        <!-- /wp:uagb/info-box -->
    </div>
    <!-- /wp:uagb/column -->
    
    <!-- wp:uagb/column -->
    <div class="wp-block-uagb-column uagb-column__wrap">
        <!-- wp:uagb/info-box -->
        <div class="wp-block-uagb-info-box">
            <h4>Service 3</h4>
            <p>Description of your third service offering.</p>
        </div>
        <!-- /wp:uagb/info-box -->
    </div>
    <!-- /wp:uagb/column -->
</div>
<!-- /wp:uagb/columns -->' \
    --allow-root

# Contact page
wp --url="http://$SUBDOMAIN.localhost:8090" post create \
    --post_type=page \
    --post_title="Contact" \
    --post_status=publish \
    --post_content='<!-- wp:uagb/forms {"block_id":"contact-form"} -->
<div class="wp-block-uagb-forms">
    <!-- Contact form will be configured here -->
    <h3>Get in Touch</h3>
    <p>We would love to hear from you!</p>
</div>
<!-- /wp:uagb/forms -->' \
    --allow-root

# Set homepage
HOME_ID=$(wp --url="http://$SUBDOMAIN.localhost:8090" post list --post_type=page --title="Home" --field=ID --allow-root)
wp --url="http://$SUBDOMAIN.localhost:8090" option update show_on_front page --allow-root
wp --url="http://$SUBDOMAIN.localhost:8090" option update page_on_front $HOME_ID --allow-root

# Create menu
wp --url="http://$SUBDOMAIN.localhost:8090" menu create "Main Menu" --allow-root

# Add pages to menu
wp --url="http://$SUBDOMAIN.localhost:8090" menu item add-post "Main Menu" \
    $(wp --url="http://$SUBDOMAIN.localhost:8090" post list --post_type=page --title="Home" --field=ID --allow-root) \
    --allow-root

wp --url="http://$SUBDOMAIN.localhost:8090" menu item add-post "Main Menu" \
    $(wp --url="http://$SUBDOMAIN.localhost:8090" post list --post_type=page --title="About" --field=ID --allow-root) \
    --allow-root

wp --url="http://$SUBDOMAIN.localhost:8090" menu item add-post "Main Menu" \
    $(wp --url="http://$SUBDOMAIN.localhost:8090" post list --post_type=page --title="Services" --field=ID --allow-root) \
    --allow-root

wp --url="http://$SUBDOMAIN.localhost:8090" menu item add-post "Main Menu" \
    $(wp --url="http://$SUBDOMAIN.localhost:8090" post list --post_type=page --title="Contact" --field=ID --allow-root) \
    --allow-root

# Assign menu to location
wp --url="http://$SUBDOMAIN.localhost:8090" menu location assign "Main Menu" primary --allow-root

echo ""
echo "========================================="
echo "✅ Site Created Successfully!"
echo "========================================="
echo "🌐 Site URL: http://$SUBDOMAIN.localhost:8090"
echo "👤 Admin URL: http://$SUBDOMAIN.localhost:8090/wp-admin"
echo "🎨 Theme: Astra (configured for $BUSINESS_TYPE)"
echo "📄 Pages created: Home, About, Services, Contact"
echo "🎯 Spectra blocks integrated"
echo "========================================="