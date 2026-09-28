import React, { useState } from 'react';
import api from '../axios';
import { useAuth } from '../contexts/AuthContext';

export default function BillingPage() {
  const { user, refresh } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const action = async (path: string, interval?: 'monthly' | 'yearly') => {
    setBusy(true); setError('');
    try {
      const { data } = await api.post(path, interval ? { interval } : {});
      if (!data?.url || !String(data.url).startsWith('https://')) throw new Error('Billing page unavailable');
      window.location.assign(data.url);
    } catch { setError('Billing is being prepared. Please contact us for help upgrading.'); setBusy(false); }
  };
  const success = window.location.pathname.endsWith('/success');
  const cancelled = window.location.pathname.endsWith('/cancel');
  return <main className="mx-auto max-w-4xl p-8 space-y-7">
    <h1 className="text-3xl font-semibold">SmartRisk 1 plans</h1>
    {success && <p role="status">Stripe is confirming your subscription. Your access updates after payment confirmation.</p>}
    {cancelled && <p role="status">Checkout was cancelled. Your saved work is still here.</p>}
    <div className="grid gap-5 md:grid-cols-2">
      <section className="rounded border p-6 space-y-3"><h2 className="text-xl font-semibold">Try SmartRisk 1</h2>
        <p>Free for 14 days. No card required.</p><p>One user and one project. Your saved work remains in your account when you upgrade.</p></section>
      <section className="rounded border p-6 space-y-3"><h2 className="text-xl font-semibold">Team</h2>
        <p>Five users and three active projects.</p><p>€399 per month or €3,990 per year.</p>
        <div className="flex flex-wrap gap-3">
          <button disabled={busy} onClick={() => void action('/billing/checkout', 'monthly')} className="rounded bg-blue-700 p-3 text-white disabled:opacity-50">Choose monthly</button>
          <button disabled={busy} onClick={() => void action('/billing/checkout', 'yearly')} className="rounded border p-3 disabled:opacity-50">Choose yearly</button>
        </div></section>
    </div>
    {user?.plan === 'pro' && <button disabled={busy} onClick={() => void action('/billing/portal')} className="rounded border p-3">Manage subscription</button>}
    <p>Need a guided evaluation? Ask us about a 30-day pilot by quote.</p>
    {error && <p role="alert" className="text-red-700">{error}</p>}
    {success && <button onClick={() => void refresh()} className="rounded border p-3">Check access</button>}
  </main>;
}
