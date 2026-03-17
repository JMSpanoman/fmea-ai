import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import {
  riskControlLibraryApi,
  RiskControlLibraryRecord,
  RiskControlLibraryCreate,
  RiskControlLibraryUpdate,
} from '../../services/riskKnowledgeBaseApi';

const CONTROL_TYPES = ['design', 'protective', 'information'];

export const RiskControlLibraryPage: React.FC = () => {
  const [items, setItems] = useState<RiskControlLibraryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [controlTypeFilter, setControlTypeFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<RiskControlLibraryRecord | null>(null);
  const [form, setForm] = useState<RiskControlLibraryCreate & RiskControlLibraryUpdate>({
    control_id: '',
    control_name: '',
    control_type: 'protective',
    description: '',
    example_application: '',
    typical_verification_method: '',
    related_standards: '',
  });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const list = await riskControlLibraryApi.list({
        skip: 0,
        limit: 500,
        search: search || undefined,
        control_type: controlTypeFilter || undefined,
      });
      setItems(list);
    } catch (e) {
      console.error(e);
      alert('Failed to load risk control library');
    } finally {
      setLoading(false);
    }
  }, [search, controlTypeFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditing(null);
    setForm({
      control_id: '',
      control_name: '',
      control_type: 'protective',
      description: '',
      example_application: '',
      typical_verification_method: '',
      related_standards: '',
    });
    setShowModal(true);
  };

  const openEdit = (row: RiskControlLibraryRecord) => {
    setEditing(row);
    setForm({
      control_id: row.control_id ?? '',
      control_name: row.control_name,
      control_type: row.control_type,
      description: row.description ?? '',
      example_application: row.example_application ?? '',
      typical_verification_method: row.typical_verification_method ?? '',
      related_standards: row.related_standards ?? '',
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const save = async () => {
    if (!form.control_name?.trim()) {
      alert('Control name is required');
      return;
    }
    if (!CONTROL_TYPES.includes(form.control_type)) {
      alert('Control type must be design, protective, or information');
      return;
    }
    try {
      if (editing) {
        await riskControlLibraryApi.update(editing.id, {
          control_id: form.control_id || undefined,
          control_name: form.control_name,
          control_type: form.control_type,
          description: form.description || undefined,
          example_application: form.example_application || undefined,
          typical_verification_method: form.typical_verification_method || undefined,
          related_standards: form.related_standards || undefined,
        });
      } else {
        await riskControlLibraryApi.create({
          control_id: form.control_id || undefined,
          control_name: form.control_name,
          control_type: form.control_type,
          description: form.description || undefined,
          example_application: form.example_application || undefined,
          typical_verification_method: form.typical_verification_method || undefined,
          related_standards: form.related_standards || undefined,
        });
      }
      closeModal();
      load();
    } catch (e) {
      console.error(e);
      alert(editing ? 'Failed to update' : 'Failed to create');
    }
  };

  const remove = async (row: RiskControlLibraryRecord) => {
    if (!window.confirm(`Delete "${row.control_name}"?`)) return;
    try {
      await riskControlLibraryApi.delete(row.id);
      load();
    } catch (e) {
      console.error(e);
      alert('Failed to delete');
    }
  };

  const columns = [
    { key: 'control_id', header: 'Control ID' },
    { key: 'control_name', header: 'Control name' },
    { key: 'control_type', header: 'Type' },
    {
      key: 'description',
      header: 'Description',
      render: (r: RiskControlLibraryRecord) => (
        <span className="line-clamp-2 max-w-xs">{r.description || '—'}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r: RiskControlLibraryRecord) => (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => openEdit(r)}>
            Edit
          </Button>
          <Button variant="danger" size="sm" onClick={() => remove(r)}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="p-6">
      <PageHeader
        title="Risk Control Library"
        description="Manage reusable risk control measures (design, protective, information)"
        actions={<Button onClick={openCreate}>Create risk control</Button>}
      />

      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            placeholder="Search by name, ID, description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={controlTypeFilter}
            onChange={(e) => setControlTypeFilter(e.target.value)}
          >
            <option value="">All types</option>
            {CONTROL_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {loading ? (
        <div className="text-text-secondary">Loading...</div>
      ) : (
        <DataTable
          data={items}
          columns={columns}
          emptyMessage="No risk control library entries. Create one to get started."
        />
      )}

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editing ? 'Edit risk control' : 'Create risk control'}
        size="lg"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button onClick={save}>{editing ? 'Update' : 'Create'}</Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input
            label="Control ID (e.g. RC-001)"
            value={form.control_id}
            onChange={(e) => setForm({ ...form, control_id: e.target.value })}
          />
          <Input
            label="Control name"
            value={form.control_name}
            onChange={(e) => setForm({ ...form, control_name: e.target.value })}
            required
          />
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">
              Control type
            </label>
            <select
              className="w-full px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
              value={form.control_type}
              onChange={(e) => setForm({ ...form, control_type: e.target.value })}
            >
              {CONTROL_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <Textarea
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            rows={3}
          />
          <Textarea
            label="Example application"
            value={form.example_application}
            onChange={(e) => setForm({ ...form, example_application: e.target.value })}
            rows={2}
          />
          <Textarea
            label="Typical verification method"
            value={form.typical_verification_method}
            onChange={(e) => setForm({ ...form, typical_verification_method: e.target.value })}
            rows={2}
          />
          <Input
            label="Related standards"
            value={form.related_standards}
            onChange={(e) => setForm({ ...form, related_standards: e.target.value })}
          />
        </div>
      </Modal>
    </div>
  );
};

export default RiskControlLibraryPage;
