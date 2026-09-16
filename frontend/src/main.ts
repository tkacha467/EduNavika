// Application Entry Point — EduNavika Production Frontend
import './styles/main.css';
import { navigate } from './routes/router';
import { getRole, isAuthenticated } from './services/authService';

// Global keyboard shortcut: Cmd+K / Ctrl+K to focus search
document.addEventListener('keydown', (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    const searchInput = document.getElementById('globalSearch') as HTMLInputElement | null;
    if (searchInput) {
      searchInput.focus();
    }
  }
});

// App Initialization
function initApp(): void {
  const hash = window.location.hash.replace(/^#\/?/, '');
  if (hash) {
    navigate(hash);
  } else if (!isAuthenticated()) {
    navigate('login');
  } else {
    const role = getRole();
    navigate(`${role}/dashboard`);
  }
}

// Start once DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
