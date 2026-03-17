import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import {
  verificationLibraryApi,
  VerificationLibraryRecord,
  VerificationLibraryCreate,
  VerificationLibraryUpdate,
} from '../../services/riskKnowledgeBaseApi';

export const VerificationLibraryPage: React.FC = () => {
  const [items, setItems] = useState<VerificationLibraryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<VerificationLibraryRecord | null>(null);
  const [form, setForm] = useState<VerificationLibraryCreate & VerificationLibraryUpdate>({
    verification_id: '',
    verification_method: '',
    description: '',
    applicable_control_types: '',
    standard_reference: '',
    typical_test_output: '',
  });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const list = await verificationLibraryApi.list({
        skip: 0,
        limit: 500,
        search: search || undefined,
      });
      setItems(list);
    } catch (e) {
      console.error(e);
      alert('Failed to load verification library');
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
      verification_id: '',
      verification_method: '',
      description: '',
      applicable_control_types: '',
      standard_reference: '',
      typical_test_output: '',
    });
    setShowModal(true);
  };

  const openEdit = (row: VerificationLibraryRecord) => {
    setEditing(row);
    setForm({
      verification_id: row.verification_id ?? '',
      verification_method: row.verification_method,
      description: row.description ?? '',
      applicable_control_types: row.applicable_control_types ?? '',
      standard_reference: row.standard_reference ?? '',
      typical_test_output: row.typical_test_output ?? '',
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const save = async () => {
    if (!form.verification_method?.trim()) {
      alert('Verification method is required');
      return;
    }
    try {
      if (editing) {
        await verificationLibraryApi.update(editing.id, {
          verification_id: form.verification_id || undefined,
          verification_method: form.verification_method,
          description: form.description || undefined,
          applicable_control_types: form.applicable_control_types || undefined,
          standard_reference: form.standard_reference || undefined,
          typical_test_output: form.typical_test_output || undefined,
        });
      } else {
        await verificationLibraryApi.create({
          verification_id: form.verification_id || undefined,
          verification_method: form.verification_method,
          description: form.description || undefined,
          applicable_control_types: form.applicable_control_types || undefined,
          standard_reference: form.standard_reference || undefined,
          typical_test_output: form.typical_test_output || undefined,
        });
      }
      closeModal();
      load();
    } catch (e) {
      console.error(e);
      alert(editing ? 'Failed to update' : 'Failed to create');
    }
  };

  const remove = async (row: VerificationLibraryRecord) => {
    if (!window.confirm(`Delete "${row.verification_method}"?`)) return;
    try {
      await verificationLibraryApi.delete(row.id);
      load();
    } catch (e) {
      console.error(e);
      alert('Failed to delete');
    }
  };

  const columns = [
    { key: 'verification_id', header: 'Verification ID' },
    { key: 'verification_method', header: 'Verification method' },
    {
      key: 'description',
      header: 'Description',
      render: (r: VerificationLibraryRecord) => (
        <span className="line-clamp-2 max-w-xs">{r.description || '—'}</span>
      ),
    },
    {
      key: 'applicable_control_types',
      header: 'Applicable control types',
      render: (r: VerificationLibraryRecord) => (
        <span className="line-clamp-1 max-w-xs">{r.applicable_control_types || '—'}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r: VerificationLibraryRecord) => (
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
        title="Verification Library"
        description="Manage reusable verification methods for risk controls and V&V"
        actions={<Button onClick={openCreate}>Create verification</Button>}
      />

      <Card className="mb-6">
        <Input
          placeholder="Search by ID, method, description, standard..."
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
          emptyMessage="No verification library entries. Create one to get started."
        />
      )}

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editing ? 'Edit verification' : 'Create verification'}
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
            label="Verification ID (e.g. V-001)"
            value={form.verification_id}
            onChange={(e) => setForm({ ...form, verification_id: e.target.value })}
          />
          <Input
            label="Verification method"
            value={form.verification_method}
            onChange={(e) => setForm({ ...form, verification_method: e.target.value })}
            required
          />
          <Textarea
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            rows={3}
          />
          <Input
            label="Applicable control types (e.g. design, protective, information)"
            value={form.applicable_control_types}
            onChange={(e) => setForm({ ...form, applicable_control_types: e.target.value })}
          />
          <Input
            label="Standard reference"
            value={form.standard_reference}
            onChange={(e) => setForm({ ...form, standard_reference: e.target.value })}
          />
          <Textarea
            label="Typical test output"
            value={form.typical_test_output}
            onChange={(e) => setForm({ ...form, typical_test_output: e.target.value })}
            rows={2}
          />
        </div>
      </Modal>
    </div>
  );
};

export default VerificationLibraryPage;
