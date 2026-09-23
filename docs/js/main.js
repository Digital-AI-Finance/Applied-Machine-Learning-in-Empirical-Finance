/**
 * Main JavaScript for Applied ML in Empirical Finance Project Website
 */

// Mobile navbar dropdown toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileToggle = document.querySelector('.navbar .mobile-toggle');
    const navbarNav = document.querySelector('.navbar-nav');

    // Create backdrop overlay
    var overlay = document.createElement('div');
    overlay.className = 'nav-overlay';
    document.body.appendChild(overlay);

    function openNav() {
        navbarNav.classList.add('open');
        mobileToggle.setAttribute('aria-expanded', 'true');
        overlay.classList.add('active');
    }

    function closeNav() {
        navbarNav.classList.remove('open');
        mobileToggle.setAttribute('aria-expanded', 'false');
        overlay.classList.remove('active');
        mobileToggle.focus();
    }

    if (mobileToggle && navbarNav) {
        mobileToggle.addEventListener('click', function() {
            var isOpen = navbarNav.classList.contains('open');
            if (isOpen) { closeNav(); } else { openNav(); }
        });

        // Close on overlay click
        overlay.addEventListener('click', closeNav);

        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navbarNav.classList.contains('open')) {
                closeNav();
            }
        });

        // Close when a nav link is clicked
        navbarNav.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', closeNav);
        });
    }

    // Navbar active state
    var currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.navbar-nav a').forEach(function(link) {
        var href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });

    // Initialize theme toggle
    initTheme();

    // Initialize scroll progress bar
    initScrollProgress();

});

/**
 * Scroll progress bar
 */
function initScrollProgress() {
    var bar = document.createElement('div');
    bar.className = 'scroll-progress';
    bar.style.width = '0';
    document.body.appendChild(bar);

    window.addEventListener('scroll', function() {
        var scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        var scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        var progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
        bar.style.width = progress + '%';
    }, { passive: true });
}

/**
 * Theme toggle (dark/light mode)
 */
function initTheme() {
    var toggle = document.getElementById('theme-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', function() {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        if (isDark) {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        }
    });

    // Listen for OS preference changes when no stored preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (!localStorage.getItem('theme')) {
            if (e.matches) {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }
        }
    });
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Export functions
window.SiteUtils = {
    formatNumber
};
