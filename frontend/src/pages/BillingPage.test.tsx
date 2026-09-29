import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, expect, test, vi } from 'vitest';
import BillingPage from './BillingPage';
import TeamPage from './TeamPage';

const mocks = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), del: vi.fn(), refresh: vi.fn() }));
vi.mock('../axios', () => ({ default: { get: mocks.get, post: mocks.post, delete: mocks.del } }));
vi.mock('../contexts/AuthContext', () => ({ useAuth: () => ({ refresh: mocks.refresh }) }));
const status = { plan: 'pro', subscription_status: null, trial_ends_at: '2026-10-13T12:00:00Z', is_billing_owner: true, has_billing_account: false };

beforeEach(() => {
  vi.clearAllMocks();
  sessionStorage.clear();
  window.history.replaceState({}, '', '/billing');
  mocks.get.mockResolvedValue({ data: status });
});
const show = (component: React.ReactNode) => render(<MemoryRouter>{component}</MemoryRouter>);

test('trial account sees EUR prices and a checkout failure preserves the page', async () => {
  mocks.post.mockRejectedValue({ response: { data: { detail: 'Billing is not configured' } } });
  show(<BillingPage />);
  fireEvent.click(await screen.findByRole('button', { name: 'Choose monthly' }));
  expect(mocks.post).toHaveBeenCalledWith('/billing/checkout', { interval: 'monthly' });
  expect(await screen.findByRole('alert')).toHaveTextContent('Billing is not configured');
  expect(screen.getByText('€399 per month or €3,990 per year.')).toBeVisible();
});

test('past-due owner can reach portal and cannot buy a second subscription', async () => {
  mocks.get.mockResolvedValue({ data: { ...status, plan: 'lite', subscription_status: 'past_due', has_billing_account: true } });
  show(<BillingPage />);
  expect(await screen.findByRole('button', { name: 'Manage subscription' })).toBeVisible();
  expect(screen.queryByRole('button', { name: 'Choose monthly' })).toBeNull();
});

test('team members cannot see checkout or portal controls', async () => {
  mocks.get.mockResolvedValue({ data: { ...status, subscription_status: 'active', is_billing_owner: false, has_billing_account: true } });
  show(<BillingPage />);
  await screen.findByText('Your team owner manages this subscription.');
  expect(screen.queryByRole('button', { name: 'Manage subscription' })).toBeNull();
  expect(screen.queryByRole('button', { name: 'Choose monthly' })).toBeNull();
});

test('success URL alone does not say payment succeeded', async () => {
  window.history.replaceState({}, '', '/billing/success');
  show(<BillingPage />);
  await screen.findByText('Subscription: No paid subscription.');
  expect(screen.getByRole('status')).toHaveTextContent('Waiting for payment confirmation');
});

test('invitation survives the signup redirect and is consumed only on success', async () => {
  window.history.replaceState({}, '', '/team/accept');
  sessionStorage.setItem('sr1_invitation', 'test-invitation-token');
  mocks.get.mockResolvedValue({ data: { is_owner: false, seat_limit: 5, members: [], invitations: [] } });
  mocks.post.mockResolvedValue({ data: { owner_id: 'owner' } });
  show(<TeamPage />);
  fireEvent.click(screen.getByRole('button', { name: 'Accept invitation' }));
  await waitFor(() => expect(mocks.post).toHaveBeenCalledWith('/team/accept', { token: 'test-invitation-token' }));
  expect(await screen.findByRole('status')).toHaveTextContent('You have joined the team');
  expect(sessionStorage.getItem('sr1_invitation')).toBeNull();
});
