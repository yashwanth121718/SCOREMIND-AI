// ============================================================
// Global Interactivity & Theme Toggle
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Handler
    const themeBtn = document.getElementById('themeBtn');
    const currentTheme = localStorage.getItem('app-theme') || 'dark';

    if (currentTheme === 'light') {
        document.body.setAttribute('data-theme', 'light');
        if (themeBtn) themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
    }

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            if (document.body.getAttribute('data-theme') === 'light') {
                document.body.removeAttribute('data-theme');
                localStorage.setItem('app-theme', 'dark');
                themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                document.body.setAttribute('data-theme', 'light');
                localStorage.setItem('app-theme', 'light');
                themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
            }
        });
    }

    // Auto-dismiss Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-custom');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
});
