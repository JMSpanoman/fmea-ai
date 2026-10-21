import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import { CustomerAuthProvider, SR1_API_AUDIENCE, SR1_CALLBACK_ORIGINS, customerAuthConfigurationError } from './CustomerAuthProvider';
import { useAuth } from './AuthContext';

const auth0 = vi.hoisted(() => ({
  getAccessTokenSilently: vi.fn(async () => 'access-token'),
  loginWithRedirect: vi.fn(),
  logout: vi.fn(),
}));

vi.mock('@auth0/auth0-react', () => ({
  Auth0Provider: ({ children }: { children: React.ReactNode }) => children,
  useAuth0: () => ({
    user: { email: 'typed@example.com' },
    isAuthenticated: true,
    isLoading: false,
    error: undefined,
    getAccessTokenSilently: auth0.getAccessTokenSilently,
    loginWithRedirect: auth0.loginWithRedirect,
    logout: auth0.logout,
  }),
}));

vi.mock('../axios', () => ({
  API_BASE_URL: '/api',
  customerAuthEnabled: true,
  getCustomerAccessToken: vi.fn(async () => 'access-token'),
  setCustomerTokenGetter: vi.fn(),
}));

function Label() {
  const { user } = useAuth();
  return <div>{user?.entitlement?.unlimited ? user.entitlement.label : user?.plan}</div>;
}

describe('CustomerAuthProvider entitlement', () => {
  beforeEach(() => {
    localStorage.setItem('userEmail', 'john@fotonconsulting.com');
    localStorage.setItem('entitlement', JSON.stringify({ unlimited: true }));
  });

  test('keeps the backend unlimited entitlement instead of the Auth0 profile email or browser storage', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({
      ok: true,
      json: async () => ({
        id: 'owner-row',
        email: 'john@fotonconsulting.com',
        plan: 'pro',
        entitlement: {
          unlimited: true,
          permanent: true,
          label: 'Owner — Unlimited',
          quotas: { projects: null, components: null, fmea_analyses: null, ai_generations: null, reports: null, exports: null },
        },
      }),
    })));
    render(<CustomerAuthProvider><Label /></CustomerAuthProvider>);
    expect(await screen.findByText('Owner — Unlimited')).toBeVisible();
    expect(screen.queryByText('typed@example.com')).toBeNull();
  });

  test('does not invent unlimited access when the backend entitlement is absent', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({
      ok: true,
      json: async () => ({ id: 'other', email: 'other@example.com', plan: 'lite' }),
    })));
    render(<CustomerAuthProvider><Label /></CustomerAuthProvider>);
    expect(await screen.findByText('lite')).toBeVisible();
    await waitFor(() => expect(screen.queryByText('Owner — Unlimited')).toBeNull());
  });

  test('requires the SR1 audience and registered callback origins outside localhost', () => {
    expect(SR1_API_AUDIENCE).toBe('https://smartrisk.fotonconsulting.com/api');
    expect(SR1_CALLBACK_ORIGINS).toEqual([
      'https://fmea-frontend-dczh.onrender.com',
      'https://sr1-sandbox-frontend-dczh.onrender.com',
    ]);
    vi.stubEnv('VITE_AUTH0_DOMAIN', 'dev-dsf588bqn08hhddj.us.auth0.com');
    vi.stubEnv('VITE_AUTH0_CLIENT_ID', 'public-client');
    vi.stubEnv('VITE_AUTH0_AUDIENCE', 'https://wrong.example/api');
    expect(customerAuthConfigurationError('https://fmea-frontend-dczh.onrender.com')).toMatch(/audience/);
    vi.stubEnv('VITE_AUTH0_AUDIENCE', SR1_API_AUDIENCE);
    expect(customerAuthConfigurationError('https://unknown.example')).toMatch(/callback/);
    expect(customerAuthConfigurationError('https://fmea-frontend-dczh.onrender.com')).toBeNull();
  });
});
