// Dashboard JavaScript functionality

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('.btn-danger[data-confirm]').click(function(e) {
        const message = $(this).data('confirm') || 'Are you sure you want to delete this item?';
        if (!confirm(message)) {
            e.preventDefault();
        }
    });

    // Loading states for buttons
    $('.btn[data-loading]').click(function() {
        const btn = $(this);
        const originalText = btn.html();
        const loadingText = btn.data('loading') || 'Loading...';
        
        btn.html(`<span class="spinner-border spinner-border-sm me-2" role="status"></span>${loadingText}`);
        btn.prop('disabled', true);
        
        // Re-enable after 3 seconds (fallback)
        setTimeout(function() {
            btn.html(originalText);
            btn.prop('disabled', false);
        }, 3000);
    });

    // Search functionality with debounce
    let searchTimeout;
    $('#search').on('input', function() {
        clearTimeout(searchTimeout);
        const searchTerm = $(this).val();
        
        searchTimeout = setTimeout(function() {
            if (searchTerm.length >= 3 || searchTerm.length === 0) {
                // Auto-submit form after 500ms delay
                $('#search').closest('form').submit();
            }
        }, 500);
    });

    // Table row click to expand details (if implemented)
    $('.table tbody tr[data-toggle="collapse"]').click(function() {
        const target = $(this).data('target');
        $(target).collapse('toggle');
    });

    // Bulk actions (if implemented)
    $('#selectAll').change(function() {
        $('.item-checkbox').prop('checked', this.checked);
        updateBulkActions();
    });

    $('.item-checkbox').change(function() {
        updateBulkActions();
    });

    function updateBulkActions() {
        const checkedItems = $('.item-checkbox:checked').length;
        const bulkActions = $('.bulk-actions');
        
        if (checkedItems > 0) {
            bulkActions.removeClass('d-none');
            bulkActions.find('.selected-count').text(checkedItems);
        } else {
            bulkActions.addClass('d-none');
        }
    }

    // Real-time updates (WebSocket placeholder)
    function initializeRealTimeUpdates() {
        // This would connect to WebSocket for real-time updates
        // For now, we'll use periodic polling for critical data
        
        setInterval(function() {
            updatePendingCounts();
        }, 30000); // Update every 30 seconds
    }

    function updatePendingCounts() {
        // Update pending user count in navigation
        $.get('/dashboard/api/pending-counts/')
            .done(function(data) {
                $('.pending-users-count').text(data.pending_users);
                $('.pending-publications-count').text(data.pending_publications);
            })
            .fail(function() {
                console.log('Failed to update pending counts');
            });
    }

    // Initialize features
    initializeRealTimeUpdates();
});

// Utility functions
function showNotification(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const alert = $(`
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('.container-fluid').prepend(alert);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        alert.fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functions for use in other scripts
window.dashboardUtils = {
    showNotification,
    formatNumber,
    formatDate,
    formatDateTime
};
