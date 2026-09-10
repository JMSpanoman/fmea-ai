import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { render } from '@testing-library/react';
import { RecommendedActionCard } from './RecommendedActionCard';
import { ProjectReadinessCard } from './ProjectReadinessCard';
import { TraceabilityHealthCard } from './TraceabilityHealthCard';
import { RiskOverviewCard } from './RiskOverviewCard';
import { selectTraceabilityHealth } from './model';
import { makeDocument } from './model/testFixtures';

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{`${location.pathname}${location.search}`}</div>;
}

describe('RecommendedActionCard', () => {
  it('navigates Continue to the traceability document', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={['/projects/proj-1/dashboard']}>
        <RecommendedActionCard
          primary={{
            id: 'complete-traceability-matrix',
            title: 'Complete the Traceability Matrix',
            reason: 'Traceability is not approved yet; gaps may exist.',
            cta: 'Continue',
            href: '/projects/proj-1/documents/tm-1',
            priority: 3,
          }}
          remaining={[]}
        />
        <LocationProbe />
      </MemoryRouter>
    );

    expect(screen.getByText('Complete the Traceability Matrix')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Continue' }));
    expect(screen.getByTestId('location')).toHaveTextContent('/projects/proj-1/documents/tm-1');
  });

  it('shows loading without fabricating an action', () => {
    render(
      <MemoryRouter>
        <RecommendedActionCard primary={null} remaining={[]} loading />
      </MemoryRouter>
    );
    expect(screen.getByText(/Loading recommended action/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument();
  });

  it('reveals remaining actions without replacing the primary CTA', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <RecommendedActionCard
          primary={{
            id: 'a',
            title: 'Complete the Traceability Matrix',
            reason: 'Traceability is not approved yet; gaps may exist.',
            cta: 'Continue',
            href: '/tm',
            priority: 3,
          }}
          remaining={[
            {
              id: 'b',
              title: 'Stale draft: FMEA',
              reason: 'Draft has not been updated in 40 days.',
              cta: 'Continue',
              href: '/fmea',
              priority: 4,
            },
          ]}
        />
      </MemoryRouter>
    );
    await user.click(screen.getByRole('button', { name: /View 1 other action/i }));
    expect(screen.getByText('Stale draft: FMEA')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'Continue' }).length).toBeGreaterThanOrEqual(1);
  });
});

describe('ProjectReadinessCard', () => {
  it('renders overall and category readiness with accessible text', () => {
    render(
      <ProjectReadinessCard
        availability="ready"
        readiness={{
          overallPct: 25,
          breakdown: [
            { name: 'Risk Management', pct: 0 },
            { name: 'Design Controls', pct: 100 },
            { name: 'V&V', pct: 0 },
            { name: 'Traceability', pct: 0 },
          ],
        }}
      />
    );
    expect(screen.getByLabelText('Overall readiness 25 percent')).toBeInTheDocument();
    expect(screen.getByLabelText('Design Controls 100 percent')).toBeInTheDocument();
    expect(screen.getByText('Risk Management')).toBeInTheDocument();
  });

  it('does not convert unavailable data to zero', () => {
    render(<ProjectReadinessCard readiness={null} availability="loading" />);
    expect(screen.getByText(/Loading readiness/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/Overall readiness/i)).not.toBeInTheDocument();
  });

  it('preserves error and empty states', () => {
    const { rerender } = render(<ProjectReadinessCard readiness={null} availability="error" />);
    expect(screen.getByText(/unavailable/i)).toBeInTheDocument();
    rerender(<ProjectReadinessCard readiness={null} availability="empty" />);
    expect(screen.getByText(/No documents available/i)).toBeInTheDocument();
  });
});

describe('TraceabilityHealthCard', () => {
  it('shows Not evaluated yet instead of Unknown', () => {
    const health = selectTraceabilityHealth([
      makeDocument({ id: 'tm', type: 'traceability_matrix', status: 'draft', content: 'x' }),
    ]);
    render(<TraceabilityHealthCard health={health} availability="ready" />);
    expect(screen.getAllByText('Not evaluated yet').length).toBeGreaterThanOrEqual(2);
    expect(screen.queryByText('Unknown')).not.toBeInTheDocument();
    expect(screen.getByText('Needs attention')).toBeInTheDocument();
  });
});

describe('RiskOverviewCard', () => {
  it('renders status counts on tinted surfaces', () => {
    render(
      <RiskOverviewCard
        availability="ready"
        counts={{ approved: 6, inReview: 0, draft: 24, notStarted: 0, total: 30 }}
      />
    );
    expect(screen.getByText('Approved')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();
    expect(screen.getByText('24')).toBeInTheDocument();
  });
});
