import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';
import { API_BASE_URL, getCustomerAccessToken, setCustomerTokenGetter } from '../axios';
import { AuthContext, type AuthContextType, type User } from './AuthContext';

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
      setUser({ id: String(profile.id), email: identity?.email || profile.email || '',
        plan: profile.plan, username: profile.username, role: profile.role });
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
  return <Auth0Provider
    domain={import.meta.env.VITE_AUTH0_DOMAIN}
    clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
    authorizationParams={{ redirect_uri: window.location.origin, audience: import.meta.env.VITE_AUTH0_AUDIENCE, scope: 'openid profile email' }}
    onRedirectCallback={(appState) => {
      const path = appState?.returnTo;
      window.history.replaceState({}, '', typeof path === 'string' && path.startsWith('/') && !path.startsWith('//') ? path : '/dashboard');
      window.dispatchEvent(new PopStateEvent('popstate'));
    }}
  ><CustomerSession>{children}</CustomerSession></Auth0Provider>;
}
