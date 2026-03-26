/**
 * Login functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const verificacionMessage = document.getElementById('verificacion-message');
    const togglePassword = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');

    // Toggle password visibility
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    // Form submit
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Hide previous messages
            hideError();
            if (verificacionMessage) {
                verificacionMessage.classList.add('hidden');
            }
            
            // Get form data
            const correo = document.getElementById('correo').value.trim();
            const password = passwordInput.value;
            const recaptchaResponse = grecaptcha.getResponse();
            
            // Validate
            if (!correo) {
                showError('El correo es obligatorio');
                return;
            }
            
            if (!validateEmail(correo)) {
                showError('Ingrese un correo válido');
                return;
            }
            
            if (!password) {
                showError('La contraseña es obligatoria');
                return;
            }
            
            if (!recaptchaResponse) {
                showError('Por favor complete el captcha');
                return;
            }
            
            // Show loading
            setLoading(true);
            
            try {
                const response = await fetch('/seguridad/api/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        correo: correo,
                        password: password,
                        recaptcha: recaptchaResponse
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Store token
                    localStorage.setItem('jwt_token', data.token);
                    sessionStorage.setItem('jwt_token', data.token);
                    
                    // Redirect
                    window.location.href = data.redirect || '/seguridad/dashboard/';
                } else {
                    // Check if email not verified
                    if (data.error === 'EMAIL_NO_VERIFICADO') {
                        if (verificacionMessage) {
                            verificacionMessage.classList.remove('hidden');
                        }
                    } else {
                        showError(data.error || 'Error al iniciar sesión');
                    }
                    grecaptcha.reset();
                }
            } catch (error) {
                console.error('Login error:', error);
                showError('Error de conexión. Intente nuevamente.');
                grecaptcha.reset();
            } finally {
                setLoading(false);
            }
        });
    }

    // Helper functions
    function showError(message) {
        if (errorText && errorMessage) {
            errorText.textContent = message;
            errorMessage.classList.remove('hidden');
            errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function hideError() {
        if (errorMessage) {
            errorMessage.classList.add('hidden');
        }
    }

    function setLoading(loading) {
        if (submitBtn) {
            submitBtn.disabled = loading;
        }
        if (btnText) {
            btnText.textContent = loading ? 'Iniciando sesión...' : 'Iniciar sesión';
        }
        if (btnLoader) {
            btnLoader.classList.toggle('hidden', !loading);
        }
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});