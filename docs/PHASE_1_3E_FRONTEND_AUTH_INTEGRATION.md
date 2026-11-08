# Phase 1.3E Frontend Authentication Integration

Removed the API-login fallback that accepted embedded student/teacher credentials after an API error. The client now fails closed on an incomplete or failed login response. The API client sends same-origin credentials and auth CSRF headers.
