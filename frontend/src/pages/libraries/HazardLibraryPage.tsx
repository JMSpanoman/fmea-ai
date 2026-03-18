import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import {
  hazardLibraryApi,
  HazardLibraryRecord,
  HazardLibraryCreate,
  HazardLibraryUpdate,
} from '../../services/riskKnowledgeBaseApi';

export const HazardLibraryPage: React.FC = () => {
  const [items, setItems] = useState<HazardLibraryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<HazardLibraryRecord | null>(null);
  const [form, setForm] = useState<HazardLibraryCreate & HazardLibraryUpdate>({
    hazard_id: '',
    hazard_name: '',
    description: '',
    category: '',
    typical_hazardous_situation: '',
    typical_harms: '',
    example_controls: '',
    verification_examples: '',
    lifecycle_phase: '',
  });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const list = await hazardLibraryApi.list({
        skip: 0,
        limit: 500,
        search: search || undefined,
        category: categoryFilter || undefined,
      });
      setItems(list);
    } catch (e) {
      console.error(e);
      alert('Failed to load hazard library');
    } finally {
      setLoading(false);
    }
  }, [search, categoryFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditing(null);
    setForm({
      hazard_id: '',
      hazard_name: '',
      description: '',
      category: '',
      typical_hazardous_situation: '',
      typical_harms: '',
      example_controls: '',
      verification_examples: '',
      lifecycle_phase: '',
    });
    setShowModal(true);
  };

  const openEdit = (row: HazardLibraryRecord) => {
    setEditing(row);
    setForm({
      hazard_id: row.hazard_id ?? '',
      hazard_name: row.hazard_name,
      description: row.description ?? '',
      category: row.category ?? '',
      typical_hazardous_situation: row.typical_hazardous_situation ?? '',
      typical_harms: row.typical_harms ?? '',
      example_controls: row.example_controls ?? '',
      verification_examples: row.verification_examples ?? '',
      lifecycle_phase: row.lifecycle_phase ?? '',
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const save = async () => {
    if (!form.hazard_name?.trim()) {
      alert('Hazard name is required');
      return;
    }
    try {
      const payload = {
        hazard_id: form.hazard_id || undefined,
        hazard_name: form.hazard_name,
        description: form.description || undefined,
        category: form.category || undefined,
        typical_hazardous_situation: form.typical_hazardous_situation || undefined,
        typical_harms: form.typical_harms || undefined,
        example_controls: form.example_controls || undefined,
        verification_examples: form.verification_examples || undefined,
        lifecycle_phase: form.lifecycle_phase || undefined,
      };
      if (editing) {
        await hazardLibraryApi.update(editing.id, payload);
      } else {
        await hazardLibraryApi.create(payload);
      }
      closeModal();
      load();
    } catch (e) {
      console.error(e);
      alert(editing ? 'Failed to update' : 'Failed to create');
    }
  };

  const remove = async (row: HazardLibraryRecord) => {
    if (!window.confirm(`Delete "${row.hazard_name}"?`)) return;
    try {
      await hazardLibraryApi.delete(row.id);
      load();
    } catch (e) {
      console.error(e);
      alert('Failed to delete');
    }
  };

  const columns = [
    { key: 'hazard_id', header: 'Hazard ID' },
    { key: 'hazard_name', header: 'Hazard name' },
    {
      key: 'description',
      header: 'Description',
      render: (r: HazardLibraryRecord) => (
        <span className="line-clamp-2 max-w-xs">{r.description || '—'}</span>
      ),
    },
    { key: 'category', header: 'Category' },
    { key: 'lifecycle_phase', header: 'Lifecycle phase' },
    {
      key: 'actions',
      header: 'Actions',
      render: (r: HazardLibraryRecord) => (
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
        title="Hazard Library"
        description="Manage reusable hazard definitions for risk analysis"
        actions={<Button onClick={openCreate}>Create hazard</Button>}
      />

      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            placeholder="Search by hazard name, ID, description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Input
            placeholder="Filter by category"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          />
        </div>
      </Card>

      {loading ? (
        <div className="text-text-secondary">Loading...</div>
      ) : (
        <DataTable
          data={items}
          columns={columns}
          emptyMessage="No hazard library entries. Create one to get started."
        />
      )}

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editing ? 'Edit hazard' : 'Create hazard'}
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
            label="Hazard ID (e.g. HZ-001)"
            value={form.hazard_id}
            onChange={(e) => setForm({ ...form, hazard_id: e.target.value })}
          />
          <Input
            label="Hazard name"
            value={form.hazard_name}
            onChange={(e) => setForm({ ...form, hazard_name: e.target.value })}
            required
          />
          <Textarea
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            rows={3}
          />
          <Input
            label="Category"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
          />
          <Textarea
            label="Typical hazardous situation"
            value={form.typical_hazardous_situation}
            onChange={(e) => setForm({ ...form, typical_hazardous_situation: e.target.value })}
            rows={2}
          />
          <Textarea
            label="Typical harms"
            value={form.typical_harms}
            onChange={(e) => setForm({ ...form, typical_harms: e.target.value })}
            rows={2}
          />
          <Textarea
            label="Example controls"
            value={form.example_controls}
            onChange={(e) => setForm({ ...form, example_controls: e.target.value })}
            rows={2}
          />
          <Textarea
            label="Verification examples"
            value={form.verification_examples}
            onChange={(e) => setForm({ ...form, verification_examples: e.target.value })}
            rows={2}
          />
          <Input
            label="Lifecycle phase"
            value={form.lifecycle_phase}
            onChange={(e) => setForm({ ...form, lifecycle_phase: e.target.value })}
          />
        </div>
      </Modal>
    </div>
  );
};

export default HazardLibraryPage;
