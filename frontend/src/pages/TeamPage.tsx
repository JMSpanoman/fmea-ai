import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../axios';
import { useAuth } from '../contexts/AuthContext';

type Team = { is_owner: boolean; seat_limit: number;
  members: { id: string; email: string; is_owner: boolean }[];
  invitations: { id: string; email: string; expires_at: string }[] };
const detail = (error: any) => typeof error?.response?.data?.detail === 'string' ? error.response.data.detail : 'Unable to update your team. Please try again.';

export default function TeamPage() {
  const { refresh } = useAuth();
  const [team, setTeam] = useState<Team | null>(null);
  const [email, setEmail] = useState('');
  const [link, setLink] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [joined, setJoined] = useState(false);
  const accepting = window.location.pathname === '/team/accept';
  const [token] = useState(() => new URLSearchParams(window.location.hash.slice(1)).get('token') || sessionStorage.getItem('sr1_invitation') || '');
  const load = async () => { const { data } = await api.get('/team'); setTeam(data); };
  useEffect(() => { void load().catch(e => setError(detail(e))); }, []);
  const run = async (action: () => Promise<void>) => {
    setBusy(true); setError('');
    try { await action(); await load(); } catch (e) { setError(detail(e)); } finally { setBusy(false); }
  };
  return <section className="mx-auto max-w-3xl p-8 space-y-6">
    <h1 className="text-3xl font-semibold">Your SmartRisk team</h1>
    {error && <p role="alert" className="text-red-700">{error}</p>}
    {accepting && !joined && <div className="rounded border p-5 space-y-3">
      <h2 className="text-xl font-semibold">Join an invited team</h2>
      <p>Sign in with the invited email address. You will share the team’s projects and three-project allowance. Your personal trial project stays with your account and is hidden while you are on the team.</p>
      <button disabled={busy || !token} className="rounded bg-blue-700 text-white p-3 disabled:opacity-50" onClick={() => void run(async () => {
        await api.post('/team/accept', { token }); sessionStorage.removeItem('sr1_invitation');
        window.history.replaceState({}, '', '/team/accept'); setJoined(true); await refresh();
      })}>Accept invitation</button>
      {!token && <p>Open the invitation link from your team owner to continue.</p>}
    </div>}
    {joined && <p role="status">You have joined the team. <Link to="/projects" className="underline">Open shared projects</Link></p>}
    {team && <>
      <p>{team.members.length} of {team.seat_limit} seats used. {team.invitations.length} reserved by pending invitations.</p>
      <ul className="divide-y border rounded">{team.members.map(member => <li key={member.id} className="p-4 flex flex-wrap gap-3 justify-between">
        <span>{member.email}{member.is_owner ? ' · Owner' : ''}</span>
        {team.is_owner && !member.is_owner && <button disabled={busy} className="text-red-700 underline" onClick={() => void run(async () => { await api.delete(`/team/members/${member.id}`); })}>Remove access</button>}
      </li>)}</ul>
      {team.is_owner && <>
        <form className="space-y-3 border rounded p-5" onSubmit={event => { event.preventDefault(); void run(async () => {
          const { data } = await api.post('/team/invitations', { email });
          setLink(`${window.location.origin}/team/accept#token=${encodeURIComponent(data.token)}`); setEmail('');
        }); }}>
          <label className="block font-semibold" htmlFor="invite-email">Invite a team member</label>
          <p>An active Team subscription includes you and four members. Invitations expire in seven days.</p>
          <input id="invite-email" type="email" required value={email} onChange={e => setEmail(e.target.value)} className="border rounded p-3 w-full" placeholder="colleague@company.com" />
          <button disabled={busy || team.members.length + team.invitations.length >= 5} className="rounded bg-blue-700 text-white p-3 disabled:opacity-50">Create invitation link</button>
        </form>
        {link && <label className="block space-y-2">Copy and share this invitation link. It is shown only now; no email has been sent.
          <input aria-label="Invitation link" readOnly value={link} onFocus={e => e.target.select()} className="border rounded p-3 w-full" />
        </label>}
        {team.invitations.length > 0 && <section className="space-y-3"><h2 className="font-semibold">Pending invitations</h2>
          {team.invitations.map(invite => <div key={invite.id} className="flex flex-wrap justify-between gap-3 border p-3 rounded">
            <span>{invite.email}</span><button disabled={busy} className="underline" onClick={() => void run(async () => { await api.delete(`/team/invitations/${invite.id}`); setLink(''); })}>Revoke invitation</button>
          </div>)}
        </section>}
      </>}
    </>}
    <Link to="/billing" className="underline">Plans and billing</Link>
  </section>;
}
