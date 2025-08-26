/**
 * KenzySites Converter Admin JavaScript
 */

jQuery(document).ready(function($) {
    'use strict';
    
    // Global variables
    let isProcessing = false;
    let currentBatchOperation = null;
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize modals
    initModals();
    
    // Initialize filters
    initFilters();
    
    // Initialize batch operations
    initBatchOperations();
    
    /**
     * Initialize tooltips
     */
    function initTooltips() {
        $('[data-tooltip]').each(function() {
            $(this).attr('title', $(this).data('tooltip'));
        });
    }
    
    /**
     * Initialize modal functionality
     */
    function initModals() {
        // Close modal when clicking outside or on close button
        $(document).on('click', '.modal-close, .template-modal', function(e) {
            if (e.target === this) {
                $('.template-modal').fadeOut(300);
            }
        });
        
        // Prevent modal from closing when clicking inside modal content
        $(document).on('click', '.modal-content', function(e) {
            e.stopPropagation();
        });
        
        // ESC key to close modals
        $(document).on('keyup', function(e) {
            if (e.keyCode === 27) { // ESC
                $('.template-modal').fadeOut(300);
            }
        });
    }
    
    /**
     * Initialize filters
     */
    function initFilters() {
        $('#filter-type, #filter-score').on('change', function() {
            filterPages();
        });
        
        // Search functionality
        $(document).on('keyup', '#search-pages', debounce(function() {
            filterPages();
        }, 300));
    }
    
    /**
     * Filter pages based on selected criteria
     */
    function filterPages() {
        const typeFilter = $('#filter-type').val();
        const scoreFilter = parseInt($('#filter-score').val()) || 0;
        const searchTerm = $('#search-pages').val().toLowerCase();
        
        $('#pages-table-body tr').each(function() {
            const $row = $(this);
            const pageData = $row.data('page-data');
            
            if (!pageData) return;
            
            let show = true;
            
            // Type filter
            if (typeFilter && pageData.suggested_type !== typeFilter) {
                show = false;
            }
            
            // Score filter
            if (scoreFilter && pageData.conversion_score < scoreFilter) {
                show = false;
            }
            
            // Search filter
            if (searchTerm) {
                const title = pageData.title.toLowerCase();
                if (title.indexOf(searchTerm) === -1) {
                    show = false;
                }
            }
            
            $row.toggle(show);
        });
        
        updateFilterResults();
    }
    
    /**
     * Update filter results count
     */
    function updateFilterResults() {
        const totalRows = $('#pages-table-body tr').length;
        const visibleRows = $('#pages-table-body tr:visible').length;
        
        $('#filter-results').text(`${visibleRows} de ${totalRows} páginas`);
    }
    
    /**
     * Initialize batch operations
     */
    function initBatchOperations() {
        // Bulk action handler
        $('#apply-bulk-action').on('click', function() {
            const action = $('#bulk-action').val();
            const selectedPages = getSelectedPages();
            
            if (!action) {
                showNotice('Selecione uma ação.', 'warning');
                return;
            }
            
            if (selectedPages.length === 0) {
                showNotice('Selecione pelo menos uma página.', 'warning');
                return;
            }
            
            switch (action) {
                case 'convert':
                    startBulkConversion(selectedPages);
                    break;
                case 'sync':
                    startBulkSync(selectedPages);
                    break;
            }
        });
        
        // Batch conversion
        $('#start-batch-conversion').on('click', function() {
            if (isProcessing) {
                showNotice('Uma operação já está em andamento.', 'warning');
                return;
            }
            
            const settings = getBatchSettings();
            const pages = getEligiblePagesForBatch(settings);
            
            if (pages.length === 0) {
                showNotice('Nenhuma página elegível para conversão em lote.', 'warning');
                return;
            }
            
            if (confirm(`Converter ${pages.length} páginas em lote?`)) {
                startBatchConversion(pages, settings);
            }
        });
        
        // Preview batch
        $('#preview-batch').on('click', function() {
            const settings = getBatchSettings();
            const pages = getEligiblePagesForBatch(settings);
            showBatchPreview(pages, settings);
        });
    }
    
    /**
     * Get selected page IDs
     */
    function getSelectedPages() {
        const selected = [];
        $('.page-checkbox:checked').each(function() {
            selected.push(parseInt($(this).val()));
        });
        return selected;
    }
    
    /**
     * Get batch conversion settings
     */
    function getBatchSettings() {
        return {
            defaultType: $('#batch-default-type').val(),
            autoSync: $('#batch-auto-sync').is(':checked'),
            filterScore: $('#batch-filter-score').is(':checked'),
            skipConverted: $('#batch-skip-converted').is(':checked'),
            minScore: $('#batch-filter-score').is(':checked') ? 60 : 0
        };
    }
    
    /**
     * Get eligible pages for batch conversion
     */
    function getEligiblePagesForBatch(settings) {
        if (typeof window.scannedPages === 'undefined') {
            return [];
        }
        
        return window.scannedPages.filter(function(page) {
            // Skip already converted
            if (settings.skipConverted && page.is_converted) {
                return false;
            }
            
            // Score filter
            if (settings.filterScore && page.conversion_score < settings.minScore) {
                return false;
            }
            
            return true;
        });
    }
    
    /**
     * Start bulk conversion
     */
    function startBulkConversion(pageIds, settings = null) {
        if (isProcessing) return;
        
        isProcessing = true;
        currentBatchOperation = 'conversion';
        
        const batchSettings = settings || {
            defaultType: 'service_showcase',
            autoSync: true
        };
        
        showBatchProgress();
        updateBatchProgress(0, pageIds.length, 0, 0);
        
        let completed = 0;
        let successful = 0;
        let errors = 0;
        
        // Process pages sequentially to avoid overwhelming the server
        processPageSequentially(pageIds, 0, batchSettings, function(success, message, pageId) {
            completed++;
            
            if (success) {
                successful++;
                logBatchMessage(`✅ Página ${pageId}: ${message}`, 'success');
            } else {
                errors++;
                logBatchMessage(`❌ Página ${pageId}: ${message}`, 'error');
            }
            
            updateBatchProgress(completed, pageIds.length, successful, errors);
            
            if (completed === pageIds.length) {
                finishBatchOperation();
                showNotice(`Conversão concluída: ${successful} sucessos, ${errors} erros`, 
                          errors > 0 ? 'warning' : 'success');
            }
        });
    }
    
    /**
     * Process pages sequentially
     */
    function processPageSequentially(pageIds, index, settings, callback) {
        if (index >= pageIds.length) return;
        
        const pageId = pageIds[index];
        
        $.post(ajaxurl, {
            action: 'kenzysites_convert_page',
            nonce: kenzysitesAjax.nonce,
            page_id: pageId,
            landing_page_type: settings.defaultType
        })
        .done(function(response) {
            if (response.success) {
                callback(true, 'Convertido com sucesso', pageId);
                
                // Auto-sync if enabled
                if (settings.autoSync) {
                    const templateId = response.data.template_id;
                    if (templateId) {
                        syncTemplate(templateId, function(syncSuccess, syncMessage) {
                            if (!syncSuccess) {
                                logBatchMessage(`⚠️ Página ${pageId}: Sincronização falhou - ${syncMessage}`, 'warning');
                            }
                        });
                    }
                }
            } else {
                callback(false, response.data || 'Erro desconhecido', pageId);
            }
        })
        .fail(function() {
            callback(false, 'Erro de conexão', pageId);
        })
        .always(function() {
            // Process next page after a small delay
            setTimeout(function() {
                processPageSequentially(pageIds, index + 1, settings, callback);
            }, 500);
        });
    }
    
    /**
     * Sync template
     */
    function syncTemplate(templateId, callback) {
        $.post(ajaxurl, {
            action: 'kenzysites_sync_to_kenzysites',
            nonce: kenzysitesAjax.nonce,
            template_id: templateId
        })
        .done(function(response) {
            callback(response.success, response.data || response.message || '');
        })
        .fail(function() {
            callback(false, 'Erro de conexão na sincronização');
        });
    }
    
    /**
     * Show batch progress modal
     */
    function showBatchProgress() {
        $('#batch-progress').show();
        $('#progress-messages').empty();
    }
    
    /**
     * Update batch progress
     */
    function updateBatchProgress(current, total, successful, errors) {
        const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
        
        $('#progress-current').text(current);
        $('#progress-total').text(total);
        $('#progress-success').text(successful);
        $('#progress-errors').text(errors);
        
        $('.progress-fill').css('width', percentage + '%');
    }
    
    /**
     * Log batch message
     */
    function logBatchMessage(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const messageHtml = `
            <li class="progress-message ${type}">
                <span class="timestamp">${timestamp}</span>
                <span class="message">${message}</span>
            </li>
        `;
        
        const $messages = $('#progress-messages');
        $messages.append(messageHtml);
        
        // Auto-scroll to bottom
        const messagesContainer = $messages.parent();
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }
    
    /**
     * Finish batch operation
     */
    function finishBatchOperation() {
        isProcessing = false;
        currentBatchOperation = null;
        
        // Add completion message
        logBatchMessage('🎉 Operação em lote concluída!', 'success');
        
        // Re-scan pages to update status
        setTimeout(function() {
            if (typeof window.refreshPagesList === 'function') {
                window.refreshPagesList();
            }
        }, 2000);
    }
    
    /**
     * Show batch preview
     */
    function showBatchPreview(pages, settings) {
        let previewHtml = `
            <div class="batch-preview">
                <h3>Preview da Conversão em Lote</h3>
                <div class="preview-settings">
                    <p><strong>Tipo padrão:</strong> ${settings.defaultType}</p>
                    <p><strong>Sincronização automática:</strong> ${settings.autoSync ? 'Sim' : 'Não'}</p>
                    <p><strong>Páginas selecionadas:</strong> ${pages.length}</p>
                </div>
                <div class="preview-pages">
                    <ul>
        `;
        
        pages.slice(0, 10).forEach(function(page) {
            previewHtml += `<li>${page.title} (Score: ${page.conversion_score}%)</li>`;
        });
        
        if (pages.length > 10) {
            previewHtml += `<li>... e mais ${pages.length - 10} páginas</li>`;
        }
        
        previewHtml += `
                    </ul>
                </div>
                <div class="preview-actions">
                    <button type="button" class="button button-primary" onclick="jQuery('#template-details-modal').hide();">
                        OK
                    </button>
                </div>
            </div>
        `;
        
        $('#template-details-modal .modal-body').html(previewHtml);
        $('#template-details-modal').show();
    }
    
    /**
     * Show notice
     */
    function showNotice(message, type = 'info') {
        const noticeHtml = `
            <div class="notice notice-${type} is-dismissible">
                <p>${message}</p>
                <button type="button" class="notice-dismiss">
                    <span class="screen-reader-text">Dismiss this notice.</span>
                </button>
            </div>
        `;
        
        $('.wrap h1').after(noticeHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(function() {
            $('.notice').fadeOut();
        }, 5000);
        
        // Manual dismiss
        $(document).on('click', '.notice-dismiss', function() {
            $(this).parent().fadeOut();
        });
    }
    
    /**
     * Debounce utility function
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = function() {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * Format file size
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Format date
     */
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    /**
     * Copy to clipboard
     */
    function copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'absolute';
            textArea.style.left = '-999999px';
            
            document.body.prepend(textArea);
            textArea.select();
            
            try {
                document.execCommand('copy');
            } catch (error) {
                console.error('Copy failed', error);
            } finally {
                textArea.remove();
            }
        }
    }
    
    /**
     * Global functions for external use
     */
    window.KenzySitesConverter = {
        showNotice: showNotice,
        formatFileSize: formatFileSize,
        formatDate: formatDate,
        copyToClipboard: copyToClipboard,
        isProcessing: function() { return isProcessing; }
    };
    
    // Export scanned pages for other scripts
    window.scannedPages = [];
    
    // Store original console methods for debugging
    if (typeof window.kenzysitesDebug !== 'undefined' && window.kenzysitesDebug) {
        window.originalConsole = {
            log: console.log,
            warn: console.warn,
            error: console.error
        };
    }
    
    // Performance monitoring
    if (window.performance && window.performance.mark) {
        window.performance.mark('kenzysites-admin-script-loaded');
    }
});