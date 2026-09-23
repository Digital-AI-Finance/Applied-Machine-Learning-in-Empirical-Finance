/* Theme detection — must run before first paint to prevent flash */
(function() {
    var t = localStorage.getItem('theme');
    if (t === 'dark' || (!t && matchMedia('(prefers-color-scheme:dark)').matches)) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
})();
