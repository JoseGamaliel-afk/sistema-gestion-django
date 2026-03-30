(function() {
    const DARK_CLASS = 'dark';

    function applyLight() {
        document.documentElement.classList.remove(DARK_CLASS);
        localStorage.setItem('theme', 'light');
    }

    applyLight();

    document.addEventListener('DOMContentLoaded', applyLight);

    window.themeManager = {
        toggle: applyLight,
        set: applyLight,
        get: () => 'light'
    };
})();