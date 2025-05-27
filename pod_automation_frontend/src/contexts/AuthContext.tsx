import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthService } from '../api/services/AuthService';
import { setAuthToken, clearAuthToken, isAuthenticated, getStoredUser, withoutAuth, DEV_MODE_BYPASS_AUTH } from '../api/apiConfig';
import type { User } from '../api/models/User';
import { ApiError } from '../api/core/ApiError';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = () => {
      try {
        // In development mode, bypass authentication and set mock user
        if (DEV_MODE_BYPASS_AUTH) {
          const mockUser = {
            id: 'dev-user-123',
            email: 'dev@example.com',
            name: 'Development User',
            created_at: new Date().toISOString()
          };
          setUser(mockUser);
          console.log('🔧 Development mode: Authentication bypassed with mock user');
        } else if (isAuthenticated()) {
          const storedUser = getStoredUser();
          if (storedUser) {
            setUser(storedUser);
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuthToken();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await withoutAuth(() => AuthService.login({ email, password }));

      // Store tokens and user data
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // Set token in API client
      setAuthToken(response.access_token);

      // Update state
      setUser(response.user);

      // Navigate to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    clearAuthToken();
    setUser(null);
    navigate('/login');
  };

  const refreshAuth = () => {
    // Refresh the authentication state from localStorage
    if (isAuthenticated()) {
      const storedUser = getStoredUser();
      if (storedUser) {
        setUser(storedUser);
      }
    } else {
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: DEV_MODE_BYPASS_AUTH || !!user,
    login,
    logout,
    refreshAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Hook for handling API errors, especially 401s
export const useApiErrorHandler = () => {
  const { logout } = useAuth();

  const handleApiError = (error: unknown) => {
    if (error instanceof ApiError && error.status === 401) {
      // In development mode, don't redirect on 401 errors
      if (DEV_MODE_BYPASS_AUTH) {
        console.warn('🔧 Dev mode: 401 error detected but not redirecting due to auth bypass');
        return false; // Let the component handle the error locally
      }

      console.warn('Authentication failed, redirecting to login');
      logout();
      return true; // Indicates the error was handled
    }
    return false; // Indicates the error was not handled
  };

  return { handleApiError };
};
