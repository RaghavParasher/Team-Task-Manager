// Ethara.ai - App JS

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Toast Notifications =====
    // Auto-dismiss toasts after 3 seconds with slide-out animation
    const toasts = document.querySelectorAll('.toast');
    
    toasts.forEach(function(toast, index) {
        // Stagger entrance animation
        toast.style.animationDelay = (index * 0.1) + 's';
        
        // Auto-dismiss after 3 seconds
        setTimeout(function() {
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 400);
        }, 3000 + (index * 500)); // stagger dismissal too
    });

    // ===== Progress Bar Animation =====
    // Animate progress bars on page load
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    progressBars.forEach(function(bar) {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = targetWidth;
        }, 200);
    });

    // ===== Distribution Bar Animation =====
    const distBars = document.querySelectorAll('.dist-bar-fill');
    distBars.forEach(function(bar, index) {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = targetWidth;
        }, 300 + (index * 100));
    });
});
