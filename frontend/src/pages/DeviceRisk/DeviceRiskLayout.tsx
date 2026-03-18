import React from 'react';
import { useParams, NavLink, Outlet } from 'react-router-dom';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';

const TABS = [
  { path: 'fmea', label: 'FMEA' },
  { path: 'hazard-analysis', label: 'Hazard Analysis' },
  { path: 'risk-traceability', label: 'Risk Traceability' },
  { path: 'residual-risk', label: 'Residual Risk' },
  { path: 'report', label: 'Report' },
] as const;

export default function DeviceRiskLayout() {
  const { id: deviceId } = useParams<{ id: string }>();

  if (!deviceId) {
    return (
      <div className="p-4">
        <p>Missing device.</p>
        <Button onClick={() => window.history.back()}>Back</Button>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <PageHeader
        title={`Device ${deviceId.slice(0, 8)}`}
        subtitle="Risk outputs for this device"
      />
      <div className="flex gap-2 mb-4">
        <Button variant="secondary" onClick={() => window.history.back()}>
          Back
        </Button>
      </div>
      <div className="flex flex-wrap gap-2 mb-4 border-b border-border pb-2">
        {TABS.map(({ path, label }) => (
          <NavLink
            key={path}
            to={path}
            end={path === 'fmea'}
            className={({ isActive }) =>
              `px-4 py-2 rounded-lg text-sm font-medium ${
                isActive
                  ? 'bg-primary text-white'
                  : 'bg-surface-secondary text-text-secondary hover:bg-surface-secondary/80'
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </div>
      <Outlet />
    </div>
  );
}
