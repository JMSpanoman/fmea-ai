import React, { useEffect, useRef } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

export default function CustomerLogin() {
  const { loginWithRedirect } = useAuth0();
  const started = useRef(false);
  useEffect(() => {
    if (window.location.pathname === '/create-account' && !started.current) {
      started.current = true;
      void loginWithRedirect({ authorizationParams: { screen_hint: 'signup' } });
    }
  }, [loginWithRedirect]);
  return <main className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
    <section className="max-w-md rounded-xl bg-white shadow p-8 text-center space-y-5">
      <h1 className="text-2xl font-semibold">SmartRisk 1</h1>
      <p>Try SmartRisk for 14 days with one user and one project. No card required. Your work stays in your account if you upgrade.</p>
      <button className="w-full rounded bg-blue-700 text-white p-3" onClick={() => void loginWithRedirect({ authorizationParams: { screen_hint: 'signup' } })}>Create account</button>
      <button className="w-full rounded border p-3" onClick={() => void loginWithRedirect()}>Sign in</button>
    </section>
  </main>;
}
