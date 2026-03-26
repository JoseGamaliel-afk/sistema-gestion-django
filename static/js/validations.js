/**
 * Form validations
 */
const Validations = {
    // Email validation
    isValidEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    },

    // Phone validation (10 digits)
    isValidPhone: function(phone) {
        const re = /^\d{10}$/;
        return re.test(phone);
    },

    // Password strength
    getPasswordStrength: function(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        
        if (strength <= 2) return { level: 'weak', text: 'Débil', color: 'red' };
        if (strength <= 4) return { level: 'medium', text: 'Media', color: 'yellow' };
        return { level: 'strong', text: 'Fuerte', color: 'green' };
    },

    // Required field
    isRequired: function(value) {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },

    // Min length
    minLength: function(value, min) {
        return value && value.length >= min;
    },

    // Max length
    maxLength: function(value, max) {
        return !value || value.length <= max;
    },

    // Numeric only
    isNumeric: function(value) {
        return /^\d+$/.test(value);
    },

    // Alphanumeric
    isAlphanumeric: function(value) {
        return /^[a-zA-Z0-9]+$/.test(value);
    },

    // Show error
    showFieldError: function(field, message) {
        const errorDiv = field.parentElement.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        } else {
            const error = document.createElement('p');
            error.className = 'field-error text-red-500 text-sm mt-1';
            error.textContent = message;
            field.parentElement.appendChild(error);
        }
        field.classList.add('border-red-500');
    },

    // Clear error
    clearFieldError: function(field) {
        const errorDiv = field.parentElement.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
        field.classList.remove('border-red-500');
    },

    // Validate form
    validateForm: function(form, rules) {
        let isValid = true;
        const errors = [];

        Object.keys(rules).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (!field) return;

            const value = field.value;
            const fieldRules = rules[fieldName];

            this.clearFieldError(field);

            for (const rule of fieldRules) {
                let valid = true;
                let message = '';

                switch (rule.type) {
                    case 'required':
                        valid = this.isRequired(value);
                        message = rule.message || 'Este campo es obligatorio';
                        break;
                    case 'email':
                        valid = !value || this.isValidEmail(value);
                        message = rule.message || 'Ingrese un email válido';
                        break;
                    case 'phone':
                        valid = !value || this.isValidPhone(value);
                        message = rule.message || 'Ingrese un teléfono válido (10 dígitos)';
                        break;
                    case 'minLength':
                        valid = this.minLength(value, rule.value);
                        message = rule.message || `Mínimo ${rule.value} caracteres`;
                        break;
                    case 'maxLength':
                        valid = this.maxLength(value, rule.value);
                        message = rule.message || `Máximo ${rule.value} caracteres`;
                        break;
                    case 'numeric':
                        valid = !value || this.isNumeric(value);
                        message = rule.message || 'Solo números';
                        break;
                    case 'match':
                        const matchField = form.querySelector(`[name="${rule.field}"]`);
                        valid = matchField && value === matchField.value;
                        message = rule.message || 'Los campos no coinciden';
                        break;
                    case 'custom':
                        valid = rule.validator(value, form);
                        message = rule.message || 'Campo inválido';
                        break;
                }

                if (!valid) {
                    isValid = false;
                    this.showFieldError(field, message);
                    errors.push({ field: fieldName, message });
                    break;
                }
            }
        });

        return { isValid, errors };
    }
};

// Real-time validation on input
document.addEventListener('DOMContentLoaded', function() {
    // Email fields
    document.querySelectorAll('input[type="email"]').forEach(field => {
        field.addEventListener('blur', function() {
            if (this.value && !Validations.isValidEmail(this.value)) {
                Validations.showFieldError(this, 'Ingrese un email válido');
            } else {
                Validations.clearFieldError(this);
            }
        });
    });

    // Phone fields
    document.querySelectorAll('input[name="celular"]').forEach(field => {
        field.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '').slice(0, 10);
        });

        field.addEventListener('blur', function() {
            if (this.value && !Validations.isValidPhone(this.value)) {
                Validations.showFieldError(this, 'Ingrese 10 dígitos numéricos');
            } else {
                Validations.clearFieldError(this);
            }
        });
    });

    // Password strength indicator
    document.querySelectorAll('input[name="password"]').forEach(field => {
        const indicator = document.createElement('div');
        indicator.className = 'password-strength mt-1 text-sm hidden';
        field.parentElement.appendChild(indicator);

        field.addEventListener('input', function() {
            if (this.value) {
                const strength = Validations.getPasswordStrength(this.value);
                indicator.textContent = `Fortaleza: ${strength.text}`;
                indicator.className = `password-strength mt-1 text-sm text-${strength.color}-500`;
                indicator.classList.remove('hidden');
            } else {
                indicator.classList.add('hidden');
            }
        });
    });
});

// Expose globally
window.Validations = Validations;