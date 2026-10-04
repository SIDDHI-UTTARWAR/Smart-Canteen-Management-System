// Sidebar toggle (mobile)
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
if (sidebarToggle) {
  sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
}

// Dark mode toggle (persists for the session using in-memory + data attribute)
const darkBtn = document.getElementById('darkModeToggle');
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  if (darkBtn) darkBtn.innerHTML = theme === 'dark'
    ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
}
let currentTheme = document.cookie.split('; ').find(r => r.startsWith('theme='))?.split('=')[1] || 'light';
applyTheme(currentTheme);
if (darkBtn) {
  darkBtn.addEventListener('click', () => {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(currentTheme);
    document.cookie = `theme=${currentTheme}; path=/; max-age=31536000`;
  });
}

// Auto-dismiss toast notifications
setTimeout(() => {
  document.querySelectorAll('.toast-msg').forEach(t => {
    t.style.transition = 'opacity .4s ease';
    t.style.opacity = '0';
    setTimeout(() => t.remove(), 400);
  });
}, 4000);
