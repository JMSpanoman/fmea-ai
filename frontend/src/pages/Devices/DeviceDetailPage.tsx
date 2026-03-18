import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { devicesApi, DeviceRecord } from '../../services/devicesApi';

export default function DeviceDetailPage() {
  const { id: deviceId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [device, setDevice] = useState<DeviceRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!deviceId) return;
    setLoading(true);
    setError(null);
    devicesApi
      .getDevice(deviceId)
      .then(setDevice)
      .catch((e) => {
        console.error(e);
        setError('Failed to load device.');
      })
      .finally(() => setLoading(false));
  }, [deviceId]);

  if (!deviceId) return null;

  return (
    <>
      <div className="flex gap-2 mb-4">
        <Button variant="secondary" onClick={() => navigate('/devices')}>
          Back to devices
        </Button>
        {deviceId && (
          <Button variant="primary" onClick={() => navigate(`components`)}>
            View Components
          </Button>
        )}
      </div>
      {error && (
        <Card className="p-4 mb-4 border-red-200 text-red-800" style={{ backgroundColor: '#fef2f2' }}>
          {error}
        </Card>
      )}
      {loading ? (
        <Card className="p-8 text-center text-gray-600" style={{ backgroundColor: '#fff' }}>Loading…</Card>
      ) : !device ? (
        <Card className="p-8 text-center text-gray-600" style={{ backgroundColor: '#fff' }}>Device not found.</Card>
      ) : (
        <>
          <PageHeader
            title={device.name || deviceId.slice(0, 8)}
            subtitle="Device overview"
          />
          {device.description && (
            <Card className="p-4 mb-4" style={{ backgroundColor: '#fff' }}>
              <p className="whitespace-pre-wrap text-gray-900">{device.description}</p>
            </Card>
          )}
          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="p-4" style={{ backgroundColor: '#fff' }}>
              <h3 className="font-semibold text-gray-900 mb-2">Components</h3>
              <p className="text-sm text-gray-700 mb-3">
                View and manage components for this device. Use the <strong>Components</strong> tab above.
              </p>
              <Button variant="primary" size="sm" onClick={() => navigate('components')}>
                View components
              </Button>
            </Card>
            <Card className="p-4" style={{ backgroundColor: '#fff' }}>
              <h3 className="font-semibold text-gray-900 mb-2">Risk Items</h3>
              <p className="text-sm text-gray-700 mb-3">
                FMEA, hazard analysis, traceability, residual risk, and report. Use the <strong>Risk Items</strong> tab above.
              </p>
              <Button variant="secondary" size="sm" onClick={() => navigate('risk-items')}>
                View risk items
              </Button>
            </Card>
          </div>
        </>
      )}
    </>
  );
}
