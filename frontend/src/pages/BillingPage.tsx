import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../axios';
import { useAuth } from '../contexts/AuthContext';

type BillingStatus = { plan: string; subscription_status: string | null; trial_ends_at: string | null;
  is_billing_owner: boolean; has_billing_account: boolean };
export default function BillingPage() {
  const { refresh } = useAuth();
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const success = window.location.pathname.endsWith('/success');
  const cancelled = window.location.pathname.endsWith('/cancel');
  const check = useCallback(async () => {
    const { data } = await api.get<BillingStatus>('/billing/status'); setStatus(data);
    if (data.subscription_status === 'active') await refresh();
    return data.subscription_status === 'active';
  }, [refresh]);
  useEffect(() => {
    let stopped = false; let timer: ReturnType<typeof setTimeout>;
    let attempts = 0;
    const poll = async () => {
      try {
        const active = await check(); attempts += 1;
        if (success && !active && !stopped && attempts < 12) timer = setTimeout(() => void poll(), 2500);
      } catch { if (!stopped) setError('Unable to check your subscription. Please try again.'); }
    };
    void poll();
    return () => { stopped = true; clearTimeout(timer); };
  }, [check, success]);
  const action = async (path: string, interval?: 'monthly' | 'yearly') => {
    setBusy(true); setError('');
    try {
      const { data } = await api.post(path, interval ? { interval } : {});
      const url = new URL(data.url);
      if (url.protocol !== 'https:' || !['checkout.stripe.com', 'billing.stripe.com'].includes(url.hostname)) throw new Error('Billing page unavailable');
      window.location.assign(url.href);
    } catch (err: any) {
      setError(typeof err?.response?.data?.detail === 'string' ? err.response.data.detail : 'Unable to open billing. Please try again.'); setBusy(false);
    }
  };
  const canCheckout = !!status?.is_billing_owner && !['active', 'trialing', 'past_due', 'unpaid', 'incomplete', 'paused'].includes(status.subscription_status || '');
  return <section className="mx-auto max-w-4xl p-8 space-y-7">
    <h1 className="text-3xl font-semibold">SmartRisk 1 plans</h1>
    {success && <p role="status">{status?.subscription_status === 'active' ? 'Your Team subscription is active. Your saved work is ready.' : 'Waiting for payment confirmation. Access updates after Stripe confirms payment. If confirmation takes longer, check access again below.'}</p>}
    {cancelled && <p role="status">Checkout was cancelled. Your saved work is still here.</p>}
    {status && <div className="rounded bg-blue-50 p-4 space-y-2">
      <p>Subscription: {status.subscription_status || 'No paid subscription'}.</p>
      {!status.subscription_status && status.trial_ends_at && <p>Trial {status.plan === 'pro' ? 'ends' : 'ended'} {new Date(status.trial_ends_at.endsWith('Z') || /[+-]\d\d:\d\d$/.test(status.trial_ends_at) ? status.trial_ends_at : `${status.trial_ends_at}Z`).toLocaleDateString()}.</p>}
      {['past_due', 'unpaid', 'incomplete'].includes(status.subscription_status || '') && <p>Payment needs attention. {status.is_billing_owner ? 'Open Manage subscription to update payment details.' : 'Ask your team owner to update payment details.'}</p>}
      {!status.is_billing_owner && <p>Your team owner manages this subscription.</p>}
    </div>}
    <div className="grid gap-5 md:grid-cols-2">
      <section className="rounded border p-6 space-y-3"><h2 className="text-xl font-semibold">Try SmartRisk 1</h2>
        <p>Free for 14 days. No card required.</p><p>One user and one project. Your saved work remains in your account when you upgrade.</p></section>
      <section className="rounded border p-6 space-y-3"><h2 className="text-xl font-semibold">Team</h2>
        <p>Five users and three active projects.</p><p>€399 per month or €3,990 per year.</p>
        <p>Renews automatically. Cancel future renewals in Manage subscription; access continues until the paid period ends.</p>
        {canCheckout && <div className="flex flex-wrap gap-3">
          <button disabled={busy} onClick={() => void action('/billing/checkout', 'monthly')} className="rounded bg-blue-700 p-3 text-white disabled:opacity-50">Choose monthly</button>
          <button disabled={busy} onClick={() => void action('/billing/checkout', 'yearly')} className="rounded border p-3 disabled:opacity-50">Choose yearly</button>
        </div>}</section>
    </div>
    {status?.is_billing_owner && status.has_billing_account && <button disabled={busy} onClick={() => void action('/billing/portal')} className="rounded border p-3">Manage subscription</button>}
    <p><Link to="/team" className="underline">Manage team</Link> · <Link to="/projects" className="underline">Open projects</Link></p>
    <p>Need a guided evaluation? <a href="https://www.fotonconsulting.com/platform/smartrisk-1" className="underline">Ask us about a 30-day pilot by quote.</a></p>
    {error && <p role="alert" className="text-red-700">{error}</p>}
    <button disabled={busy} onClick={() => { setError(''); void check().catch(() => setError('Unable to check your subscription. Please try again.')); }} className="rounded border p-3">Check access</button>
  </section>;
}
