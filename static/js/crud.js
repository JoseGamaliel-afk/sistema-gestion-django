/**
 * CRUD operations helper
 */
const CrudManager = {
    // Delete confirmation
    confirmDelete: function(id, name, url, csrfToken) {
        return new Promise((resolve, reject) => {
            if (confirm(`¿Está seguro de eliminar "${name}"?`)) {
                this.delete(id, url, csrfToken)
                    .then(resolve)
                    .catch(reject);
            } else {
                reject('Cancelled');
            }
        });
    },

    // Delete request
    delete: async function(id, url, csrfToken) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });

            const data = await response.json();

            if (data.success) {
                return data;
            } else {
                throw new Error(data.error || 'Error al eliminar');
            }
        } catch (error) {
            console.error('Delete error:', error);
            throw error;
        }
    },

    // Search with debounce
    search: (function() {
        let timeout;
        return function(callback, delay = 300) {
            clearTimeout(timeout);
            timeout = setTimeout(callback, delay);
        };
    })(),

    // Show toast notification
    showToast: function(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg flex items-center z-50 transform transition-all duration-300 ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white`;
        
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} mr-2"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        });
        
        // Remove after delay
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(amount);
    },

    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('es-CO', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },

    // Paginate
    paginate: function(items, page, perPage) {
        const start = (page - 1) * perPage;
        const end = start + perPage;
        return {
            items: items.slice(start, end),
            totalPages: Math.ceil(items.length / perPage),
            currentPage: page,
            totalItems: items.length
        };
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-auto-hide');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(el => {
        el.classList.add('tooltip');
    });
});

// Expose globally
window.CrudManager = CrudManager;