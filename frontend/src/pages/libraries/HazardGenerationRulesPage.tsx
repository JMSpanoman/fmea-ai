import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import {
  hazardGenerationRulesApi,
  HazardGenerationRuleRecord,
  HazardGenerationRuleCreate,
  HazardGenerationRuleUpdate,
} from '../../services/hazardGenerationRulesApi';
import { hazardLibraryApi } from '../../services/riskKnowledgeBaseApi';

export const HazardGenerationRulesPage: React.FC = () => {
  const [items, setItems] = useState<HazardGenerationRuleRecord[]>([]);
  const [hazards, setHazards] = useState<{ id: string; name: string; code?: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggerFilter, setTriggerFilter] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<HazardGenerationRuleRecord | null>(null);
  const [form, setForm] = useState<HazardGenerationRuleCreate & HazardGenerationRuleUpdate>({
    name: '',
    trigger_type: 'component',
    component_type: '',
    interface_type: '',
    node_type: '',
    hazard_library_id: '',
    priority: 0,
    is_active: true,
  });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [rules, hazardList] = await Promise.all([
        hazardGenerationRulesApi.list({
          trigger_type: triggerFilter || undefined,
          limit: 500,
        }),
        hazardLibraryApi.list({ skip: 0, limit: 500 }),
      ]);
      setItems(rules);
      setHazards(hazardList.map((h) => ({ id: h.id, name: h.hazard_name, code: h.hazard_id ?? undefined })));
    } catch (e) {
      console.error(e);
      alert('Failed to load rules');
    } finally {
      setLoading(false);
    }
  }, [triggerFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditing(null);
    setForm({
      name: '',
      trigger_type: 'component',
      component_type: '',
      interface_type: '',
      node_type: '',
      hazard_library_id: hazards[0]?.id ?? '',
      priority: 0,
      is_active: true,
    });
    setShowModal(true);
  };

  const openEdit = (row: HazardGenerationRuleRecord) => {
    setEditing(row);
    setForm({
      name: row.name ?? '',
      trigger_type: row.trigger_type,
      component_type: row.component_type ?? '',
      interface_type: row.interface_type ?? '',
      node_type: row.node_type ?? '',
      hazard_library_id: row.hazard_library_id,
      priority: row.priority ?? 0,
      is_active: row.is_active ?? true,
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const save = async () => {
    if (!form.hazard_library_id) {
      alert('Hazard library entry is required');
      return;
    }
    try {
      if (editing) {
        await hazardGenerationRulesApi.update(editing.id, {
          name: form.name || undefined,
          trigger_type: form.trigger_type,
          component_type: form.component_type || undefined,
          interface_type: form.interface_type || undefined,
          node_type: form.node_type || undefined,
          hazard_library_id: form.hazard_library_id,
          priority: form.priority,
          is_active: form.is_active,
        });
      } else {
        await hazardGenerationRulesApi.create({
          name: form.name || undefined,
          trigger_type: form.trigger_type,
          component_type: form.component_type || undefined,
          interface_type: form.interface_type || undefined,
          node_type: form.node_type || undefined,
          hazard_library_id: form.hazard_library_id,
          priority: form.priority,
          is_active: form.is_active,
        });
      }
      closeModal();
      load();
    } catch (e) {
      console.error(e);
      alert('Failed to save rule');
    }
  };

  const deleteRule = async (id: string) => {
    if (!window.confirm('Delete this rule?')) return;
    try {
      await hazardGenerationRulesApi.delete(id);
      load();
    } catch (e) {
      console.error(e);
      alert('Failed to delete rule');
    }
  };

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'trigger_type', label: 'Trigger' },
    { key: 'component_type', label: 'Component type' },
    { key: 'interface_type', label: 'Interface type' },
    { key: 'hazard_library_id', label: 'Hazard (ID)' },
    { key: 'priority', label: 'Priority' },
    { key: 'is_active', label: 'Active' },
  ];

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <PageHeader
        title="Hazard Generation Rules"
        subtitle="Map component/interface types to hazard library (SmartRisk Phase 2)"
      />
      <div className="flex gap-2 mb-4">
        <select
          className="border rounded px-2 py-1 text-sm"
          value={triggerFilter}
          onChange={(e) => setTriggerFilter(e.target.value)}
        >
          <option value="">All triggers</option>
          <option value="component">Component</option>
          <option value="interface">Interface</option>
        </select>
        <Button onClick={openCreate}>New rule</Button>
      </div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <Card className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                {columns.map((c) => (
                  <th key={c.key} className="text-left p-2">
                    {c.label}
                  </th>
                ))}
                <th className="p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.id} className="border-b">
                  {columns.map((c) => (
                    <td key={c.key} className="p-2">
                      {String((row as any)[c.key] ?? '')}
                    </td>
                  ))}
                  <td className="p-2">
                    <button
                      type="button"
                      className="text-blue-600 mr-2"
                      onClick={() => openEdit(row)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="text-red-600"
                      onClick={() => deleteRule(row.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {items.length === 0 && (
            <p className="p-4 text-gray-500 text-sm">No rules. Create rules to link component/interface types to hazards.</p>
          )}
        </Card>
      )}

      <Modal open={showModal} onClose={closeModal} title={editing ? 'Edit rule' : 'New rule'}>
        <div className="space-y-2">
          <Input
            label="Name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          />
          <label className="block">
            <span className="text-sm text-gray-600">Trigger type</span>
            <select
              className="mt-1 block w-full border rounded px-2 py-1"
              value={form.trigger_type}
              onChange={(e) => setForm((f) => ({ ...f, trigger_type: e.target.value }))}
            >
              <option value="component">Component</option>
              <option value="interface">Interface</option>
            </select>
          </label>
          {form.trigger_type === 'component' && (
            <Input
              label="Component type (e.g. electrical, mechanical)"
              value={form.component_type}
              onChange={(e) => setForm((f) => ({ ...f, component_type: e.target.value }))}
            />
          )}
          {form.trigger_type === 'interface' && (
            <Input
              label="Interface type (e.g. electrical, data)"
              value={form.interface_type}
              onChange={(e) => setForm((f) => ({ ...f, interface_type: e.target.value }))}
            />
          )}
          <Input
            label="Node type filter (optional)"
            value={form.node_type}
            onChange={(e) => setForm((f) => ({ ...f, node_type: e.target.value }))}
            placeholder="system, subsystem, component"
          />
          <label className="block">
            <span className="text-sm text-gray-600">Hazard (from library)</span>
            <select
              className="mt-1 block w-full border rounded px-2 py-1"
              value={form.hazard_library_id}
              onChange={(e) => setForm((f) => ({ ...f, hazard_library_id: e.target.value }))}
            >
              <option value="">— Select —</option>
              {hazards.map((h) => (
                <option key={h.id} value={h.id}>
                  {h.code ? `${h.code}: ` : ''}{h.name}
                </option>
              ))}
            </select>
          </label>
          <Input
            label="Priority"
            type="number"
            value={form.priority ?? 0}
            onChange={(e) => setForm((f) => ({ ...f, priority: parseInt(e.target.value, 10) || 0 }))}
          />
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.is_active ?? true}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
            />
            Active
          </label>
          <Button onClick={save}>{editing ? 'Update' : 'Create'}</Button>
        </div>
      </Modal>
    </div>
  );
};

export default HazardGenerationRulesPage;
