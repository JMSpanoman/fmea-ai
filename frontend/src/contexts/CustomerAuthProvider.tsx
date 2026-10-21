import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';
import { API_BASE_URL, getCustomerAccessToken, setCustomerTokenGetter } from '../axios';
import { AuthContext, type AuthContextType, type User } from './AuthContext';

export const SR1_API_AUDIENCE = 'https://smartrisk.fotonconsulting.com/api';
export const SR1_CALLBACK_ORIGINS = [
  'https://fmea-frontend-dczh.onrender.com',
  'https://sr1-sandbox-frontend-dczh.onrender.com',
];

export function customerAuthConfigurationError(origin = typeof window === 'undefined' ? '' : window.location.origin): string | null {
  const audience = import.meta.env.VITE_AUTH0_AUDIENCE;
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  if (!domain || !clientId || !audience) return null;
  if (audience !== SR1_API_AUDIENCE) return 'SmartRisk Auth0 audience is not the configured SR1 API.';
  let host = '';
  try { host = new URL(origin).hostname; } catch { host = ''; }
  const local = host === 'localhost' || host === '127.0.0.1' || host === '[::1]';
  if (!local && !SR1_CALLBACK_ORIGINS.includes(origin)) return 'This origin is not a registered Auth0 callback URL.';
  return null;
}

function CustomerSession({ children }: { children: React.ReactNode }) {
  const { user: identity, error: authError, isAuthenticated, isLoading, getAccessTokenSilently, loginWithRedirect, logout: auth0Logout } = useAuth0();
  const [user, setUser] = useState<User | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    if (!isAuthenticated) { setUser(null); return; }
    setLoadingProfile(true);
    setError('');
    try {
      setCustomerTokenGetter(getAccessTokenSilently);
      const token = await getCustomerAccessToken();
      if (!token) throw new Error('Your session has expired. Sign in again to continue.');
      ['token', 'auth_token', 'jwt', 'userEmail', 'dev_login_email', 'user'].forEach(key => localStorage.removeItem(key));
      const response = await fetch(`${API_BASE_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(typeof data.detail === 'string' ? data.detail : `Account unavailable (${response.status}). Please try again.`);
      }
      const profile = await response.json();
      const entitlement = profile.entitlement && profile.entitlement.unlimited === true
        ? {
            unlimited: true,
            permanent: profile.entitlement.permanent === true,
            label: typeof profile.entitlement.label === 'string' ? profile.entitlement.label : 'Owner — Unlimited',
            quotas: {
              projects: null,
              components: null,
              fmea_analyses: null,
              ai_generations: null,
              reports: null,
              exports: null,
            },
          }
        : profile.entitlement
          ? {
              unlimited: false,
              permanent: false,
              label: null,
              quotas: {
                projects: typeof profile.entitlement.quotas?.projects === 'number' ? profile.entitlement.quotas.projects : null,
                components: null,
                fmea_analyses: null,
                ai_generations: null,
                reports: null,
                exports: null,
              },
            }
          : undefined;
      setUser({ id: String(profile.id), email: profile.email || identity?.email || '',
        plan: profile.plan, username: profile.username, role: profile.role, entitlement });
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : 'Unable to load your account. Please try again.');
      localStorage.removeItem('token');
    } finally { setLoadingProfile(false); }
  }, [getAccessTokenSilently, identity?.email, isAuthenticated]);

  useEffect(() => {
    setCustomerTokenGetter(isAuthenticated ? getAccessTokenSilently : null);
    return () => setCustomerTokenGetter(null);
  }, [getAccessTokenSilently, isAuthenticated]);
  useEffect(() => { void refresh(); }, [refresh]);

  const value = useMemo<AuthContextType>(() => ({
    user,
    isAuthenticated: isAuthenticated && !!user,
    isLoading: isLoading || (!user && loadingProfile) || (isAuthenticated && !user && !error),
    error: error || authError?.message,
    login: async () => { await loginWithRedirect({ authorizationParams: { screen_hint: 'login' } }); },
    logout: () => {
      ['token', 'auth_token', 'jwt', 'userEmail', 'dev_login_email', 'user'].forEach(key => localStorage.removeItem(key));
      setCustomerTokenGetter(null);
      setUser(null);
      auth0Logout({ logoutParams: { returnTo: window.location.origin } });
    },
    refresh,
  }), [user, isAuthenticated, isLoading, loadingProfile, error, authError, loginWithRedirect, auth0Logout, refresh]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function CustomerAuthProvider({ children }: { children: React.ReactNode }) {
  const configurationError = customerAuthConfigurationError();
  if (configurationError) {
    return <div role="alert">{configurationError}</div>;
  }
  return <Auth0Provider
    domain={import.meta.env.VITE_AUTH0_DOMAIN}
    clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
    cacheLocation="memory"
    useRefreshTokens
    useRefreshTokensFallback
    authorizationParams={{ redirect_uri: window.location.origin, audience: import.meta.env.VITE_AUTH0_AUDIENCE, scope: 'openid profile email' }}
    onRedirectCallback={(appState) => {
      const path = appState?.returnTo;
      window.history.replaceState({}, '', typeof path === 'string' && path.startsWith('/') && !path.startsWith('//') ? path : '/dashboard');
      window.dispatchEvent(new PopStateEvent('popstate'));
    }}
  ><CustomerSession>{children}</CustomerSession></Auth0Provider>;
}
