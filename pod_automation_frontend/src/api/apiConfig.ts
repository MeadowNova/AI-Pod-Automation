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
  
  // Set the authentication token if provided
  if (options?.token) {
    OpenAPI.TOKEN = options.token;
  }
  
  // Add any additional headers or configuration here
  OpenAPI.HEADERS = {
    'Content-Type': 'application/json',
  };
  
  console.log(`API client initialized with base URL: ${OpenAPI.BASE}`);
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
  } else {
    OpenAPI.TOKEN = undefined;
  }
}

/**
 * Clear the authentication token
 */
export function clearAuthToken() {
  OpenAPI.TOKEN = undefined;
}
