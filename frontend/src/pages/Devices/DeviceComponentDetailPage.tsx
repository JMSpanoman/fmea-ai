import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { devicesApi, DeviceComponentRecord } from '../../services/devicesApi';
import { componentsApi } from '../../services/apiPhase1';

export default function DeviceComponentDetailPage() {
  const { id: deviceId, componentId } = useParams<{ id: string; componentId: string }>();
  const navigate = useNavigate();
  const [component, setComponent] = useState<DeviceComponentRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [generateMessage, setGenerateMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!deviceId || !componentId) return;
    setLoading(true);
    setError(null);
    devicesApi
      .getDeviceComponent(deviceId, componentId)
      .then(setComponent)
      .catch((e) => {
        console.error(e);
        setError('Failed to load component.');
      })
      .finally(() => setLoading(false));
  }, [deviceId, componentId]);

  const handleGenerateRiskSuggestions = async () => {
    if (!component?.project_id || !componentId) return;
    setGenerateLoading(true);
    setGenerateMessage(null);
    try {
      const res = await componentsApi.generateRiskSuggestions(component.project_id, componentId);
      setGenerateMessage(`Generated ${res.created} suggestion(s). You can review and accept them in the project.`);
    } catch (e) {
      console.error(e);
      setGenerateMessage('Failed to generate risk suggestions.');
    } finally {
      setGenerateLoading(false);
    }
  };

  if (!deviceId || !componentId) return null;

  const attrs = component?.attributes ?? {};
  const functionsList = component?.functions ?? [];
  const interfacesList = component?.interfaces ?? [];
  const hasAttrs = Object.keys(attrs).length > 0;
  const hasFunctions = functionsList.length > 0;
  const hasInterfaces = interfacesList.length > 0;

  return (
    <>
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Button
          variant="secondary"
          onClick={() => navigate(`/devices/${deviceId}/components`)}
        >
          Back to components
        </Button>
        {component?.project_id && (
          <Button
            variant="primary"
            onClick={handleGenerateRiskSuggestions}
            disabled={generateLoading}
          >
            {generateLoading ? 'Generating…' : 'Generate Risk Suggestions'}
          </Button>
        )}
      </div>
      {generateMessage && (
        <Card
          className={`p-4 mb-4 border ${generateMessage.startsWith('Failed') ? 'border-red-200 text-red-800' : 'border-green-200 text-green-800'}`}
          style={{ backgroundColor: generateMessage.startsWith('Failed') ? '#fef2f2' : '#f0fdf4' }}
        >
          {generateMessage}
        </Card>
      )}
      {error && (
        <Card className="p-4 mb-4 border-red-200 text-red-800" style={{ backgroundColor: '#fef2f2' }}>
          {error}
        </Card>
      )}
      {loading ? (
        <Card className="p-8 text-center text-gray-600" style={{ backgroundColor: '#fff' }}>Loading…</Card>
      ) : !component ? (
        <Card className="p-8 text-center text-gray-600" style={{ backgroundColor: '#fff' }}>Component not found.</Card>
      ) : (
        <>
          <PageHeader
            title={component.component_name}
            subtitle={`Component · ${component.risk_items_count ?? 0} risk item(s) for this device`}
          />

          <Card className="p-4 mb-4" style={{ backgroundColor: '#fff' }}>
            <h3 className="font-semibold text-gray-900 mb-2">Type</h3>
            <p className="text-gray-900">{component.component_type || '—'}</p>
          </Card>

          {hasAttrs && (
            <Card className="p-4 mb-4" style={{ backgroundColor: '#fff' }}>
              <h3 className="font-semibold text-gray-900 mb-2">Attributes</h3>
              <dl className="grid gap-2 text-sm">
                {Object.entries(attrs).map(([key, value]) => (
                  <div key={key}>
                    <dt className="text-gray-600">{key.replace(/_/g, ' ')}</dt>
                    <dd className="text-gray-900">
                      {typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value)}
                    </dd>
                  </div>
                ))}
              </dl>
            </Card>
          )}

          {hasFunctions && (
            <Card className="p-4 mb-4" style={{ backgroundColor: '#fff' }}>
              <h3 className="font-semibold text-gray-900 mb-2">Functions</h3>
              <ul className="list-disc list-inside text-gray-900 text-sm space-y-1">
                {functionsList.map((fn, i) => (
                  <li key={i}>
                    {typeof fn === 'object' && fn !== null ? JSON.stringify(fn) : String(fn)}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {hasInterfaces && (
            <Card className="p-4 mb-4" style={{ backgroundColor: '#fff' }}>
              <h3 className="font-semibold text-gray-900 mb-2">Interfaces</h3>
              <ul className="list-disc list-inside text-gray-900 text-sm space-y-1">
                {interfacesList.map((iface, i) => (
                  <li key={i}>
                    {typeof iface === 'object' && iface !== null ? JSON.stringify(iface) : String(iface)}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          <Card className="p-4" style={{ backgroundColor: '#fff' }}>
            <h3 className="font-semibold text-gray-900 mb-2">Details</h3>
            <dl className="grid gap-2 text-sm">
              <div>
                <dt className="text-gray-600">Critical to essential performance</dt>
                <dd className="text-gray-900">{component.critical_to_essential_performance || '—'}</dd>
              </div>
              <div>
                <dt className="text-gray-600">ID</dt>
                <dd className="font-mono text-gray-900">{component.id}</dd>
              </div>
              <div>
                <dt className="text-gray-600">Risk items (this device)</dt>
                <dd className="text-gray-900">{component.risk_items_count ?? 0}</dd>
              </div>
            </dl>
          </Card>
        </>
      )}
    </>
  );
}
