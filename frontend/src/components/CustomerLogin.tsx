import React, { useEffect, useRef } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useAuth } from '../contexts/AuthContext';

export default function CustomerLogin() {
  const { loginWithRedirect, isAuthenticated } = useAuth0();
  const { error, logout, refresh } = useAuth();
  const started = useRef(false);
  const signIn = (signup = false) => {
    const invited = window.location.pathname === '/team/accept';
    if (invited) {
      const token = new URLSearchParams(window.location.hash.slice(1)).get('token');
      if (token) sessionStorage.setItem('sr1_invitation', token);
    }
    return loginWithRedirect({ appState: { returnTo: invited ? '/team/accept' : '/dashboard' },
      authorizationParams: { screen_hint: signup ? 'signup' : 'login', ...(isAuthenticated ? { prompt: 'login' } : {}) } });
  };
  useEffect(() => {
    if (window.location.pathname === '/create-account' && !started.current && !error) {
      started.current = true;
      void signIn(true);
    }
  }, [error]);
  return <main className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
    <section className="max-w-md rounded-xl bg-white shadow p-8 text-center space-y-5">
      <h1 className="text-2xl font-semibold">SmartRisk 1</h1>
      <p>Try SmartRisk for 14 days with one user and one project. No card required. Your work stays in your account if you upgrade.</p>
      {error && <p role="alert" className="text-red-700">{error}</p>}
      {isAuthenticated ? <>
        <button className="w-full rounded border p-3" onClick={() => void refresh()}>Try again</button>
        <button className="w-full rounded border p-3" onClick={() => void signIn()}>Sign in again</button>
        <button className="w-full rounded border p-3" onClick={logout}>Sign out</button>
      </> : <>
        <button className="w-full rounded bg-blue-700 text-white p-3" onClick={() => void signIn(true)}>Create account</button>
        <button className="w-full rounded border p-3" onClick={() => void signIn()}>Sign in</button>
      </>}
    </section>
  </main>;
}
