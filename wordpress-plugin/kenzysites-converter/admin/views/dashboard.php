<?php
/**
 * Admin Dashboard View
 */

if (!defined('ABSPATH')) {
    exit;
}

// Get statistics
$total_pages = wp_count_posts('page')->publish;
$elementor_pages = 0;
$converted_templates = 0;
$synced_templates = 0;

// Count Elementor pages
$elementor_query = new WP_Query([
    'post_type' => 'page',
    'meta_query' => [
        [
            'key' => '_elementor_edit_mode',
            'value' => 'builder',
            'compare' => '='
        ]
    ],
    'posts_per_page' => -1,
    'fields' => 'ids'
]);
$elementor_pages = $elementor_query->found_posts;

// Get converted templates stats
global $wpdb;
$table_name = $wpdb->prefix . 'kenzysites_converted_templates';
if ($wpdb->get_var("SHOW TABLES LIKE '$table_name'") == $table_name) {
    $converted_templates = $wpdb->get_var("SELECT COUNT(*) FROM $table_name");
    $synced_templates = $wpdb->get_var("SELECT COUNT(*) FROM $table_name WHERE sync_status = 'synced'");
}

// Get recent activity
$recent_conversions = $wpdb->get_results(
    "SELECT * FROM $table_name ORDER BY conversion_date DESC LIMIT 5",
    ARRAY_A
);
?>

<div class="wrap">
    <h1 class="wp-heading-inline">
        <?php _e('KenzySites Converter Dashboard', 'kenzysites-converter'); ?>
    </h1>
    
    <div class="kenzysites-header">
        <p class="description">
            <?php _e('Converta suas landing pages Elementor em templates ACF para o sistema KenzySites', 'kenzysites-converter'); ?>
        </p>
    </div>
    
    <!-- Statistics Cards -->
    <div class="kenzysites-stats-grid">
        <div class="kenzysites-stat-card">
            <div class="stat-icon">
                <span class="dashicons dashicons-admin-page"></span>
            </div>
            <div class="stat-content">
                <h3><?php echo number_format($total_pages); ?></h3>
                <p><?php _e('Total de Páginas', 'kenzysites-converter'); ?></p>
            </div>
        </div>
        
        <div class="kenzysites-stat-card elementor">
            <div class="stat-icon">
                <span class="dashicons dashicons-elementor"></span>
            </div>
            <div class="stat-content">
                <h3><?php echo number_format($elementor_pages); ?></h3>
                <p><?php _e('Páginas Elementor', 'kenzysites-converter'); ?></p>
            </div>
        </div>
        
        <div class="kenzysites-stat-card converted">
            <div class="stat-icon">
                <span class="dashicons dashicons-convert"></span>
            </div>
            <div class="stat-content">
                <h3><?php echo number_format($converted_templates); ?></h3>
                <p><?php _e('Templates Convertidos', 'kenzysites-converter'); ?></p>
            </div>
        </div>
        
        <div class="kenzysites-stat-card synced">
            <div class="stat-icon">
                <span class="dashicons dashicons-cloud-upload"></span>
            </div>
            <div class="stat-content">
                <h3><?php echo number_format($synced_templates); ?></h3>
                <p><?php _e('Sincronizados', 'kenzysites-converter'); ?></p>
            </div>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="kenzysites-quick-actions">
        <h2><?php _e('Ações Rápidas', 'kenzysites-converter'); ?></h2>
        
        <div class="action-buttons">
            <a href="<?php echo admin_url('admin.php?page=kenzysites-converter-convert'); ?>" class="button button-primary button-hero">
                <span class="dashicons dashicons-convert"></span>
                <?php _e('Converter Landing Pages', 'kenzysites-converter'); ?>
            </a>
            
            <button type="button" class="button button-secondary button-hero" id="scan-pages-btn">
                <span class="dashicons dashicons-search"></span>
                <?php _e('Escanear Páginas Elementor', 'kenzysites-converter'); ?>
            </button>
            
            <button type="button" class="button button-secondary button-hero" id="test-connection-btn">
                <span class="dashicons dashicons-admin-plugins"></span>
                <?php _e('Testar Conexão KenzySites', 'kenzysites-converter'); ?>
            </button>
            
            <a href="<?php echo admin_url('admin.php?page=kenzysites-converter-settings'); ?>" class="button button-secondary button-hero">
                <span class="dashicons dashicons-admin-generic"></span>
                <?php _e('Configurações', 'kenzysites-converter'); ?>
            </a>
        </div>
    </div>
    
    <!-- Connection Status -->
    <div class="kenzysites-connection-status">
        <h3><?php _e('Status da Conexão', 'kenzysites-converter'); ?></h3>
        
        <div class="connection-info">
            <div class="connection-indicator" id="connection-status">
                <span class="status-dot unknown"></span>
                <span class="status-text"><?php _e('Não testado', 'kenzysites-converter'); ?></span>
            </div>
            
            <div class="connection-details">
                <p><strong><?php _e('URL da API:', 'kenzysites-converter'); ?></strong> <?php echo esc_html(KenzySitesConverter::get_option('api_url', 'http://localhost:8000/api')); ?></p>
                <p><strong><?php _e('API Key:', 'kenzysites-converter'); ?></strong> 
                    <?php 
                    $api_key = KenzySitesConverter::get_option('api_key');
                    echo $api_key ? str_repeat('*', strlen($api_key) - 4) . substr($api_key, -4) : __('Não configurada', 'kenzysites-converter');
                    ?>
                </p>
            </div>
        </div>
    </div>
    
    <!-- Recent Activity -->
    <?php if (!empty($recent_conversions)): ?>
    <div class="kenzysites-recent-activity">
        <h3><?php _e('Atividade Recente', 'kenzysites-converter'); ?></h3>
        
        <table class="wp-list-table widefat fixed striped">
            <thead>
                <tr>
                    <th><?php _e('Template', 'kenzysites-converter'); ?></th>
                    <th><?php _e('Página Original', 'kenzysites-converter'); ?></th>
                    <th><?php _e('Tipo', 'kenzysites-converter'); ?></th>
                    <th><?php _e('Data Conversão', 'kenzysites-converter'); ?></th>
                    <th><?php _e('Status Sincronização', 'kenzysites-converter'); ?></th>
                    <th><?php _e('Ações', 'kenzysites-converter'); ?></th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($recent_conversions as $conversion): 
                    $page = get_post($conversion['page_id']);
                    $page_title = $page ? $page->post_title : __('Página removida', 'kenzysites-converter');
                ?>
                <tr>
                    <td><strong><?php echo esc_html($conversion['template_id']); ?></strong></td>
                    <td>
                        <?php if ($page): ?>
                            <a href="<?php echo get_edit_post_link($conversion['page_id']); ?>" target="_blank">
                                <?php echo esc_html($page_title); ?>
                            </a>
                        <?php else: ?>
                            <?php echo esc_html($page_title); ?>
                        <?php endif; ?>
                    </td>
                    <td><?php echo esc_html($conversion['landing_page_type']); ?></td>
                    <td><?php echo date_i18n('d/m/Y H:i', strtotime($conversion['conversion_date'])); ?></td>
                    <td>
                        <span class="sync-status sync-<?php echo esc_attr($conversion['sync_status']); ?>">
                            <?php 
                            switch ($conversion['sync_status']) {
                                case 'synced':
                                    _e('Sincronizado', 'kenzysites-converter');
                                    break;
                                case 'pending':
                                    _e('Pendente', 'kenzysites-converter');
                                    break;
                                case 'error':
                                    _e('Erro', 'kenzysites-converter');
                                    break;
                                default:
                                    _e('Desconhecido', 'kenzysites-converter');
                            }
                            ?>
                        </span>
                    </td>
                    <td>
                        <?php if ($conversion['sync_status'] !== 'synced'): ?>
                            <button type="button" class="button button-small sync-template-btn" 
                                    data-template-id="<?php echo esc_attr($conversion['template_id']); ?>">
                                <?php _e('Sincronizar', 'kenzysites-converter'); ?>
                            </button>
                        <?php endif; ?>
                        
                        <a href="<?php echo admin_url('admin.php?page=kenzysites-converter-convert&template=' . $conversion['template_id']); ?>" 
                           class="button button-small">
                            <?php _e('Ver Detalhes', 'kenzysites-converter'); ?>
                        </a>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        
        <p class="description">
            <a href="<?php echo admin_url('admin.php?page=kenzysites-converter-convert'); ?>">
                <?php _e('Ver todos os templates convertidos →', 'kenzysites-converter'); ?>
            </a>
        </p>
    </div>
    <?php endif; ?>
    
    <!-- Help Section -->
    <div class="kenzysites-help">
        <h3><?php _e('Como Usar', 'kenzysites-converter'); ?></h3>
        
        <div class="help-steps">
            <div class="help-step">
                <div class="step-number">1</div>
                <div class="step-content">
                    <h4><?php _e('Configure a API', 'kenzysites-converter'); ?></h4>
                    <p><?php _e('Vá em Configurações e defina a URL da API e chave de acesso do seu sistema KenzySites.', 'kenzysites-converter'); ?></p>
                </div>
            </div>
            
            <div class="help-step">
                <div class="step-number">2</div>
                <div class="step-content">
                    <h4><?php _e('Escaneie as Páginas', 'kenzysites-converter'); ?></h4>
                    <p><?php _e('Use o botão "Escanear Páginas Elementor" para identificar todas as landing pages disponíveis.', 'kenzysites-converter'); ?></p>
                </div>
            </div>
            
            <div class="help-step">
                <div class="step-number">3</div>
                <div class="step-content">
                    <h4><?php _e('Converta para ACF', 'kenzysites-converter'); ?></h4>
                    <p><?php _e('Vá em "Converter" e selecione as páginas que deseja transformar em templates ACF.', 'kenzysites-converter'); ?></p>
                </div>
            </div>
            
            <div class="help-step">
                <div class="step-number">4</div>
                <div class="step-content">
                    <h4><?php _e('Sincronize com KenzySites', 'kenzysites-converter'); ?></h4>
                    <p><?php _e('Os templates convertidos são automaticamente enviados para seu sistema KenzySites.', 'kenzysites-converter'); ?></p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Loading overlay -->
    <div id="kenzysites-loading" class="kenzysites-loading" style="display: none;">
        <div class="loading-content">
            <div class="spinner"></div>
            <p class="loading-text"><?php _e('Processando...', 'kenzysites-converter'); ?></p>
        </div>
    </div>
</div>

<script type="text/javascript">
jQuery(document).ready(function($) {
    // Scan pages button
    $('#scan-pages-btn').on('click', function() {
        const $btn = $(this);
        const originalText = $btn.text();
        
        $btn.prop('disabled', true).text(kenzysitesAjax.strings.scanning);
        
        $.post(kenzysitesAjax.ajax_url, {
            action: 'kenzysites_scan_pages',
            nonce: kenzysitesAjax.nonce
        })
        .done(function(response) {
            if (response.success) {
                alert('✅ ' + response.data.length + ' páginas Elementor encontradas!');
                location.reload();
            } else {
                alert('❌ Erro: ' + response.data);
            }
        })
        .fail(function() {
            alert('❌ Erro de conexão');
        })
        .always(function() {
            $btn.prop('disabled', false).text(originalText);
        });
    });
    
    // Test connection button
    $('#test-connection-btn').on('click', function() {
        const $btn = $(this);
        const originalText = $btn.text();
        
        $btn.prop('disabled', true).text('Testando...');
        $('#connection-status .status-dot').removeClass().addClass('status-dot testing');
        $('#connection-status .status-text').text('Testando conexão...');
        
        $.post(kenzysitesAjax.ajax_url, {
            action: 'kenzysites_test_connection',
            nonce: kenzysitesAjax.nonce
        })
        .done(function(response) {
            if (response.success) {
                $('#connection-status .status-dot').removeClass().addClass('status-dot connected');
                $('#connection-status .status-text').text('✅ Conectado com sucesso');
                alert('✅ Conexão estabelecida com sucesso!');
            } else {
                $('#connection-status .status-dot').removeClass().addClass('status-dot error');
                $('#connection-status .status-text').text('❌ Erro de conexão');
                alert('❌ Erro de conexão: ' + response.data);
            }
        })
        .fail(function() {
            $('#connection-status .status-dot').removeClass().addClass('status-dot error');
            $('#connection-status .status-text').text('❌ Falha na comunicação');
            alert('❌ Erro de comunicação com a API');
        })
        .always(function() {
            $btn.prop('disabled', false).text(originalText);
        });
    });
    
    // Sync template buttons
    $('.sync-template-btn').on('click', function() {
        const $btn = $(this);
        const templateId = $btn.data('template-id');
        const originalText = $btn.text();
        
        if (!confirm('Sincronizar template "' + templateId + '" com o KenzySites?')) {
            return;
        }
        
        $btn.prop('disabled', true).text(kenzysitesAjax.strings.syncing);
        
        $.post(kenzysitesAjax.ajax_url, {
            action: 'kenzysites_sync_to_kenzysites',
            nonce: kenzysitesAjax.nonce,
            template_id: templateId
        })
        .done(function(response) {
            if (response.success) {
                alert('✅ Template sincronizado com sucesso!');
                location.reload();
            } else {
                alert('❌ Erro na sincronização: ' + response.data);
                $btn.prop('disabled', false).text(originalText);
            }
        })
        .fail(function() {
            alert('❌ Erro de conexão durante sincronização');
            $btn.prop('disabled', false).text(originalText);
        });
    });
});
</script>