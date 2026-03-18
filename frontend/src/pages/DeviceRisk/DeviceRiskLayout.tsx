import React from 'react';
import { useParams, NavLink, Outlet } from 'react-router-dom';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';

const TABS = [
  { path: '', label: 'Overview', end: true },
  { path: 'components', label: 'Components', end: false },
  { path: 'risk-items', label: 'Risk Items', end: true },
] as const;

export default function DeviceRiskLayout() {
  const { id: deviceId } = useParams<{ id: string }>();

  if (!deviceId) {
    return (
      <div className="p-4 min-h-full" style={{ backgroundColor: '#f5f5f5', color: '#111' }}>
        <p className="text-gray-900">Missing device.</p>
        <Button onClick={() => window.history.back()}>Back</Button>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-7xl mx-auto min-h-full" style={{ backgroundColor: '#f5f5f5', color: '#111' }}>
      <PageHeader
        title={`Device ${deviceId.slice(0, 8)}`}
        subtitle="Overview, components, and risk items"
      />
      <div className="flex gap-2 mb-4">
        <Button variant="secondary" onClick={() => window.history.back()}>
          Back
        </Button>
      </div>
      <div className="flex flex-wrap gap-2 mb-4 border-b border-gray-300 pb-2">
        {TABS.map(({ path, label, end }) => (
          <NavLink
            key={path}
            to={path}
            end={end}
            className={({ isActive }) =>
              `px-4 py-2 rounded-lg text-sm font-medium ${
                isActive
                  ? 'bg-primary text-gray-900'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
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
