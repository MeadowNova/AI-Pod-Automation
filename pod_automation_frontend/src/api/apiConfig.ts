/* API Configuration for POD Automation
 * This file configures the OpenAPI client to connect to the backend API
 */

import { OpenAPI } from './core/OpenAPI';

/**
 * Initialize the API client with the correct configuration
 * @param options Configuration options
 */
export function initializeApi(options?: {
  baseUrl?: string;
  token?: string;
}) {
  // Set the base URL for the API
  // In development, we connect to the backend API server
  // In production, this would be configured differently
  OpenAPI.BASE = options?.baseUrl || 'http://localhost:8001/api/v1';

  // Clear any authentication token for development
  OpenAPI.TOKEN = undefined;

  // Clear localStorage tokens
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');

  // Add any additional headers or configuration here
  OpenAPI.HEADERS = {
    'Content-Type': 'application/json',
  };

  console.log(`API client initialized with base URL: ${OpenAPI.BASE}`);
  console.log(`🔧 Development mode: No authentication token set`);
}

/**
 * Get the current API configuration
 */
export function getApiConfig() {
  return {
    baseUrl: OpenAPI.BASE,
    hasToken: !!OpenAPI.TOKEN,
  };
}

/**
 * Set the authentication token for API requests
 * @param token JWT token
 */
export function setAuthToken(token: string | null) {
  if (token) {
    OpenAPI.TOKEN = token;
    localStorage.setItem('access_token', token);
  } else {
    OpenAPI.TOKEN = undefined;
    localStorage.removeItem('access_token');
  }
}

/**
 * Clear the authentication token
 */
export function clearAuthToken() {
  OpenAPI.TOKEN = undefined;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!OpenAPI.TOKEN || !!localStorage.getItem('access_token');
}

/**
 * Get stored user data
 */
export function getStoredUser() {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
}

/**
 * Development mode flag - set to true to bypass authentication
 */
export const DEV_MODE_BYPASS_AUTH = true;

/**
 * Mock user for development mode
 */
export const DEV_MOCK_USER = {
  id: 'dev-user-123',
  email: 'dev@example.com',
  name: 'Development User',
  created_at: new Date().toISOString()
};

/**
 * Temporarily clear the token for public API calls
 */
export function withoutAuth<T>(apiCall: () => Promise<T>): Promise<T> {
  const originalToken = OpenAPI.TOKEN;

  // Temporarily remove the token
  OpenAPI.TOKEN = undefined;

  // Make the API call and restore the token afterwards
  return apiCall().finally(() => {
    OpenAPI.TOKEN = originalToken;
  });
}

/**
 * Set up development mode with mock authentication
 */
export function setupDevMode() {
  if (DEV_MODE_BYPASS_AUTH) {
    // Set a mock token for development
    OpenAPI.TOKEN = 'dev-mock-token-123';
    localStorage.setItem('access_token', 'dev-mock-token-123');
    localStorage.setItem('user', JSON.stringify(DEV_MOCK_USER));
    console.log('🔧 Development mode: Authentication bypassed with mock user');
  }
}
