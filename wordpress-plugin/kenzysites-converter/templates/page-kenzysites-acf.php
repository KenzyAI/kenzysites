<?php
/**
 * Template Name: KenzySites ACF Page
 * Template for pages converted from Elementor to ACF
 */

get_header(); ?>

<style>
/* Base styles for ACF template */
.kenzysites-acf-page {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
}

.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 80px 20px;
    text-align: center;
    margin-bottom: 50px;
}

.hero-section h1 {
    font-size: 3rem;
    margin-bottom: 20px;
    font-weight: 700;
}

.hero-section .subtitle {
    font-size: 1.2rem;
    margin-bottom: 30px;
    opacity: 0.9;
}

.hero-cta {
    background: #ff6b6b;
    color: white;
    padding: 15px 30px;
    border: none;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-block;
    transition: transform 0.3s ease;
}

.hero-cta:hover {
    transform: translateY(-2px);
    color: white;
}

.content-section {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    margin-bottom: 50px;
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin: 40px 0;
}

.service-card {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s ease;
}

.service-card:hover {
    transform: translateY(-5px);
}

.contact-section {
    background: #f8f9fa;
    padding: 60px 20px;
    text-align: center;
}

.contact-info {
    max-width: 600px;
    margin: 0 auto;
}

.contact-info h2 {
    margin-bottom: 30px;
    color: #333;
}

.contact-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.contact-item {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.testimonials {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 60px 20px;
    text-align: center;
}

.testimonial-item {
    max-width: 600px;
    margin: 0 auto;
    padding: 30px;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    margin-bottom: 20px;
}

@media (max-width: 768px) {
    .hero-section h1 {
        font-size: 2rem;
    }
    
    .services-grid {
        grid-template-columns: 1fr;
    }
    
    .contact-details {
        grid-template-columns: 1fr;
    }
}
</style>

<div class="kenzysites-acf-page">
    <?php while (have_posts()) : the_post(); ?>
        
        <!-- Hero Section -->
        <?php 
        // Get template variables
        $variables = get_post_meta(get_the_ID(), '_kenzysites_template_variables', true) ?: [];
        ?>
        <section class="hero-section">
            <h1><?php echo esc_html($variables['NOME_MEDICO'] ?? 'Dr. Especialista'); ?></h1>
            <p class="subtitle">Especialista em <?php echo esc_html($variables['ESPECIALIDADE'] ?? 'Medicina'); ?></p>
            <p class="subtitle"><?php echo esc_html($variables['CRM'] ?? ''); ?> - <?php echo esc_html($variables['CIDADE'] ?? 'Sua Cidade'); ?></p>
            
            <a href="tel:<?php echo esc_attr(preg_replace('/[^0-9]/', '', $variables['TELEFONE'] ?? '')); ?>" class="hero-cta">
                <?php echo esc_html($variables['TELEFONE'] ?? 'Agendar Consulta'); ?>
            </a>
        </section>
        
        <!-- Services Section -->
        <?php 
        $services = get_field('services');
        if ($services && is_array($services)): ?>
        <section class="content-section">
            <h2 style="text-align: center; margin-bottom: 40px;">Nossos Serviços</h2>
            <div class="services-grid">
                <?php foreach ($services as $service): ?>
                <div class="service-card">
                    <?php if (isset($service['service_icon']) && $service['service_icon']): ?>
                        <div style="font-size: 3rem; margin-bottom: 20px;">
                            <?php echo esc_html($service['service_icon']); ?>
                        </div>
                    <?php endif; ?>
                    
                    <?php if (isset($service['service_title'])): ?>
                        <h3><?php echo esc_html($service['service_title']); ?></h3>
                    <?php endif; ?>
                    
                    <?php if (isset($service['service_description'])): ?>
                        <p><?php echo esc_html($service['service_description']); ?></p>
                    <?php endif; ?>
                    
                    <?php if (isset($service['service_price'])): ?>
                        <div style="font-weight: bold; color: #667eea; font-size: 1.2rem; margin-top: 15px;">
                            <?php echo esc_html($service['service_price']); ?>
                        </div>
                    <?php endif; ?>
                </div>
                <?php endforeach; ?>
            </div>
        </section>
        <?php endif; ?>
        
        <!-- Testimonials Section -->
        <?php 
        $testimonials = get_field('testimonials');
        if ($testimonials && is_array($testimonials)): ?>
        <section class="testimonials">
            <h2 style="margin-bottom: 40px;">Depoimentos</h2>
            <?php foreach ($testimonials as $testimonial): ?>
            <div class="testimonial-item">
                <?php if (isset($testimonial['testimonial_text'])): ?>
                    <p style="font-style: italic; margin-bottom: 20px;">
                        "<?php echo esc_html($testimonial['testimonial_text']); ?>"
                    </p>
                <?php endif; ?>
                
                <?php if (isset($testimonial['testimonial_author'])): ?>
                    <strong><?php echo esc_html($testimonial['testimonial_author']); ?></strong>
                <?php endif; ?>
                
                <?php if (isset($testimonial['testimonial_rating'])): ?>
                    <div style="margin-top: 10px;">
                        <?php 
                        $rating = intval($testimonial['testimonial_rating']);
                        for ($i = 1; $i <= 5; $i++) {
                            echo $i <= $rating ? '⭐' : '☆';
                        }
                        ?>
                    </div>
                <?php endif; ?>
            </div>
            <?php endforeach; ?>
        </section>
        <?php endif; ?>
        
        <!-- Contact Section -->
        <section class="contact-section">
            <div class="contact-info">
                <h2>Entre em Contato com <?php echo esc_html($variables['NOME_MEDICO'] ?? 'o Especialista'); ?></h2>
                
                <div class="contact-details">
                    <?php if (!empty($variables['TELEFONE'])): ?>
                    <div class="contact-item">
                        <h3>📞 Telefone</h3>
                        <p><a href="tel:<?php echo esc_attr(preg_replace('/[^0-9]/', '', $variables['TELEFONE'])); ?>"><?php echo esc_html($variables['TELEFONE']); ?></a></p>
                    </div>
                    <?php endif; ?>
                    
                    <?php if (!empty($variables['EMAIL'])): ?>
                    <div class="contact-item">
                        <h3>✉️ Email</h3>
                        <p><a href="mailto:<?php echo esc_attr($variables['EMAIL']); ?>"><?php echo esc_html($variables['EMAIL']); ?></a></p>
                    </div>
                    <?php endif; ?>
                    
                    <?php if (!empty($variables['ENDERECO'])): ?>
                    <div class="contact-item">
                        <h3>📍 Endereço</h3>
                        <p><?php echo esc_html($variables['ENDERECO']); ?></p>
                    </div>
                    <?php endif; ?>
                    
                    <?php if (!empty($variables['CONSULTORIO'])): ?>
                    <div class="contact-item">
                        <h3>🏥 Consultório</h3>
                        <p><?php echo esc_html($variables['CONSULTORIO']); ?></p>
                    </div>
                    <?php endif; ?>
                    
                    <?php if (!empty($variables['FORMACAO'])): ?>
                    <div class="contact-item">
                        <h3>🎓 Formação</h3>
                        <p><?php echo esc_html($variables['FORMACAO']); ?></p>
                    </div>
                    <?php endif; ?>
                </div>
                
                <a href="https://wa.me/55<?php echo esc_attr(preg_replace('/[^0-9]/', '', $variables['TELEFONE'] ?? '')); ?>?text=Olá! Gostaria de agendar uma consulta com <?php echo esc_attr($variables['NOME_MEDICO'] ?? ''); ?>" class="hero-cta" style="margin-top: 30px;">
                    💬 WhatsApp - Agendar Consulta
                </a>
            </div>
        </section>
        
        <!-- Dynamic Content Section -->
        <?php 
        // Display any additional ACF fields that were detected from Elementor
        $all_fields = get_fields();
        $displayed_fields = ['hero_title', 'hero_subtitle', 'hero_cta_text', 'hero_cta_url', 'services', 'testimonials', 'contact_phone', 'contact_email', 'contact_address', 'contact_hours', 'contact_cta_text', 'contact_cta_url'];
        
        $additional_fields = array_diff_key($all_fields ?: [], array_flip($displayed_fields));
        
        if (!empty($additional_fields)): ?>
        <section class="content-section">
            <h2 style="text-align: center; margin-bottom: 40px;">Conteúdo Adicional</h2>
            <?php foreach ($additional_fields as $field_name => $field_value): ?>
                <?php if (!empty($field_value)): ?>
                <div style="margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    <h3 style="text-transform: capitalize; margin-bottom: 15px;">
                        <?php echo esc_html(str_replace(['_', '-'], ' ', $field_name)); ?>
                    </h3>
                    
                    <?php if (is_string($field_value)): ?>
                        <p><?php echo esc_html($field_value); ?></p>
                    <?php elseif (is_array($field_value)): ?>
                        <pre style="background: white; padding: 10px; border-radius: 4px; overflow-x: auto;">
                            <?php echo esc_html(print_r($field_value, true)); ?>
                        </pre>
                    <?php endif; ?>
                </div>
                <?php endif; ?>
            <?php endforeach; ?>
        </section>
        <?php endif; ?>
        
    <?php endwhile; ?>
</div>

<?php get_footer(); ?>