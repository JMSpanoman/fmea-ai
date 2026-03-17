import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import {
  harmLibraryApi,
  HarmLibraryRecord,
  HarmLibraryCreate,
  HarmLibraryUpdate,
} from '../../services/riskKnowledgeBaseApi';

export const HarmLibraryPage: React.FC = () => {
  const [items, setItems] = useState<HarmLibraryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<HarmLibraryRecord | null>(null);
  const [form, setForm] = useState<HarmLibraryCreate & HarmLibraryUpdate>({
    harm_id: '',
    harm_name: '',
    description: '',
    severity_guidance: '',
    clinical_examples: '',
  });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const list = await harmLibraryApi.list({ skip: 0, limit: 500, search: search || undefined });
      setItems(list);
    } catch (e) {
      console.error(e);
      alert('Failed to load harm library');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditing(null);
    setForm({
      harm_id: '',
      harm_name: '',
      description: '',
      severity_guidance: '',
      clinical_examples: '',
    });
    setShowModal(true);
  };

  const openEdit = (row: HarmLibraryRecord) => {
    setEditing(row);
    setForm({
      harm_id: row.harm_id ?? '',
      harm_name: row.harm_name,
      description: row.description ?? '',
      severity_guidance: row.severity_guidance ?? '',
      clinical_examples: row.clinical_examples ?? '',
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const save = async () => {
    if (!form.harm_name?.trim()) {
      alert('Harm name is required');
      return;
    }
    try {
      if (editing) {
        await harmLibraryApi.update(editing.id, {
          harm_id: form.harm_id || undefined,
          harm_name: form.harm_name,
          description: form.description || undefined,
          severity_guidance: form.severity_guidance || undefined,
          clinical_examples: form.clinical_examples || undefined,
        });
      } else {
        await harmLibraryApi.create({
          harm_id: form.harm_id || undefined,
          harm_name: form.harm_name,
          description: form.description || undefined,
          severity_guidance: form.severity_guidance || undefined,
          clinical_examples: form.clinical_examples || undefined,
        });
      }
      closeModal();
      load();
    } catch (e) {
      console.error(e);
      alert(editing ? 'Failed to update' : 'Failed to create');
    }
  };

  const remove = async (row: HarmLibraryRecord) => {
    if (!window.confirm(`Delete "${row.harm_name}"?`)) return;
    try {
      await harmLibraryApi.delete(row.id);
      load();
    } catch (e) {
      console.error(e);
      alert('Failed to delete');
    }
  };

  const columns = [
    { key: 'harm_id', header: 'Harm ID' },
    { key: 'harm_name', header: 'Harm name' },
    {
      key: 'description',
      header: 'Description',
      render: (r: HarmLibraryRecord) => (
        <span className="line-clamp-2 max-w-xs">{r.description || '—'}</span>
      ),
    },
    {
      key: 'severity_guidance',
      header: 'Severity guidance',
      render: (r: HarmLibraryRecord) => (
        <span className="line-clamp-2 max-w-xs">{r.severity_guidance || '—'}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r: HarmLibraryRecord) => (
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
        title="Harm Library"
        description="Manage reusable harm definitions (clinical outcomes) for risk analysis"
        actions={<Button onClick={openCreate}>Create harm</Button>}
      />

      <Card className="mb-6">
        <Input
          placeholder="Search by harm ID, name, description, clinical examples..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-md"
        />
      </Card>

      {loading ? (
        <div className="text-text-secondary">Loading...</div>
      ) : (
        <DataTable
          data={items}
          columns={columns}
          emptyMessage="No harm library entries. Create one to get started."
        />
      )}

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editing ? 'Edit harm' : 'Create harm'}
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
            label="Harm ID (e.g. HR-001)"
            value={form.harm_id}
            onChange={(e) => setForm({ ...form, harm_id: e.target.value })}
          />
          <Input
            label="Harm name"
            value={form.harm_name}
            onChange={(e) => setForm({ ...form, harm_name: e.target.value })}
            required
          />
          <Textarea
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            rows={3}
          />
          <Textarea
            label="Severity guidance"
            value={form.severity_guidance}
            onChange={(e) => setForm({ ...form, severity_guidance: e.target.value })}
            rows={2}
          />
          <Textarea
            label="Clinical examples"
            value={form.clinical_examples}
            onChange={(e) => setForm({ ...form, clinical_examples: e.target.value })}
            rows={3}
          />
        </div>
      </Modal>
    </div>
  );
};

export default HarmLibraryPage;
