/**
 * KenzySites Template Manager - Admin JavaScript
 */

jQuery(document).ready(function($) {
    
    // Export single template
    $('.export-template').on('click', function() {
        var templateId = $(this).data('template-id');
        var button = $(this);
        
        button.prop('disabled', true).text('Exportando...');
        
        $.ajax({
            url: kenzysites_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'kenzysites_export_template',
                template_id: templateId,
                nonce: kenzysites_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    $('#export-result').html(
                        '<div class="notice notice-success"><p>' + response.data.message + 
                        ' <a href="' + response.data.download_url + '" download>Download ' + response.data.filename + '</a></p></div>'
                    );
                    
                    // Auto download
                    window.open(response.data.download_url, '_blank');
                } else {
                    $('#export-result').html(
                        '<div class="notice notice-error"><p>Erro: ' + response.data + '</p></div>'
                    );
                }
                
                button.prop('disabled', false).text('Exportar');
            },
            error: function() {
                $('#export-result').html(
                    '<div class="notice notice-error"><p>Erro ao exportar template.</p></div>'
                );
                button.prop('disabled', false).text('Exportar');
            }
        });
    });
    
    // Export all templates
    $('#export-all-templates').on('click', function() {
        var button = $(this);
        
        button.prop('disabled', true).text('Exportando todos os templates...');
        
        $.ajax({
            url: kenzysites_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'kenzysites_export_all_templates',
                nonce: kenzysites_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    $('#export-result').html(
                        '<div class="notice notice-success"><p>' + response.data.message + 
                        ' <a href="' + response.data.download_url + '" download>Download ' + response.data.filename + '</a></p></div>'
                    );
                    
                    // Auto download
                    window.open(response.data.download_url, '_blank');
                } else {
                    $('#export-result').html(
                        '<div class="notice notice-error"><p>Erro: ' + response.data + '</p></div>'
                    );
                }
                
                button.prop('disabled', false).text('Exportar Todos os Templates');
            },
            error: function() {
                $('#export-result').html(
                    '<div class="notice notice-error"><p>Erro ao exportar templates.</p></div>'
                );
                button.prop('disabled', false).text('Exportar Todos os Templates');
            }
        });
    });
    
    // Copy placeholder to clipboard
    $('code').on('click', function() {
        var text = $(this).text();
        var temp = $('<input>');
        $('body').append(temp);
        temp.val(text).select();
        document.execCommand('copy');
        temp.remove();
        
        // Show feedback
        var original = $(this).html();
        $(this).html('✓ Copiado!').css('color', '#0066FF');
        
        setTimeout(() => {
            $(this).html(original).css('color', '');
        }, 1000);
    });
    
    // Add tooltip to placeholders
    $('code').attr('title', 'Clique para copiar');
    
    // Live preview of placeholders
    if ($('#template-preview').length > 0) {
        function updatePreview() {
            var content = $('#template-content').val();
            
            // Replace placeholders with example values
            $('.placeholder-input').each(function() {
                var placeholder = $(this).data('placeholder');
                var value = $(this).val();
                content = content.replace(new RegExp(placeholder, 'g'), value);
            });
            
            $('#template-preview').html(content);
        }
        
        $('.placeholder-input').on('input', updatePreview);
        $('#template-content').on('input', updatePreview);
    }
});