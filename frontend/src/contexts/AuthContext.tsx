import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { API_BASE_URL } from '../axios';

interface User {
  id: string;
  email: string;
  plan?: string;  // "lite" | "pro" — SaaS tier from backend
  username?: string;
  name?: string;
  role?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email?: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchMe = useCallback(async (token: string): Promise<User> => {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      throw new Error(`Failed to load user profile (${res.status})`);
    }
    const data: any = await res.json();
    // Be tolerant of differing shapes between dev-login and /auth/me
    return {
      id: String(data?.id ?? data?.user?.id ?? ''),
      email: String(data?.email ?? data?.user?.email ?? ''),
      plan: data?.plan ?? data?.user?.plan ?? 'lite',
      username: data?.username ?? data?.user?.username,
      name: data?.full_name ?? data?.name ?? data?.user?.full_name ?? data?.user?.name,
      role: data?.role ?? data?.user?.role,
    };
  }, []);

  const refresh = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setUser(null);
      return;
    }
    try {
      const me = await fetchMe(token);
      if (!me.email) {
        // If backend returns no identity, treat as unauthenticated
        throw new Error('User profile missing email');
      }
      setUser(me);
    } catch (err) {
      console.warn('[auth] /auth/me failed; clearing token', err);
      localStorage.removeItem('token');
      localStorage.removeItem('auth_token'); // legacy
      localStorage.removeItem('jwt'); // legacy
      localStorage.removeItem('userEmail'); // legacy allowlist
      setUser(null);
    }
  }, [fetchMe]);

  useEffect(() => {
    (async () => {
      try {
        await refresh();
      } finally {
        setIsLoading(false);
      }
    })();
  }, [refresh]);

  const login = async (email?: string): Promise<void> => {
    // Optional dev-only allowlist gate (off by default)
    const allowlistEnabled =
      import.meta.env.DEV && String(import.meta.env.VITE_DEV_EMAIL_ALLOWLIST || '').toLowerCase() === 'true';

    if (allowlistEnabled) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email || !emailRegex.test(email)) {
        throw new Error('Please enter a valid email address');
      }
      const { default: emailRepository } = await import('../services/emailRepository');
      const { default: emailNotificationService } = await import('../services/emailNotificationService');

      const authorizedUser = emailRepository.getEmailByAddress(email);
      if (!authorizedUser || !authorizedUser.isActive) {
        throw new Error(
          'This email address is not authorized to access the system or is inactive. Please contact your administrator.'
        );
      }

      // Optional: send login notification (best effort)
      try {
        await emailNotificationService.sendLoginNotification({
          userEmail: authorizedUser.email,
          userName: authorizedUser.name || 'Unknown',
          userRole: authorizedUser.role || 'User',
          loginTime: new Date().toLocaleString(),
          ipAddress: 'Unknown',
          userAgent: navigator.userAgent,
        });
      } catch {
        // ignore
      }
    }

    // Remember chosen dev identity (used for dev token refreshes)
    if (email) {
      localStorage.setItem('dev_login_email', email);
    }

    // Dev-friendly login: obtain a JWT via /auth/dev-login when available.
    // In production this should be replaced by a real Auth0 login flow, but we keep backend APIs unchanged.
    const res = await fetch(`${API_BASE_URL}/auth/dev-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: (email ? JSON.stringify({ email }) : undefined),
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`Login failed (${res.status}) ${text}`);
    }
    const data: any = await res.json();
    const token = String(data?.access_token || '');
    if (!token) {
      throw new Error('Login failed: missing access_token');
    }

    // Single source of truth: JWT token
    localStorage.setItem('token', token);
    // Backward-compatible mirrors (legacy callers)
    localStorage.setItem('auth_token', token);
    localStorage.setItem('jwt', token);
    localStorage.removeItem('userEmail');

    await refresh();
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('jwt');
    localStorage.removeItem('userEmail');
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user && !!localStorage.getItem('token'),
    login,
    logout,
    refresh,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
