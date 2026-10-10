// Base HTTP API Client for EduNavika Backend

const API_BASE = '/api/v1';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const STORAGE_KEY_TOKEN = 'edunavika_token';

export async function request<T>(
  endpoint: string,
  options: RequestInit & { timeoutMs?: number } = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY_TOKEN) : null;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> || {}),
  };

  const timeoutMs = options.timeoutMs ?? 25000;
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timeoutId = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;

  const config: RequestInit = {
    ...options,
    headers,
    signal: options.signal || (controller ? controller.signal : undefined),
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }
      throw new ApiError(
        errorData.detail || errorData.message || `Request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }
    return (await response.json()) as T;
  } catch (err: any) {
    if (err.name === 'AbortError') {
      throw new ApiError(`Request timeout after ${timeoutMs}ms connecting to EduNavika backend`, 408);
    }
    if (err instanceof ApiError) throw err;
    throw new ApiError(err.message || 'Network error connecting to EduNavika backend', 0);
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
  }
}

export const api = {
  get: <T>(endpoint: string, options?: RequestInit & { timeoutMs?: number }) =>
    request<T>(endpoint, { method: 'GET', ...options }),
  post: <T>(endpoint: string, body?: any, options?: RequestInit & { timeoutMs?: number }) =>
    request<T>(endpoint, { method: 'POST', body: body ? JSON.stringify(body) : undefined, ...options }),
  put: <T>(endpoint: string, body?: any, options?: RequestInit & { timeoutMs?: number }) =>
    request<T>(endpoint, { method: 'PUT', body: body ? JSON.stringify(body) : undefined, ...options }),
  delete: <T>(endpoint: string, options?: RequestInit & { timeoutMs?: number }) =>
    request<T>(endpoint, { method: 'DELETE', ...options }),
};
