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
    code: '',
    name: '',
    description: '',
    category: '',
    source_standard: '',
    is_active: true,
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
      code: '',
      name: '',
      description: '',
      category: '',
      source_standard: '',
      is_active: true,
    });
    setShowModal(true);
  };

  const openEdit = (row: HazardLibraryRecord) => {
    setEditing(row);
    setForm({
      code: row.code ?? '',
      name: row.name,
      description: row.description ?? '',
      category: row.category ?? '',
      source_standard: row.source_standard ?? '',
      is_active: row.is_active ?? true,
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const save = async () => {
    if (!form.name?.trim()) {
      alert('Name is required');
      return;
    }
    try {
      if (editing) {
        await hazardLibraryApi.update(editing.id, {
          code: form.code || undefined,
          name: form.name,
          description: form.description || undefined,
          category: form.category || undefined,
          source_standard: form.source_standard || undefined,
          is_active: form.is_active,
        });
      } else {
        await hazardLibraryApi.create({
          code: form.code || undefined,
          name: form.name,
          description: form.description || undefined,
          category: form.category || undefined,
          source_standard: form.source_standard || undefined,
          is_active: form.is_active ?? true,
        });
      }
      closeModal();
      load();
    } catch (e) {
      console.error(e);
      alert(editing ? 'Failed to update' : 'Failed to create');
    }
  };

  const remove = async (row: HazardLibraryRecord) => {
    if (!window.confirm(`Delete "${row.name}"?`)) return;
    try {
      await hazardLibraryApi.delete(row.id);
      load();
    } catch (e) {
      console.error(e);
      alert('Failed to delete');
    }
  };

  const columns = [
    { key: 'code', header: 'Code' },
    { key: 'name', header: 'Name' },
    {
      key: 'description',
      header: 'Description',
      render: (r: HazardLibraryRecord) => (
        <span className="line-clamp-2 max-w-xs">{r.description || '—'}</span>
      ),
    },
    { key: 'category', header: 'Category' },
    {
      key: 'is_active',
      header: 'Active',
      render: (r: HazardLibraryRecord) => (r.is_active ? 'Yes' : 'No'),
    },
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
            placeholder="Search by name, code, description..."
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
            label="Code (e.g. HZ-001)"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
          />
          <Input
            label="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
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
          <Input
            label="Source standard"
            value={form.source_standard}
            onChange={(e) => setForm({ ...form, source_standard: e.target.value })}
          />
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
              className="rounded border-border"
            />
            <span className="text-sm text-text-primary">Active</span>
          </label>
        </div>
      </Modal>
    </div>
  );
};

export default HazardLibraryPage;
