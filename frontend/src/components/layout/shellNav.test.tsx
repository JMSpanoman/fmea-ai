import React from 'react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { render } from '@testing-library/react';
import { PrimaryNavigation } from './PrimaryNavigation';
import { DocumentLibraryNav } from './DocumentLibraryNav';
import { AppSidebar } from './AppSidebar';
import { AppHeader } from './AppHeader';

const logout = vi.fn();

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 'user-1',
      email: 'secret.user@example.com',
      name: 'Pat Analyst',
      plan: 'pro',
    },
    logout,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    refresh: vi.fn(),
  }),
}));

vi.mock('../../contexts/ProjectContext', () => ({
  useProject: () => ({
    currentProject: {
      id: '11111111-2222-3333-4444-555555555555',
      name: 'Pacemaker V&V Demo',
    },
    setCurrentProject: vi.fn(),
    isProjectSelected: true,
    clearCurrentProject: vi.fn(),
    updateCurrentProject: vi.fn(),
  }),
}));

vi.mock('../../services/projectService', () => ({
  default: {
    getProjects: vi.fn().mockResolvedValue([
      { id: '11111111-2222-3333-4444-555555555555', name: 'Pacemaker V&V Demo' },
    ]),
  },
}));

function wrap(ui: React.ReactElement, route = '/projects/11111111-2222-3333-4444-555555555555/dashboard') {
  return render(<MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>);
}

describe('PrimaryNavigation', () => {
  it('renders the simplified destinations and marks the active page', () => {
    wrap(<PrimaryNavigation />);
    expect(screen.getByRole('button', { name: 'Dashboard' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('button', { name: 'Projects' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Documents' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Traceability' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Actions' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reports' })).toBeInTheDocument();
  });
});

describe('DocumentLibraryNav', () => {
  it('expands existing documentation groups and keeps current routes', async () => {
    const user = userEvent.setup();
    wrap(<DocumentLibraryNav />);
    await user.click(screen.getByRole('button', { name: 'Document library' }));
    expect(screen.getByRole('button', { name: 'Risk Management Core' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Regulatory & Audit Outputs' })).toBeInTheDocument();
  });
});

describe('AppSidebar', () => {
  it('opens an accessible mobile drawer that closes with Escape', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    wrap(<AppSidebar mobileOpen onClose={onClose} />);
    expect(screen.getByRole('dialog', { name: 'Navigation' })).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();
  });
});

describe('AppHeader', () => {
  beforeEach(() => {
    logout.mockReset();
  });

  it('shows the project name without the UUID or user email', () => {
    wrap(<AppHeader onOpenNavigation={() => undefined} />);
    expect(screen.getByLabelText('Current project: Pacemaker V&V Demo')).toBeInTheDocument();
    expect(screen.queryByText(/11111111-2222-3333-4444-555555555555/)).not.toBeInTheDocument();
    expect(screen.queryByText('secret.user@example.com')).not.toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'Account menu' })).toHaveLength(1);
    expect(screen.getByRole('button', { name: 'Open navigation', hidden: true })).toBeInTheDocument();
  });
});
