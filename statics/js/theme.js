// ===== テーマ管理（全ページ共通） =====
(function() {
    const currentTheme = localStorage.getItem('theme') || 'system';
    const html = document.documentElement;

    // テーマ適用（ちらつき防止のため即時実行）
    if (currentTheme === 'system') {
        html.removeAttribute('data-theme');
    } else {
        html.setAttribute('data-theme', currentTheme);
    }
})();

function applyTheme(theme) {
    const html = document.documentElement;
    if (theme === 'system') {
        html.removeAttribute('data-theme');
    } else {
        html.setAttribute('data-theme', theme);
    }
    localStorage.setItem('theme', theme);
    updateAllLogos();
}

function updateAllLogos() {
    const theme = localStorage.getItem('theme') || 'system';
    const isDark = theme === 'dark' ||
        (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.querySelectorAll('#logo-img').forEach(logo => {
        logo.style.mixBlendMode = isDark ? 'screen' : 'normal';
    });
}

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateAllLogos);
window.addEventListener('DOMContentLoaded', updateAllLogos);
