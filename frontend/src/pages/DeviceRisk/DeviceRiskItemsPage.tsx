import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

export default function DeviceRiskItemsPage() {
  const { id: deviceId } = useParams<{ id: string }>();

  if (!deviceId) return null;

  const links = [
    { to: 'fmea', label: 'FMEA' },
    { to: 'hazard-analysis', label: 'Hazard Analysis' },
    { to: 'risk-traceability', label: 'Risk Traceability' },
    { to: 'residual-risk', label: 'Residual Risk' },
    { to: 'report', label: 'Report' },
  ];

  return (
    <>
      <h2 className="text-lg font-semibold mb-3 text-gray-900">Risk Items</h2>
      <Card className="p-4" style={{ backgroundColor: '#fff' }}>
        <p className="text-sm text-gray-700 mb-4">
          View and export risk outputs for this device: FMEA, hazard analysis, traceability, residual risk, and generated report.
        </p>
        <div className="flex flex-wrap gap-2">
          {links.map(({ to, label }) => (
            <Link key={to} to={`/devices/${deviceId}/${to}`}>
              <Button variant="secondary" size="sm">{label}</Button>
            </Link>
          ))}
        </div>
      </Card>
    </>
  );
}
