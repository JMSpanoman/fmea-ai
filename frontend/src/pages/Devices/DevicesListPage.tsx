import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { devicesApi, DeviceRecord } from '../../services/devicesApi';
import projectService from '../../services/projectService';

interface ProjectOption {
  id: string;
  name: string;
}

export default function DevicesListPage() {
  const navigate = useNavigate();
  const [devices, setDevices] = useState<DeviceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [projects, setProjects] = useState<ProjectOption[]>([]);
  const [createProjectId, setCreateProjectId] = useState('');
  const [createName, setCreateName] = useState('');
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const loadDevices = () => {
    setLoading(true);
    setError(null);
    devicesApi
      .listDevices()
      .then(setDevices)
      .catch((e) => {
        console.error(e);
        setError('Failed to load devices.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const openCreate = () => {
    setCreateOpen(true);
    setCreateError(null);
    setCreateProjectId('');
    setCreateName('');
    projectService
      .getProjects()
      .then((list) => setProjects(list.map((p) => ({ id: p.id, name: p.name }))))
      .catch(() => setProjects([]));
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createProjectId.trim()) return;
    setCreateSubmitting(true);
    setCreateError(null);
    try {
      await devicesApi.createDevice({
        project_id: createProjectId.trim(),
        name: createName.trim() || undefined,
      });
      setCreateOpen(false);
      loadDevices();
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create device.');
    } finally {
      setCreateSubmitting(false);
    }
  };

  return (
    <div className="p-4 max-w-4xl mx-auto min-h-full" style={{ backgroundColor: '#f5f5f5', color: '#111' }}>
      <PageHeader
        title="Devices"
        subtitle="Devices from your projects. Open a device to view risk outputs and components."
      />
      <div className="flex gap-2 mb-4">
        <Button variant="secondary" onClick={() => navigate('/projects')}>
          Back to projects
        </Button>
      </div>
      {error && (
        <Card className="p-4 mb-4 bg-red-50 border-red-200 text-red-800" style={{ backgroundColor: '#fef2f2' }}>
          {error}
        </Card>
      )}
      {!error && loading && (
        <Card className="p-8 text-center text-gray-600" style={{ backgroundColor: '#fff' }}>Loading…</Card>
      )}
      {!error && !loading && devices.length === 0 && (
        <Card className="p-8 text-center" style={{ backgroundColor: '#fff' }}>
          <p className="text-gray-600 mb-4">
            No devices yet. Create a device for a project, or create one when you accept component risk suggestions.
          </p>
          <Button variant="primary" onClick={openCreate}>
            Create device
          </Button>
        </Card>
      )}

      <Modal
        isOpen={createOpen}
        onClose={() => !createSubmitting && setCreateOpen(false)}
        title="Create device"
        footer={
          <>
            <Button variant="secondary" onClick={() => setCreateOpen(false)} disabled={createSubmitting}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleCreateSubmit}
              disabled={createSubmitting || !createProjectId.trim()}
            >
              {createSubmitting ? 'Creating…' : 'Create'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          {createError && <p className="text-sm text-red-600">{createError}</p>}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project</label>
            <select
              value={createProjectId}
              onChange={(e) => setCreateProjectId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900"
              required
            >
              <option value="">Select a project</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <Input
            label="Device name (optional)"
            value={createName}
            onChange={(e) => setCreateName(e.target.value)}
            placeholder="e.g. Main unit"
          />
        </form>
      </Modal>
      {!error && !loading && devices.length > 0 && (
        <Card className="overflow-hidden" style={{ backgroundColor: '#fff' }}>
          <ul className="divide-y divide-gray-200">
            {devices.map((d) => (
              <li key={d.id}>
                <button
                  type="button"
                  onClick={() => navigate(`/devices/${d.id}`)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors text-gray-900"
                >
                  <div className="font-medium">
                    {d.name || d.id.slice(0, 8)}
                  </div>
                  {d.description && (
                    <div className="text-sm text-gray-600 mt-0.5 line-clamp-1">
                      {d.description}
                    </div>
                  )}
                  <div className="text-xs text-gray-500 mt-1">
                    ID: {d.id.slice(0, 8)}…
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
