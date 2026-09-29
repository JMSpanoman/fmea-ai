import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../axios';
import { useAuth } from '../contexts/AuthContext';

type BillingStatus = { plan: string; subscription_status: string | null; trial_ends_at: string | null;
  is_billing_owner: boolean; has_billing_account: boolean };
export default function BillingPage() {
  const { user, refresh } = useAuth();
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [checking, setChecking] = useState(false);
  const [accessMessage, setAccessMessage] = useState('');
  const [error, setError] = useState('');
  const checkRequest = useRef<Promise<boolean> | null>(null);
  const manualCheckPending = useRef(false);
  const success = window.location.pathname.endsWith('/success');
  const cancelled = window.location.pathname.endsWith('/cancel');
  const check = useCallback(() => {
    if (checkRequest.current) return checkRequest.current;
    const request = (async () => {
      const { data } = await api.get<BillingStatus>('/billing/status', { timeout: 15000 });
      setStatus(data);
      // Refresh account entitlements only when they changed. Refreshing on every
      // active response can repeatedly reload auth consumers after payment.
      if (data.plan !== user?.plan) await refresh();
      return data.subscription_status === 'active';
    })().finally(() => {
      if (checkRequest.current === request) checkRequest.current = null;
    });
    checkRequest.current = request;
    return request;
  }, [refresh, user?.plan]);
  const checkAccess = useCallback(async () => {
    if (manualCheckPending.current) return;
    manualCheckPending.current = true;
    setChecking(true); setError(''); setAccessMessage('');
    try {
      await check();
      setAccessMessage('Access check complete.');
    } catch {
      setError('Unable to check your subscription. Please try again.');
    } finally {
      manualCheckPending.current = false;
      setChecking(false);
    }
  }, [check]);
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
  useEffect(() => {
    const onPageShow = (event: PageTransitionEvent) => {
      if (!event.persisted) return;
      // Safari can restore the page exactly as it was while opening Stripe.
      setBusy(false);
      void checkAccess();
    };
    window.addEventListener('pageshow', onPageShow);
    return () => window.removeEventListener('pageshow', onPageShow);
  }, [checkAccess]);
  const action = async (path: string, interval?: 'monthly' | 'yearly') => {
    setBusy(true); setError('');
    try {
      const { data } = await api.post(path, interval ? { interval } : {});
      const url = new URL(data.url);
      if (url.protocol !== 'https:' || !['checkout.stripe.com', 'billing.stripe.com'].includes(url.hostname)) throw new Error('Billing page unavailable');
      window.location.assign(url.href);
    } catch (err: any) {
      setError(typeof err?.response?.data?.detail === 'string' ? err.response.data.detail : 'Unable to open billing. Please try again.');
    } finally { setBusy(false); }
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
        <p>Prices exclude VAT.</p>
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
    <button type="button" disabled={checking} aria-busy={checking} onClick={() => void checkAccess()} className="rounded border border-blue-700 bg-white p-3 text-blue-800 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 disabled:cursor-wait disabled:opacity-60">{checking ? 'Checking access…' : 'Check access'}</button>
    {accessMessage && <p role="status" className="text-green-800">{accessMessage}</p>}
  </section>;
}
