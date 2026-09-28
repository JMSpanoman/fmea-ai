import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';
import { API_BASE_URL, setCustomerTokenGetter } from '../axios';
import { AuthContext, type AuthContextType, type User } from './AuthContext';

function CustomerSession({ children }: { children: React.ReactNode }) {
  const { user: identity, isAuthenticated, isLoading, getAccessTokenSilently, loginWithRedirect, logout: auth0Logout } = useAuth0();
  const [user, setUser] = useState<User | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(false);

  const refresh = useCallback(async () => {
    if (!isAuthenticated) { setUser(null); return; }
    setLoadingProfile(true);
    try {
      const token = await getAccessTokenSilently();
      // Some older SR1 fetch callers still read this key. Replace them with the
      // SDK token getter before enabling customer sign-in on Render.
      localStorage.setItem('token', token);
      const response = await fetch(`${API_BASE_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) throw new Error(`Account unavailable (${response.status})`);
      const profile = await response.json();
      setUser({ id: String(profile.id), email: identity?.email || profile.email || '',
        plan: profile.plan, username: profile.username, role: profile.role });
    } catch {
      setUser(null);
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
    isLoading: isLoading || loadingProfile,
    login: async () => { await loginWithRedirect({ authorizationParams: { screen_hint: 'login' } }); },
    logout: () => {
      localStorage.removeItem('token');
      setUser(null);
      auth0Logout({ logoutParams: { returnTo: window.location.origin } });
    },
    refresh,
  }), [user, isAuthenticated, isLoading, loadingProfile, loginWithRedirect, auth0Logout, refresh]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function CustomerAuthProvider({ children }: { children: React.ReactNode }) {
  return <Auth0Provider
    domain={import.meta.env.VITE_AUTH0_DOMAIN}
    clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
    authorizationParams={{ redirect_uri: window.location.origin, audience: import.meta.env.VITE_AUTH0_AUDIENCE }}
  ><CustomerSession>{children}</CustomerSession></Auth0Provider>;
}
