<?php
/**
 * Converter Page View
 */

if (!defined('ABSPATH')) {
    exit;
}

// Get Elementor pages
$elementor_scanner = new KenzySites_Elementor_Scanner();
$api_client = new KenzySites_API_Client();

$current_tab = isset($_GET['tab']) ? sanitize_text_field($_GET['tab']) : 'scan';
$landing_page_types = $api_client->get_landing_page_types();

// Get converted templates
$converted_templates = kenzysites_get_converted_templates();
?>

<div class="wrap">
    <h1 class="wp-heading-inline">
        <?php _e('Converter Landing Pages', 'kenzysites-converter'); ?>
    </h1>
    
    <div class="kenzysites-converter">
        <!-- Tabs -->
        <div class="converter-header">
            <nav class="nav-tab-wrapper">
                <a href="?page=kenzysites-converter-convert&tab=scan" 
                   class="nav-tab <?php echo $current_tab === 'scan' ? 'nav-tab-active' : ''; ?>">
                    <span class="dashicons dashicons-search"></span>
                    <?php _e('Escanear Páginas', 'kenzysites-converter'); ?>
                </a>
                <a href="?page=kenzysites-converter-convert&tab=converted" 
                   class="nav-tab <?php echo $current_tab === 'converted' ? 'nav-tab-active' : ''; ?>">
                    <span class="dashicons dashicons-convert"></span>
                    <?php _e('Templates Convertidos', 'kenzysites-converter'); ?>
                    <span class="count">(<?php echo count($converted_templates); ?>)</span>
                </a>
                <a href="?page=kenzysites-converter-convert&tab=batch" 
                   class="nav-tab <?php echo $current_tab === 'batch' ? 'nav-tab-active' : ''; ?>">
                    <span class="dashicons dashicons-admin-tools"></span>
                    <?php _e('Conversão em Lote', 'kenzysites-converter'); ?>
                </a>
            </nav>
        </div>
        
        <div class="converter-content">
            <?php if ($current_tab === 'scan'): ?>
                <!-- Scan Tab -->
                <div class="tab-content">
                    <div class="tab-header">
                        <h2><?php _e('Páginas Elementor Disponíveis', 'kenzysites-converter'); ?></h2>
                        <p class="description">
                            <?php _e('Escaneie suas páginas Elementor e converta-as em templates ACF para o KenzySites', 'kenzysites-converter'); ?>
                        </p>
                    </div>
                    
                    <div class="scan-actions">
                        <button type="button" class="button button-primary" id="scan-pages-btn">
                            <span class="dashicons dashicons-search"></span>
                            <?php _e('Escanear Páginas Elementor', 'kenzysites-converter'); ?>
                        </button>
                        
                        <div class="scan-filters">
                            <select id="filter-type">
                                <option value=""><?php _e('Todos os tipos', 'kenzysites-converter'); ?></option>
                                <?php foreach ($landing_page_types as $type): ?>
                                    <option value="<?php echo esc_attr($type['value']); ?>">
                                        <?php echo esc_html($type['label']); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                            
                            <select id="filter-score">
                                <option value=""><?php _e('Todos os scores', 'kenzysites-converter'); ?></option>
                                <option value="80"><?php _e('Score ≥ 80%', 'kenzysites-converter'); ?></option>
                                <option value="60"><?php _e('Score ≥ 60%', 'kenzysites-converter'); ?></option>
                                <option value="40"><?php _e('Score ≥ 40%', 'kenzysites-converter'); ?></option>
                            </select>
                        </div>
                    </div>
                    
                    <div id="scan-results" class="scan-results" style="display: none;">
                        <table class="wp-list-table widefat fixed striped elementor-pages-table">
                            <thead>
                                <tr>
                                    <th class="check-column">
                                        <input type="checkbox" id="select-all-pages" />
                                    </th>
                                    <th><?php _e('Página', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Preview', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Análise', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Tipo Sugerido', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Score', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Status', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Ações', 'kenzysites-converter'); ?></th>
                                </tr>
                            </thead>
                            <tbody id="pages-table-body">
                                <!-- Dynamically populated -->
                            </tbody>
                        </table>
                        
                        <div class="bulk-actions">
                            <select id="bulk-action">
                                <option value=""><?php _e('Ações em lote', 'kenzysites-converter'); ?></option>
                                <option value="convert"><?php _e('Converter Selecionadas', 'kenzysites-converter'); ?></option>
                                <option value="sync"><?php _e('Sincronizar Selecionadas', 'kenzysites-converter'); ?></option>
                            </select>
                            <button type="button" class="button" id="apply-bulk-action">
                                <?php _e('Aplicar', 'kenzysites-converter'); ?>
                            </button>
                        </div>
                    </div>
                </div>
                
            <?php elseif ($current_tab === 'converted'): ?>
                <!-- Converted Templates Tab -->
                <div class="tab-content">
                    <div class="tab-header">
                        <h2><?php _e('Templates Convertidos', 'kenzysites-converter'); ?></h2>
                        <p class="description">
                            <?php _e('Gerencie os templates que já foram convertidos para ACF', 'kenzysites-converter'); ?>
                        </p>
                    </div>
                    
                    <?php if (empty($converted_templates)): ?>
                        <div class="empty-state">
                            <div class="empty-icon">
                                <span class="dashicons dashicons-convert"></span>
                            </div>
                            <h3><?php _e('Nenhum template convertido', 'kenzysites-converter'); ?></h3>
                            <p><?php _e('Vá para a aba "Escanear Páginas" para começar a converter suas landing pages Elementor.', 'kenzysites-converter'); ?></p>
                            <a href="?page=kenzysites-converter-convert&tab=scan" class="button button-primary">
                                <?php _e('Escanear Páginas Agora', 'kenzysites-converter'); ?>
                            </a>
                        </div>
                    <?php else: ?>
                        <table class="wp-list-table widefat fixed striped">
                            <thead>
                                <tr>
                                    <th><?php _e('Template ID', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Página Original', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Tipo', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Data Conversão', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Status Sync', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Campos ACF', 'kenzysites-converter'); ?></th>
                                    <th><?php _e('Ações', 'kenzysites-converter'); ?></th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($converted_templates as $template): 
                                    $page = get_post($template['page_id']);
                                    $page_title = $page ? $page->post_title : __('Página removida', 'kenzysites-converter');
                                    $acf_data = json_decode($template['acf_data'], true);
                                    $field_count = is_array($acf_data) ? count($acf_data) : 0;
                                ?>
                                <tr>
                                    <td><strong><?php echo esc_html($template['template_id']); ?></strong></td>
                                    <td>
                                        <?php if ($page): ?>
                                            <a href="<?php echo get_edit_post_link($template['page_id']); ?>" target="_blank">
                                                <?php echo esc_html($page_title); ?>
                                            </a>
                                        <?php else: ?>
                                            <?php echo esc_html($page_title); ?>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <span class="landing-page-type type-<?php echo esc_attr($template['landing_page_type']); ?>">
                                            <?php echo esc_html(ucfirst(str_replace('_', ' ', $template['landing_page_type']))); ?>
                                        </span>
                                    </td>
                                    <td><?php echo date_i18n('d/m/Y H:i', strtotime($template['conversion_date'])); ?></td>
                                    <td>
                                        <span class="sync-status sync-<?php echo esc_attr($template['sync_status']); ?>">
                                            <?php 
                                            switch ($template['sync_status']) {
                                                case 'synced':
                                                    _e('✅ Sincronizado', 'kenzysites-converter');
                                                    break;
                                                case 'pending':
                                                    _e('⏳ Pendente', 'kenzysites-converter');
                                                    break;
                                                case 'error':
                                                    _e('❌ Erro', 'kenzysites-converter');
                                                    break;
                                                default:
                                                    _e('❓ Desconhecido', 'kenzysites-converter');
                                            }
                                            ?>
                                        </span>
                                        <?php if ($template['sync_status'] === 'error' && !empty($template['sync_error'])): ?>
                                            <div class="error-message" style="font-size: 11px; color: #dc3232; margin-top: 2px;">
                                                <?php echo esc_html($template['sync_error']); ?>
                                            </div>
                                        <?php endif; ?>
                                    </td>
                                    <td><?php echo number_format($field_count); ?> grupos</td>
                                    <td>
                                        <div class="template-actions">
                                            <?php if ($template['sync_status'] !== 'synced'): ?>
                                                <button type="button" class="button button-small sync-template-btn" 
                                                        data-template-id="<?php echo esc_attr($template['template_id']); ?>">
                                                    <?php _e('Sincronizar', 'kenzysites-converter'); ?>
                                                </button>
                                            <?php endif; ?>
                                            
                                            <button type="button" class="button button-small view-template-btn" 
                                                    data-template-id="<?php echo esc_attr($template['template_id']); ?>">
                                                <?php _e('Ver Detalhes', 'kenzysites-converter'); ?>
                                            </button>
                                            
                                            <?php if ($page): ?>
                                                <a href="<?php echo get_permalink($template['page_id']); ?>" 
                                                   class="button button-small" target="_blank">
                                                    <?php _e('Ver Original', 'kenzysites-converter'); ?>
                                                </a>
                                            <?php endif; ?>
                                        </div>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    <?php endif; ?>
                </div>
                
            <?php elseif ($current_tab === 'batch'): ?>
                <!-- Batch Conversion Tab -->
                <div class="tab-content">
                    <div class="tab-header">
                        <h2><?php _e('Conversão em Lote', 'kenzysites-converter'); ?></h2>
                        <p class="description">
                            <?php _e('Converta múltiplas páginas Elementor de uma só vez', 'kenzysites-converter'); ?>
                        </p>
                    </div>
                    
                    <div class="batch-conversion">
                        <div class="batch-settings">
                            <h3><?php _e('Configurações da Conversão', 'kenzysites-converter'); ?></h3>
                            
                            <table class="form-table">
                                <tr>
                                    <th><?php _e('Tipo Padrão', 'kenzysites-converter'); ?></th>
                                    <td>
                                        <select id="batch-default-type">
                                            <?php foreach ($landing_page_types as $type): ?>
                                                <option value="<?php echo esc_attr($type['value']); ?>" 
                                                        <?php selected($type['value'], 'service_showcase'); ?>>
                                                    <?php echo esc_html($type['label']); ?>
                                                </option>
                                            <?php endforeach; ?>
                                        </select>
                                        <p class="description">
                                            <?php _e('Tipo que será aplicado a todas as páginas selecionadas', 'kenzysites-converter'); ?>
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <th><?php _e('Sincronização Automática', 'kenzysites-converter'); ?></th>
                                    <td>
                                        <label>
                                            <input type="checkbox" id="batch-auto-sync" checked />
                                            <?php _e('Sincronizar automaticamente após conversão', 'kenzysites-converter'); ?>
                                        </label>
                                    </td>
                                </tr>
                                <tr>
                                    <th><?php _e('Filtros', 'kenzysites-converter'); ?></th>
                                    <td>
                                        <label>
                                            <input type="checkbox" id="batch-filter-score" />
                                            <?php _e('Apenas páginas com score ≥ 60%', 'kenzysites-converter'); ?>
                                        </label>
                                        <br>
                                        <label>
                                            <input type="checkbox" id="batch-skip-converted" checked />
                                            <?php _e('Pular páginas já convertidas', 'kenzysites-converter'); ?>
                                        </label>
                                    </td>
                                </tr>
                            </table>
                        </div>
                        
                        <div class="batch-actions">
                            <button type="button" class="button button-primary" id="start-batch-conversion">
                                <span class="dashicons dashicons-admin-tools"></span>
                                <?php _e('Iniciar Conversão em Lote', 'kenzysites-converter'); ?>
                            </button>
                            
                            <button type="button" class="button button-secondary" id="preview-batch">
                                <span class="dashicons dashicons-visibility"></span>
                                <?php _e('Visualizar Páginas Selecionadas', 'kenzysites-converter'); ?>
                            </button>
                        </div>
                        
                        <div id="batch-progress" class="batch-progress" style="display: none;">
                            <div class="progress-header">
                                <h3><?php _e('Progresso da Conversão', 'kenzysites-converter'); ?></h3>
                                <div class="progress-stats">
                                    <span class="stat">
                                        <strong id="progress-current">0</strong> / 
                                        <span id="progress-total">0</span>
                                    </span>
                                    <span class="stat success">
                                        ✅ <span id="progress-success">0</span>
                                    </span>
                                    <span class="stat error">
                                        ❌ <span id="progress-errors">0</span>
                                    </span>
                                </div>
                            </div>
                            
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 0%;"></div>
                            </div>
                            
                            <div class="progress-log">
                                <ul id="progress-messages"></ul>
                            </div>
                        </div>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    </div>
    
    <!-- Template Details Modal -->
    <div id="template-details-modal" class="template-modal" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3><?php _e('Detalhes do Template', 'kenzysites-converter'); ?></h3>
                <button type="button" class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <!-- Dynamically populated -->
            </div>
        </div>
    </div>
    
    <!-- Conversion Modal -->
    <div id="conversion-modal" class="template-modal" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3><?php _e('Converter Página', 'kenzysites-converter'); ?></h3>
                <button type="button" class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <form id="conversion-form">
                    <table class="form-table">
                        <tr>
                            <th><?php _e('Tipo de Landing Page', 'kenzysites-converter'); ?></th>
                            <td>
                                <select name="landing_page_type" required>
                                    <?php foreach ($landing_page_types as $type): ?>
                                        <option value="<?php echo esc_attr($type['value']); ?>">
                                            <?php echo esc_html($type['label']); ?>
                                        </option>
                                    <?php endforeach; ?>
                                </select>
                                <p class="description"><?php _e('Escolha o tipo mais adequado para esta página', 'kenzysites-converter'); ?></p>
                            </td>
                        </tr>
                    </table>
                    
                    <div class="modal-actions">
                        <button type="submit" class="button button-primary">
                            <?php _e('Converter Agora', 'kenzysites-converter'); ?>
                        </button>
                        <button type="button" class="button button-secondary modal-close">
                            <?php _e('Cancelar', 'kenzysites-converter'); ?>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
jQuery(document).ready(function($) {
    let currentPageId = null;
    let scannedPages = [];
    
    // Scan pages
    $('#scan-pages-btn').on('click', function() {
        const $btn = $(this);
        const originalText = $btn.html();
        
        $btn.prop('disabled', true).html('<span class="dashicons dashicons-update spin"></span> <?php _e('Escaneando...', 'kenzysites-converter'); ?>');
        
        $.post(ajaxurl, {
            action: 'kenzysites_scan_pages',
            nonce: kenzysitesAjax.nonce
        })
        .done(function(response) {
            if (response.success) {
                scannedPages = response.data;
                displayScannedPages(scannedPages);
                $('#scan-results').show();
            } else {
                alert('❌ Erro: ' + response.data);
            }
        })
        .fail(function() {
            alert('❌ Erro de conexão');
        })
        .always(function() {
            $btn.prop('disabled', false).html(originalText);
        });
    });
    
    // Display scanned pages
    function displayScannedPages(pages) {
        const tbody = $('#pages-table-body');
        tbody.empty();
        
        pages.forEach(function(page) {
            const row = `
                <tr data-page-id="${page.id}">
                    <td><input type="checkbox" class="page-checkbox" value="${page.id}" /></td>
                    <td>
                        <strong><a href="${page.url}" target="_blank">${page.title}</a></strong>
                        <div class="page-meta">
                            <span>ID: ${page.id}</span> | 
                            <span>Modificado: ${new Date(page.modified).toLocaleDateString()}</span>
                        </div>
                    </td>
                    <td>
                        <img src="${page.thumbnail}" class="page-thumbnail" alt="Preview" />
                    </td>
                    <td>
                        <div class="page-analysis">
                            <div>📄 ${page.analysis.sections} seções</div>
                            <div>🧩 ${page.analysis.widget_count} widgets</div>
                            <div>🔘 ${page.analysis.cta_buttons} CTAs</div>
                            ${page.analysis.has_form ? '<div>📝 Formulário</div>' : ''}
                            ${page.analysis.has_testimonials ? '<div>💬 Depoimentos</div>' : ''}
                        </div>
                    </td>
                    <td>
                        <span class="suggested-type">${page.suggested_type.replace(/_/g, ' ')}</span>
                    </td>
                    <td>
                        <div class="score-container">
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${page.conversion_score}%"></div>
                            </div>
                            <span class="score-text">${page.conversion_score}%</span>
                        </div>
                    </td>
                    <td>
                        <span class="page-status ${page.is_converted ? 'converted' : 'not-converted'}">
                            ${page.is_converted ? '✅ Convertido' : '⏳ Não convertido'}
                        </span>
                    </td>
                    <td>
                        <div class="page-actions">
                            ${!page.is_converted ? `<button type="button" class="button button-small convert-page-btn" data-page-id="${page.id}">Converter</button>` : ''}
                            <a href="${page.elementor_edit_url}" class="button button-small" target="_blank">Editar</a>
                        </div>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }
    
    // Convert single page
    $(document).on('click', '.convert-page-btn', function() {
        currentPageId = $(this).data('page-id');
        const page = scannedPages.find(p => p.id == currentPageId);
        
        if (page) {
            // Set suggested type
            $('#conversion-modal select[name="landing_page_type"]').val(page.suggested_type);
        }
        
        $('#conversion-modal').show();
    });
    
    // Conversion form submission
    $('#conversion-form').on('submit', function(e) {
        e.preventDefault();
        
        if (!currentPageId) return;
        
        const landingPageType = $(this).find('select[name="landing_page_type"]').val();
        
        $.post(ajaxurl, {
            action: 'kenzysites_convert_page',
            nonce: kenzysitesAjax.nonce,
            page_id: currentPageId,
            landing_page_type: landingPageType
        })
        .done(function(response) {
            if (response.success) {
                alert('✅ Página convertida com sucesso!');
                $('#conversion-modal').hide();
                // Refresh the page or update the row
                location.reload();
            } else {
                alert('❌ Erro na conversão: ' + response.data);
            }
        })
        .fail(function() {
            alert('❌ Erro de conexão durante conversão');
        });
    });
    
    // Modal controls
    $('.modal-close').on('click', function() {
        $('.template-modal').hide();
    });
    
    $(window).on('click', function(e) {
        if ($(e.target).hasClass('template-modal')) {
            $('.template-modal').hide();
        }
    });
    
    // Select all checkbox
    $('#select-all-pages').on('change', function() {
        $('.page-checkbox').prop('checked', this.checked);
    });
    
    // Sync template buttons
    $('.sync-template-btn').on('click', function() {
        const $btn = $(this);
        const templateId = $btn.data('template-id');
        const originalText = $btn.text();
        
        if (!confirm('Sincronizar template "' + templateId + '" com o KenzySites?')) {
            return;
        }
        
        $btn.prop('disabled', true).text('Sincronizando...');
        
        $.post(ajaxurl, {
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