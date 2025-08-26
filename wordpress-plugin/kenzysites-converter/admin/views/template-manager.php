<?php
/**
 * Template Manager Admin Page
 * Manages template variables and API settings for KenzySites
 */

if (!defined('ABSPATH')) {
    exit;
}

// Get all pages with template variables
global $wpdb;
$template_pages = $wpdb->get_results("
    SELECT p.ID, p.post_title, pm1.meta_value as template_type, pm2.meta_value as variables
    FROM {$wpdb->posts} p
    LEFT JOIN {$wpdb->postmeta} pm1 ON p.ID = pm1.post_id AND pm1.meta_key = '_kenzysites_template_type'
    LEFT JOIN {$wpdb->postmeta} pm2 ON p.ID = pm2.post_id AND pm2.meta_key = '_kenzysites_template_variables'
    WHERE p.post_type = 'page' 
    AND p.post_status = 'publish'
    AND pm1.meta_value IS NOT NULL
    ORDER BY p.post_title
");

// Get API key
$api_key = get_option('kenzysites_api_key', '');

// Handle API key update
if (isset($_POST['update_api_key']) && wp_verify_nonce($_POST['_wpnonce'], 'kenzysites_api_key')) {
    $new_api_key = sanitize_text_field($_POST['api_key']);
    update_option('kenzysites_api_key', $new_api_key);
    echo '<div class="notice notice-success"><p>API Key atualizada com sucesso!</p></div>';
    $api_key = $new_api_key;
}

// Generate new API key if requested
if (isset($_POST['generate_api_key']) && wp_verify_nonce($_POST['_wpnonce'], 'kenzysites_api_key')) {
    $new_api_key = 'kenzysites_' . wp_generate_password(32, false);
    update_option('kenzysites_api_key', $new_api_key);
    echo '<div class="notice notice-success"><p>Nova API Key gerada com sucesso!</p></div>';
    $api_key = $new_api_key;
}
?>

<div class="wrap">
    <h1>🚀 KenzySites Template Manager</h1>
    <p>Gerencie templates com variáveis dinâmicas para agentes automatizados</p>
    
    <!-- API Configuration -->
    <div class="card">
        <h2>🔑 Configuração da API</h2>
        <p>Configure a API key para permitir que agentes externos modifiquem os templates.</p>
        
        <form method="post" action="">
            <?php wp_nonce_field('kenzysites_api_key'); ?>
            
            <table class="form-table">
                <tr>
                    <th scope="row">API Key</th>
                    <td>
                        <input type="text" name="api_key" value="<?php echo esc_attr($api_key); ?>" class="regular-text" readonly>
                        <button type="submit" name="generate_api_key" class="button">Gerar Nova</button>
                        <p class="description">Esta chave permite que agentes alterem os templates via API REST.</p>
                    </td>
                </tr>
            </table>
        </form>
        
        <?php if ($api_key): ?>
        <div class="notice notice-info" style="margin-top: 20px;">
            <h4>📋 Endpoints da API Disponíveis:</h4>
            <ul>
                <li><code>GET /wp-json/kenzysites/v1/templates/types</code> - Listar tipos de template</li>
                <li><code>GET /wp-json/kenzysites/v1/templates/{id}/variables</code> - Obter variáveis do template</li>
                <li><code>POST /wp-json/kenzysites/v1/templates/{id}/update</code> - Atualizar variáveis</li>
                <li><code>POST /wp-json/kenzysites/v1/templates/{id}/preview</code> - Preview do template</li>
                <li><code>POST /wp-json/kenzysites/v1/templates/{id}/upload-image</code> - Upload de imagem</li>
            </ul>
            <p><strong>Header necessário:</strong> <code>X-KenzySites-API-Key: <?php echo esc_html($api_key); ?></code></p>
        </div>
        <?php endif; ?>
    </div>
    
    <!-- Template Pages -->
    <div class="card" style="margin-top: 20px;">
        <h2>📄 Templates Disponíveis</h2>
        
        <?php if (empty($template_pages)): ?>
            <p>Nenhum template encontrado. Converta uma página Elementor primeiro para criar templates.</p>
            <a href="<?php echo admin_url('admin.php?page=kenzysites-converter-convert'); ?>" class="button button-primary">Converter Página</a>
        <?php else: ?>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th>Página</th>
                        <th>Tipo</th>
                        <th>Variáveis</th>
                        <th>API Endpoint</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($template_pages as $page): 
                        $variables = unserialize($page->variables) ?: [];
                        $variable_count = count($variables);
                        $page_url = get_permalink($page->ID);
                        $edit_url = admin_url('post.php?post=' . $page->ID . '&action=edit');
                        $api_endpoint = rest_url('kenzysites/v1/templates/' . $page->ID . '/update');
                    ?>
                    <tr>
                        <td>
                            <strong><a href="<?php echo esc_url($edit_url); ?>"><?php echo esc_html($page->post_title); ?></a></strong>
                            <div class="row-actions">
                                <span><a href="<?php echo esc_url($page_url); ?>" target="_blank">Ver Página</a> | </span>
                                <span><a href="<?php echo esc_url($edit_url); ?>">Editar</a></span>
                            </div>
                        </td>
                        <td>
                            <span class="dashicons dashicons-<?php echo $page->template_type === 'medico' ? 'heart' : ($page->template_type === 'restaurante' ? 'food' : 'admin-users'); ?>"></span>
                            <?php echo esc_html(ucfirst($page->template_type)); ?>
                        </td>
                        <td>
                            <span class="badge"><?php echo $variable_count; ?> variáveis</span>
                            <?php if ($variable_count > 0): ?>
                                <details style="margin-top: 5px;">
                                    <summary style="cursor: pointer; color: #0073aa;">Ver Variáveis</summary>
                                    <ul style="margin: 5px 0; padding-left: 20px;">
                                        <?php foreach ($variables as $var_name => $var_value): ?>
                                            <li><code>{{<?php echo esc_html($var_name); ?>}}</code>: <?php echo esc_html(mb_substr($var_value, 0, 50)); ?><?php echo mb_strlen($var_value) > 50 ? '...' : ''; ?></li>
                                        <?php endforeach; ?>
                                    </ul>
                                </details>
                            <?php endif; ?>
                        </td>
                        <td>
                            <code style="font-size: 11px;">POST <?php echo esc_html($api_endpoint); ?></code>
                            <button class="button button-small copy-endpoint" data-endpoint="<?php echo esc_attr($api_endpoint); ?>" title="Copiar endpoint">📋</button>
                        </td>
                        <td>
                            <a href="#" class="button button-small test-api" data-page-id="<?php echo $page->ID; ?>" title="Testar API">🧪 Testar</a>
                            <a href="<?php echo rest_url('kenzysites/v1/templates/' . $page->ID . '/variables'); ?>" class="button button-small" target="_blank" title="Ver JSON">📄 JSON</a>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>
    
    <!-- API Testing -->
    <div class="card" style="margin-top: 20px;">
        <h2>🧪 Teste da API</h2>
        <p>Teste os endpoints da API diretamente no painel.</p>
        
        <div id="api-tester" style="display: none;">
            <h3>Testando Template: <span id="test-page-title"></span></h3>
            
            <div style="display: flex; gap: 20px;">
                <div style="flex: 1;">
                    <h4>Dados para Envio (JSON):</h4>
                    <textarea id="test-json" rows="10" style="width: 100%;" placeholder='{"variables": {"NOME_MEDICO": "Dr. Teste", "TELEFONE": "(11) 99999-9999"}}'></textarea>
                    <button id="send-test" class="button button-primary">Enviar Teste</button>
                </div>
                
                <div style="flex: 1;">
                    <h4>Resposta da API:</h4>
                    <div id="test-response" style="background: #f1f1f1; padding: 10px; border-radius: 4px; min-height: 200px; font-family: monospace; white-space: pre-wrap;"></div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent Logs -->
    <div class="card" style="margin-top: 20px;">
        <h2>📊 Atividade Recente</h2>
        
        <?php
        $recent_logs = [];
        if (class_exists('KenzySites_Template_Engine')) {
            $template_engine = new KenzySites_Template_Engine();
            $recent_logs = $template_engine->get_update_logs();
            $recent_logs = array_slice($recent_logs, 0, 10); // Last 10 entries
        }
        ?>
        
        <?php if (empty($recent_logs)): ?>
            <p>Nenhuma atividade recente encontrada.</p>
        <?php else: ?>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Página</th>
                        <th>Variáveis Alteradas</th>
                        <th>IP</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($recent_logs as $log): 
                        $page_title = get_the_title($log['page_id']) ?: 'Página #' . $log['page_id'];
                    ?>
                    <tr>
                        <td><?php echo esc_html(date('d/m/Y H:i:s', strtotime($log['timestamp']))); ?></td>
                        <td><a href="<?php echo admin_url('post.php?post=' . $log['page_id'] . '&action=edit'); ?>"><?php echo esc_html($page_title); ?></a></td>
                        <td>
                            <?php 
                            $variable_names = array_keys($log['variables']);
                            echo esc_html(implode(', ', array_slice($variable_names, 0, 3)));
                            if (count($variable_names) > 3) {
                                echo ' <span style="color: #666;">+' . (count($variable_names) - 3) . ' mais</span>';
                            }
                            ?>
                        </td>
                        <td><?php echo esc_html($log['ip_address']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>
</div>

<style>
.badge {
    background: #0073aa;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: bold;
}

.copy-endpoint {
    margin-left: 5px;
}

.card {
    background: white;
    border: 1px solid #ccd0d4;
    border-radius: 4px;
    padding: 20px;
}

#api-tester {
    background: #f9f9f9;
    padding: 15px;
    border-radius: 4px;
    border-left: 4px solid #0073aa;
}
</style>

<script>
jQuery(document).ready(function($) {
    // Copy endpoint to clipboard
    $('.copy-endpoint').on('click', function(e) {
        e.preventDefault();
        const endpoint = $(this).data('endpoint');
        navigator.clipboard.writeText(endpoint).then(function() {
            $(e.target).text('✅');
            setTimeout(() => $(e.target).text('📋'), 2000);
        });
    });
    
    // Test API
    $('.test-api').on('click', function(e) {
        e.preventDefault();
        const pageId = $(this).data('page-id');
        const pageTitle = $(this).closest('tr').find('td:first strong a').text();
        
        $('#test-page-title').text(pageTitle);
        $('#api-tester').show();
        
        // Load current variables
        $.get('<?php echo rest_url('kenzysites/v1/templates/'); ?>' + pageId + '/variables', {}, function(data) {
            const example = {
                variables: data.current_variables || {}
            };
            $('#test-json').val(JSON.stringify(example, null, 2));
        }).fail(function() {
            const example = {
                variables: {
                    "NOME_MEDICO": "Dr. João Silva",
                    "ESPECIALIDADE": "Cardiologia",
                    "TELEFONE": "(11) 99999-9999"
                }
            };
            $('#test-json').val(JSON.stringify(example, null, 2));
        });
        
        // Scroll to tester
        $('html, body').animate({
            scrollTop: $("#api-tester").offset().top - 20
        }, 500);
        
        // Store page ID for testing
        $('#send-test').data('page-id', pageId);
    });
    
    // Send test request
    $('#send-test').on('click', function() {
        const pageId = $(this).data('page-id');
        const jsonData = $('#test-json').val();
        
        try {
            const data = JSON.parse(jsonData);
            
            $('#test-response').text('Enviando...');
            
            $.ajax({
                url: '<?php echo rest_url('kenzysites/v1/templates/'); ?>' + pageId + '/update',
                method: 'POST',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('X-KenzySites-API-Key', '<?php echo esc_js($api_key); ?>');
                },
                data: data,
                success: function(response) {
                    $('#test-response').text(JSON.stringify(response, null, 2));
                },
                error: function(xhr) {
                    const error = xhr.responseJSON || {error: 'Erro desconhecido'};
                    $('#test-response').text('ERRO:\n' + JSON.stringify(error, null, 2));
                }
            });
            
        } catch (e) {
            $('#test-response').text('ERRO: JSON inválido\n' + e.message);
        }
    });
});
</script>