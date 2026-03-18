import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { DataTable } from '../../components/ui/DataTable';
import { devicesApi, DeviceComponentRecord } from '../../services/devicesApi';
import { componentsApi } from '../../services/apiPhase1';

export default function DeviceComponentsPage() {
  const { id: deviceId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [components, setComponents] = useState<DeviceComponentRecord[]>([]);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createDescription, setCreateDescription] = useState('');
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const loadData = () => {
    if (!deviceId) return;
    setLoading(true);
    setError(null);
    Promise.all([
      devicesApi.getDevice(deviceId),
      devicesApi.getDeviceComponents(deviceId),
    ])
      .then(([device, comps]) => {
        setProjectId(device.project_id);
        setComponents(comps);
      })
      .catch((e) => {
        console.error(e);
        setError('Failed to load components.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [deviceId]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !createName.trim()) return;
    setCreateSubmitting(true);
    setCreateError(null);
    try {
      await componentsApi.create(projectId, {
        name: createName.trim(),
        description: createDescription.trim() || undefined,
      });
      setCreateOpen(false);
      setCreateName('');
      setCreateDescription('');
      loadData();
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create component.');
    } finally {
      setCreateSubmitting(false);
    }
  };

  if (!deviceId) return null;

  return (
    <>
      <div className="flex items-center justify-between gap-4 mb-3">
        <h2 className="text-lg font-semibold text-gray-900">Components</h2>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => navigate(`/devices/${deviceId}`)}>
            Back to device
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setCreateOpen(true)}
            disabled={!projectId}
          >
            Create Component
          </Button>
        </div>
      </div>
      {error && (
        <Card className="p-4 mb-4 border-red-200 text-red-800" style={{ backgroundColor: '#fef2f2' }}>
          {error}
        </Card>
      )}
      {loading ? (
        <Card className="p-8 text-center text-gray-600" style={{ backgroundColor: '#fff' }}>Loading…</Card>
      ) : (
        <DataTable
          data={components}
          columns={[
            { key: 'component_name', header: 'Component name' },
            { key: 'component_type', header: 'Component type' },
            { key: 'critical_to_essential_performance', header: 'Critical to essential performance' },
          ]}
          onRowClick={(row) => navigate(`/devices/${deviceId}/components/${row.id}`)}
          emptyMessage="No components yet. Use Create Component to add one."
          light
        />
      )}

      <Modal
        isOpen={createOpen}
        onClose={() => {
          if (!createSubmitting) {
            setCreateOpen(false);
            setCreateError(null);
          }
        }}
        title="Create Component"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setCreateOpen(false)}
              disabled={createSubmitting}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleCreateSubmit}
              disabled={createSubmitting || !createName.trim()}
            >
              {createSubmitting ? 'Creating…' : 'Create'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          {createError && (
            <p className="text-sm text-red-600">{createError}</p>
          )}
          <Input
            label="Name"
            value={createName}
            onChange={(e) => setCreateName(e.target.value)}
            placeholder="Component name"
            required
          />
          <Textarea
            label="Description"
            value={createDescription}
            onChange={(e) => setCreateDescription(e.target.value)}
            placeholder="Optional description"
            rows={3}
          />
        </form>
      </Modal>
    </>
  );
}
