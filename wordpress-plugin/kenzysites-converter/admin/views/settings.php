<?php
/**
 * Settings Page View
 */

if (!defined('ABSPATH')) {
    exit;
}

// Handle form submission
if (isset($_POST['submit']) && wp_verify_nonce($_POST['kenzysites_settings_nonce'], 'kenzysites_settings')) {
    // Sanitize and save settings
    $api_url = sanitize_url($_POST['api_url']);
    $api_key = sanitize_text_field($_POST['api_key']);
    $auto_sync = isset($_POST['auto_sync']) ? 'yes' : 'no';
    $sync_interval = intval($_POST['sync_interval']);
    
    // Validate URL
    if (!empty($api_url) && !filter_var($api_url, FILTER_VALIDATE_URL)) {
        $error_message = __('URL da API inválida', 'kenzysites-converter');
    } else {
        // Save options
        KenzySitesConverter::update_option('api_url', $api_url);
        KenzySitesConverter::update_option('api_key', $api_key);
        KenzySitesConverter::update_option('auto_sync', $auto_sync);
        KenzySitesConverter::update_option('sync_interval', $sync_interval);
        
        $success_message = __('Configurações salvas com sucesso!', 'kenzysites-converter');
    }
}

// Clear error logs
if (isset($_POST['clear_logs']) && wp_verify_nonce($_POST['kenzysites_settings_nonce'], 'kenzysites_settings')) {
    $api_client = new KenzySites_API_Client();
    $cleared = $api_client->clear_error_logs();
    $success_message = sprintf(__('%d logs de erro removidos', 'kenzysites-converter'), $cleared);
}

// Get current settings
$api_url = KenzySitesConverter::get_option('api_url', 'http://localhost:8000/api');
$api_key = KenzySitesConverter::get_option('api_key', '');
$auto_sync = KenzySitesConverter::get_option('auto_sync', 'yes');
$sync_interval = KenzySitesConverter::get_option('sync_interval', 30);

// Get API status
$api_client = new KenzySites_API_Client();
$health_status = $api_client->get_health_status();
$sync_stats = $api_client->get_sync_stats();
?>

<div class="wrap kenzysites-settings">
    <h1 class="wp-heading-inline">
        <?php _e('Configurações KenzySites', 'kenzysites-converter'); ?>
    </h1>
    
    <?php if (isset($success_message)): ?>
        <div class="notice notice-success is-dismissible">
            <p><?php echo esc_html($success_message); ?></p>
        </div>
    <?php endif; ?>
    
    <?php if (isset($error_message)): ?>
        <div class="notice notice-error is-dismissible">
            <p><?php echo esc_html($error_message); ?></p>
        </div>
    <?php endif; ?>
    
    <form method="post" action="">
        <?php wp_nonce_field('kenzysites_settings', 'kenzysites_settings_nonce'); ?>
        
        <!-- API Configuration -->
        <div class="settings-section">
            <div class="settings-section-header">
                <h3><?php _e('Configuração da API', 'kenzysites-converter'); ?></h3>
                <p class="description"><?php _e('Configure a conexão com seu sistema KenzySites', 'kenzysites-converter'); ?></p>
            </div>
            
            <div class="settings-section-content">
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="api_url"><?php _e('URL da API', 'kenzysites-converter'); ?></label>
                        </th>
                        <td>
                            <input type="url" id="api_url" name="api_url" value="<?php echo esc_attr($api_url); ?>" 
                                   class="regular-text" placeholder="http://localhost:8000/api" required />
                            <p class="description">
                                <?php _e('URL base da API do seu sistema KenzySites', 'kenzysites-converter'); ?>
                            </p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">
                            <label for="api_key"><?php _e('Chave da API', 'kenzysites-converter'); ?></label>
                        </th>
                        <td>
                            <input type="password" id="api_key" name="api_key" value="<?php echo esc_attr($api_key); ?>" 
                                   class="regular-text" />
                            <button type="button" class="button button-secondary" id="toggle-api-key">
                                <?php _e('Mostrar/Ocultar', 'kenzysites-converter'); ?>
                            </button>
                            <p class="description">
                                <?php _e('Chave de autenticação da API (obtida no painel KenzySites)', 'kenzysites-converter'); ?>
                            </p>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        
        <!-- Sync Configuration -->
        <div class="settings-section">
            <div class="settings-section-header">
                <h3><?php _e('Configurações de Sincronização', 'kenzysites-converter'); ?></h3>
                <p class="description"><?php _e('Configure como os templates são sincronizados', 'kenzysites-converter'); ?></p>
            </div>
            
            <div class="settings-section-content">
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <?php _e('Sincronização Automática', 'kenzysites-converter'); ?>
                        </th>
                        <td>
                            <label>
                                <input type="checkbox" name="auto_sync" value="yes" 
                                       <?php checked($auto_sync, 'yes'); ?> />
                                <?php _e('Sincronizar templates automaticamente após conversão', 'kenzysites-converter'); ?>
                            </label>
                            <p class="description">
                                <?php _e('Quando ativado, templates convertidos são enviados automaticamente para o KenzySites', 'kenzysites-converter'); ?>
                            </p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">
                            <label for="sync_interval"><?php _e('Intervalo de Verificação', 'kenzysites-converter'); ?></label>
                        </th>
                        <td>
                            <input type="number" id="sync_interval" name="sync_interval" 
                                   value="<?php echo esc_attr($sync_interval); ?>" 
                                   min="5" max="1440" class="small-text" />
                            <?php _e('minutos', 'kenzysites-converter'); ?>
                            <p class="description">
                                <?php _e('Frequência para verificar templates pendentes de sincronização', 'kenzysites-converter'); ?>
                            </p>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        
        <!-- API Status -->
        <div class="settings-section">
            <div class="settings-section-header">
                <h3><?php _e('Status da API', 'kenzysites-converter'); ?></h3>
                <p class="description"><?php _e('Informações sobre a conexão com a API', 'kenzysites-converter'); ?></p>
            </div>
            
            <div class="settings-section-content">
                <div class="api-status-grid">
                    <div class="status-item">
                        <h4><?php _e('Status da Conexão', 'kenzysites-converter'); ?></h4>
                        <div class="status-indicator">
                            <span class="status-dot status-<?php echo esc_attr($health_status['status']); ?>"></span>
                            <span class="status-text">
                                <?php 
                                switch ($health_status['status']) {
                                    case 'healthy':
                                        _e('✅ Conectado', 'kenzysites-converter');
                                        break;
                                    case 'unhealthy':
                                        _e('⚠️ Instável', 'kenzysites-converter');
                                        break;
                                    default:
                                        _e('❌ Desconectado', 'kenzysites-converter');
                                }
                                ?>
                            </span>
                        </div>
                        <p class="status-message"><?php echo esc_html($health_status['message']); ?></p>
                        <p class="status-timestamp">
                            <?php _e('Última verificação:', 'kenzysites-converter'); ?>
                            <?php echo date_i18n('d/m/Y H:i:s', strtotime($health_status['timestamp'])); ?>
                        </p>
                    </div>
                    
                    <div class="status-item">
                        <h4><?php _e('Estatísticas de Sincronização', 'kenzysites-converter'); ?></h4>
                        <div class="sync-stats">
                            <div class="stat">
                                <span class="stat-number"><?php echo number_format($sync_stats['total']); ?></span>
                                <span class="stat-label"><?php _e('Total', 'kenzysites-converter'); ?></span>
                            </div>
                            <div class="stat">
                                <span class="stat-number"><?php echo number_format($sync_stats['synced']); ?></span>
                                <span class="stat-label"><?php _e('Sincronizados', 'kenzysites-converter'); ?></span>
                            </div>
                            <div class="stat">
                                <span class="stat-number"><?php echo number_format($sync_stats['pending']); ?></span>
                                <span class="stat-label"><?php _e('Pendentes', 'kenzysites-converter'); ?></span>
                            </div>
                            <div class="stat">
                                <span class="stat-number"><?php echo number_format($sync_stats['errors']); ?></span>
                                <span class="stat-label"><?php _e('Erros', 'kenzysites-converter'); ?></span>
                            </div>
                        </div>
                        <?php if ($sync_stats['last_sync']): ?>
                            <p class="last-sync">
                                <?php _e('Última sincronização:', 'kenzysites-converter'); ?>
                                <?php echo date_i18n('d/m/Y H:i:s', strtotime($sync_stats['last_sync'])); ?>
                            </p>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Actions -->
        <div class="settings-section">
            <div class="settings-section-header">
                <h3><?php _e('Ações', 'kenzysites-converter'); ?></h3>
                <p class="description"><?php _e('Ferramentas de manutenção e teste', 'kenzysites-converter'); ?></p>
            </div>
            
            <div class="settings-section-content">
                <div class="action-buttons">
                    <button type="button" class="button button-secondary" id="test-connection-btn">
                        <span class="dashicons dashicons-admin-plugins"></span>
                        <?php _e('Testar Conexão', 'kenzysites-converter'); ?>
                    </button>
                    
                    <button type="button" class="button button-secondary" id="sync-all-btn">
                        <span class="dashicons dashicons-update"></span>
                        <?php _e('Sincronizar Pendentes', 'kenzysites-converter'); ?>
                    </button>
                    
                    <button type="submit" name="clear_logs" class="button button-secondary" 
                            onclick="return confirm('<?php _e('Tem certeza que deseja limpar todos os logs de erro?', 'kenzysites-converter'); ?>')">
                        <span class="dashicons dashicons-trash"></span>
                        <?php _e('Limpar Logs de Erro', 'kenzysites-converter'); ?>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- System Information -->
        <div class="settings-section">
            <div class="settings-section-header">
                <h3><?php _e('Informações do Sistema', 'kenzysites-converter'); ?></h3>
                <p class="description"><?php _e('Informações úteis para suporte', 'kenzysites-converter'); ?></p>
            </div>
            
            <div class="settings-section-content">
                <table class="widefat striped">
                    <tbody>
                        <tr>
                            <td><strong><?php _e('Versão do Plugin', 'kenzysites-converter'); ?></strong></td>
                            <td><?php echo KENZYSITES_CONVERTER_VERSION; ?></td>
                        </tr>
                        <tr>
                            <td><strong><?php _e('Versão do WordPress', 'kenzysites-converter'); ?></strong></td>
                            <td><?php echo get_bloginfo('version'); ?></td>
                        </tr>
                        <tr>
                            <td><strong><?php _e('Versão do Elementor', 'kenzysites-converter'); ?></strong></td>
                            <td><?php echo defined('ELEMENTOR_VERSION') ? ELEMENTOR_VERSION : __('Não instalado', 'kenzysites-converter'); ?></td>
                        </tr>
                        <tr>
                            <td><strong><?php _e('Versão do PHP', 'kenzysites-converter'); ?></strong></td>
                            <td><?php echo PHP_VERSION; ?></td>
                        </tr>
                        <tr>
                            <td><strong><?php _e('URL do Site', 'kenzysites-converter'); ?></strong></td>
                            <td><?php echo get_site_url(); ?></td>
                        </tr>
                        <tr>
                            <td><strong><?php _e('Tema Ativo', 'kenzysites-converter'); ?></strong></td>
                            <td><?php echo wp_get_theme()->get('Name'); ?></td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="margin-top: 15px;">
                    <button type="button" class="button button-secondary" id="copy-system-info">
                        <span class="dashicons dashicons-clipboard"></span>
                        <?php _e('Copiar Informações do Sistema', 'kenzysites-converter'); ?>
                    </button>
                </div>
            </div>
        </div>
        
        <?php submit_button(__('Salvar Configurações', 'kenzysites-converter')); ?>
    </form>
    
    <!-- Debug Panel -->
    <?php if (defined('WP_DEBUG') && WP_DEBUG): ?>
    <div class="settings-section">
        <div class="settings-section-header">
            <h3><?php _e('Painel de Debug', 'kenzysites-converter'); ?></h3>
            <p class="description"><?php _e('Informações de debug (visível apenas com WP_DEBUG ativado)', 'kenzysites-converter'); ?></p>
        </div>
        
        <div class="settings-section-content">
            <textarea class="widefat" rows="10" readonly id="debug-info">
<?php
echo "=== DEBUG INFORMATION ===\n";
echo "Plugin Version: " . KENZYSITES_CONVERTER_VERSION . "\n";
echo "WordPress Version: " . get_bloginfo('version') . "\n";
echo "PHP Version: " . PHP_VERSION . "\n";
echo "API URL: " . $api_url . "\n";
echo "API Key: " . (empty($api_key) ? 'Not set' : 'Set (' . strlen($api_key) . ' chars)') . "\n";
echo "Auto Sync: " . $auto_sync . "\n";
echo "Sync Interval: " . $sync_interval . " minutes\n";
echo "Health Status: " . json_encode($health_status, JSON_PRETTY_PRINT) . "\n";
echo "Sync Stats: " . json_encode($sync_stats, JSON_PRETTY_PRINT) . "\n";
?>
            </textarea>
        </div>
    </div>
    <?php endif; ?>
</div>

<script type="text/javascript">
jQuery(document).ready(function($) {
    // Toggle API key visibility
    $('#toggle-api-key').on('click', function() {
        const $input = $('#api_key');
        const type = $input.attr('type') === 'password' ? 'text' : 'password';
        $input.attr('type', type);
    });
    
    // Test connection
    $('#test-connection-btn').on('click', function() {
        const $btn = $(this);
        const originalText = $btn.html();
        
        $btn.prop('disabled', true).html('<span class="dashicons dashicons-update spin"></span> Testando...');
        
        $.post(ajaxurl, {
            action: 'kenzysites_test_connection',
            nonce: '<?php echo wp_create_nonce("kenzysites_nonce"); ?>'
        })
        .done(function(response) {
            if (response.success) {
                alert('✅ Conexão estabelecida com sucesso!\n\nResposta da API: ' + JSON.stringify(response.data, null, 2));
                location.reload();
            } else {
                alert('❌ Erro de conexão:\n\n' + response.data);
            }
        })
        .fail(function() {
            alert('❌ Erro de comunicação com o servidor');
        })
        .always(function() {
            $btn.prop('disabled', false).html(originalText);
        });
    });
    
    // Sync all pending templates
    $('#sync-all-btn').on('click', function() {
        const $btn = $(this);
        const originalText = $btn.html();
        
        if (!confirm('<?php _e('Sincronizar todos os templates pendentes?', 'kenzysites-converter'); ?>')) {
            return;
        }
        
        $btn.prop('disabled', true).html('<span class="dashicons dashicons-update spin"></span> Sincronizando...');
        
        // This would be implemented as a custom AJAX action
        $.post(ajaxurl, {
            action: 'kenzysites_sync_all_pending',
            nonce: '<?php echo wp_create_nonce("kenzysites_nonce"); ?>'
        })
        .done(function(response) {
            if (response.success) {
                const result = response.data;
                alert(`✅ Sincronização concluída!\n\nSucesso: ${result.success}\nErros: ${result.errors}`);
                location.reload();
            } else {
                alert('❌ Erro na sincronização: ' + response.data);
            }
        })
        .fail(function() {
            alert('❌ Erro de comunicação durante sincronização');
        })
        .always(function() {
            $btn.prop('disabled', false).html(originalText);
        });
    });
    
    // Copy system info
    $('#copy-system-info').on('click', function() {
        let systemInfo = '';
        $('.widefat tbody tr').each(function() {
            const label = $(this).find('td:first strong').text();
            const value = $(this).find('td:last').text();
            systemInfo += label + ': ' + value + '\n';
        });
        
        navigator.clipboard.writeText(systemInfo).then(function() {
            alert('✅ Informações do sistema copiadas para a área de transferência!');
        }).catch(function() {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = systemInfo;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert('✅ Informações do sistema copiadas!');
        });
    });
});
</script>

<style>
.api-status-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-top: 15px;
}

.status-item {
    padding: 15px;
    background: #f8f9fa;
    border-radius: 4px;
    border-left: 4px solid #ddd;
}

.status-item h4 {
    margin-top: 0;
    margin-bottom: 10px;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.status-dot.status-healthy {
    background: #4caf50;
}

.status-dot.status-unhealthy {
    background: #ff9800;
}

.status-dot.status-error {
    background: #f44336;
}

.sync-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin: 10px 0;
}

.stat {
    text-align: center;
    padding: 8px;
    background: white;
    border-radius: 3px;
}

.stat-number {
    display: block;
    font-size: 20px;
    font-weight: bold;
    color: #0073aa;
}

.stat-label {
    font-size: 12px;
    color: #666;
}

.action-buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.action-buttons .button {
    display: flex;
    align-items: center;
    gap: 5px;
}

.spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
    .api-status-grid {
        grid-template-columns: 1fr;
    }
    
    .sync-stats {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .action-buttons {
        flex-direction: column;
    }
}
</style>