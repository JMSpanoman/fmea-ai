import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input, Textarea } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import {
  deviceArchitectureApi,
  DeviceArchitectureRecord,
  DeviceArchitectureDetail,
  DeviceArchitectureNodeRecord,
  DeviceInterfaceRecord,
  SuggestedHazard,
  HazardLogTable,
} from '../services/deviceArchitectureApi';

const NODE_TYPES = ['system', 'subsystem', 'component'];

export const DeviceArchitecturePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [architectures, setArchitectures] = useState<DeviceArchitectureRecord[]>([]);
  const [selectedArch, setSelectedArch] = useState<DeviceArchitectureDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [suggestions, setSuggestions] = useState<SuggestedHazard[] | null>(null);
  const [hazardLog, setHazardLog] = useState<HazardLogTable | null>(null);
  const [createRiskItems, setCreateRiskItems] = useState(false);
  const [showArchModal, setShowArchModal] = useState(false);
  const [showNodeModal, setShowNodeModal] = useState(false);
  const [showInterfaceModal, setShowInterfaceModal] = useState(false);
  const [archForm, setArchForm] = useState({ name: '', description: '' });
  const [nodeForm, setNodeForm] = useState({
    name: '',
    description: '',
    node_type: 'component',
    component_type: '',
    parent_id: '',
  });
  const [interfaceForm, setInterfaceForm] = useState({
    from_node_id: '',
    to_node_id: '',
    name: '',
    interface_type: '',
  });

  const loadArchitectures = useCallback(async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const list = await deviceArchitectureApi.list(projectId);
      setArchitectures(list);
      if (selectedArch && !list.find((a) => a.id === selectedArch.id)) {
        setSelectedArch(null);
        setSuggestions(null);
        setHazardLog(null);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  const loadDetail = useCallback(
    async (archId: string) => {
      if (!projectId) return;
      try {
        const detail = await deviceArchitectureApi.get(projectId, archId);
        setSelectedArch(detail);
        setSuggestions(null);
        setHazardLog(null);
      } catch (e) {
        console.error(e);
      }
    },
    [projectId]
  );

  useEffect(() => {
    loadArchitectures();
  }, [loadArchitectures]);

  const handleCreateArch = async () => {
    if (!projectId || !archForm.name.trim()) return;
    try {
      await deviceArchitectureApi.create(projectId, {
        name: archForm.name.trim(),
        description: archForm.description || undefined,
      });
      setArchForm({ name: '', description: '' });
      setShowArchModal(false);
      loadArchitectures();
    } catch (e) {
      console.error(e);
      alert('Failed to create architecture');
    }
  };

  const handleCreateNode = async () => {
    if (!projectId || !selectedArch || !nodeForm.name.trim()) return;
    try {
      await deviceArchitectureApi.createNode(projectId, selectedArch.id, {
        name: nodeForm.name.trim(),
        description: nodeForm.description || undefined,
        node_type: nodeForm.node_type,
        component_type: nodeForm.component_type || undefined,
        parent_id: nodeForm.parent_id || undefined,
      });
      setNodeForm({
        name: '',
        description: '',
        node_type: 'component',
        component_type: '',
        parent_id: '',
      });
      setShowNodeModal(false);
      loadDetail(selectedArch.id);
    } catch (e) {
      console.error(e);
      alert('Failed to create node');
    }
  };

  const handleCreateInterface = async () => {
    if (!projectId || !selectedArch || !interfaceForm.from_node_id || !interfaceForm.to_node_id)
      return;
    try {
      await deviceArchitectureApi.createInterface(projectId, selectedArch.id, {
        from_node_id: interfaceForm.from_node_id,
        to_node_id: interfaceForm.to_node_id,
        name: interfaceForm.name || undefined,
        interface_type: interfaceForm.interface_type || undefined,
      });
      setInterfaceForm({ from_node_id: '', to_node_id: '', name: '', interface_type: '' });
      setShowInterfaceModal(false);
      loadDetail(selectedArch.id);
    } catch (e) {
      console.error(e);
      alert('Failed to create interface');
    }
  };

  const handleGenerateHazards = async () => {
    if (!projectId || !selectedArch) return;
    try {
      const res = await deviceArchitectureApi.generateHazards(
        projectId,
        selectedArch.id,
        { create_risk_items: createRiskItems },
        true
      );
      setSuggestions(res.suggestions);
      if (res.created_risk_item_ids?.length) {
        alert(`Created ${res.created_risk_item_ids.length} risk item(s). You can view them under Risk Items.`);
      }
    } catch (e) {
      console.error(e);
      alert('Failed to generate hazards');
    }
  };

  const handleLoadHazardLog = async () => {
    if (!projectId || !selectedArch) return;
    try {
      const log = await deviceArchitectureApi.getHazardLog(projectId, selectedArch.id, true);
      setHazardLog(log);
    } catch (e) {
      console.error(e);
      alert('Failed to load hazard log');
    }
  };

  const getNodeById = (id: string): DeviceArchitectureNodeRecord | undefined =>
    selectedArch?.nodes.find((n) => n.id === id);

  if (!projectId) {
    return (
      <div className="p-4">
        <p>Project not found.</p>
        <Button onClick={() => navigate('/projects')}>Back to projects</Button>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <PageHeader
        title="Device Architecture"
        subtitle="Define device structure for architecture-driven hazard analysis (SmartRisk)"
      />
      <div className="flex gap-4 mb-4">
        <Button onClick={() => navigate(`/projects/${projectId}/dashboard`)} variant="secondary">
          Back to project
        </Button>
        <Button onClick={() => setShowArchModal(true)}>New architecture</Button>
      </div>

      {loading ? (
        <p>Loading architectures...</p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-2">Architectures</h3>
            <ul className="space-y-1">
              {architectures.map((a) => (
                <li key={a.id}>
                  <button
                    type="button"
                    onClick={() => loadDetail(a.id)}
                    className={`w-full text-left px-2 py-1.5 rounded ${
                      selectedArch?.id === a.id ? 'bg-blue-100' : 'hover:bg-gray-100'
                    }`}
                  >
                    {a.name}
                  </button>
                </li>
              ))}
              {architectures.length === 0 && (
                <li className="text-gray-500 text-sm">No architectures. Create one to start.</li>
              )}
            </ul>
          </Card>

          <div className="lg:col-span-2 space-y-4">
            {selectedArch && (
              <>
                <Card className="p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="font-semibold">{selectedArch.name}</h3>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => setShowNodeModal(true)}>
                        Add node
                      </Button>
                      <Button size="sm" variant="secondary" onClick={() => setShowInterfaceModal(true)}>
                        Add interface
                      </Button>
                    </div>
                  </div>
                  {selectedArch.description && (
                    <p className="text-sm text-gray-600 mb-3">{selectedArch.description}</p>
                  )}
                  <h4 className="text-sm font-medium mt-2">Nodes ({selectedArch.nodes.length})</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    {selectedArch.nodes.map((n) => (
                      <li key={n.id} className="flex justify-between">
                        <span>
                          [{n.node_type}] {n.name}
                          {n.component_type && (
                            <span className="text-gray-500 ml-1">({n.component_type})</span>
                          )}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <h4 className="text-sm font-medium mt-2">Interfaces ({selectedArch.interfaces.length})</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    {selectedArch.interfaces.map((i) => (
                      <li key={i.id}>
                        {getNodeById(i.from_node_id)?.name ?? i.from_node_id.slice(0, 8)} →{' '}
                        {getNodeById(i.to_node_id)?.name ?? i.to_node_id.slice(0, 8)}
                        {i.interface_type && ` (${i.interface_type})`}
                      </li>
                    ))}
                  </ul>
                </Card>

                <Card className="p-4">
                  <h3 className="font-semibold mb-2">Hazard generation</h3>
                  <label className="flex items-center gap-2 mb-2">
                    <input
                      type="checkbox"
                      checked={createRiskItems}
                      onChange={(e) => setCreateRiskItems(e.target.checked)}
                    />
                    Create risk items from suggestions (link to hazard library)
                  </label>
                  <div className="flex gap-2">
                    <Button onClick={handleGenerateHazards}>Generate hazards</Button>
                    <Button variant="secondary" onClick={handleLoadHazardLog}>
                      View hazard log table
                    </Button>
                  </div>
                  {suggestions !== null && (
                    <div className="mt-3">
                      <h4 className="text-sm font-medium">Suggested hazards ({suggestions.length})</h4>
                      <ul className="text-sm mt-1 space-y-1 max-h-48 overflow-y-auto">
                        {suggestions.map((s, i) => (
                          <li key={`${s.source_id}-${s.rule_id}-${i}`}>
                            {s.source_type}: {s.source_name} → {s.hazard_name ?? s.hazard_library_id}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {hazardLog && (
                    <div className="mt-3">
                      <h4 className="text-sm font-medium">Hazard log: {hazardLog.architecture_name}</h4>
                      <div className="overflow-x-auto mt-1 max-h-64 overflow-y-auto">
                        <table className="w-full text-sm border">
                          <thead>
                            <tr className="bg-gray-100">
                              <th className="text-left p-1">Source</th>
                              <th className="text-left p-1">Hazard</th>
                              <th className="text-left p-1">Code</th>
                            </tr>
                          </thead>
                          <tbody>
                            {hazardLog.rows.map((r, i) => (
                              <tr key={i} className="border-t">
                                <td className="p-1">{r.source_name}</td>
                                <td className="p-1">{r.hazard_name ?? '-'}</td>
                                <td className="p-1">{r.hazard_code ?? '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </Card>
              </>
            )}
          </div>
        </div>
      )}

      <Modal open={showArchModal} onClose={() => setShowArchModal(false)} title="New architecture">
        <div className="space-y-2">
          <Input
            label="Name"
            value={archForm.name}
            onChange={(e) => setArchForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="e.g. Main device v1"
          />
          <Textarea
            label="Description"
            value={archForm.description}
            onChange={(e) => setArchForm((f) => ({ ...f, description: e.target.value }))}
          />
          <Button onClick={handleCreateArch}>Create</Button>
        </div>
      </Modal>

      <Modal open={showNodeModal} onClose={() => setShowNodeModal(false)} title="Add node">
        <div className="space-y-2">
          <Input
            label="Name"
            value={nodeForm.name}
            onChange={(e) => setNodeForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="e.g. Power supply"
          />
          <Textarea
            label="Description"
            value={nodeForm.description}
            onChange={(e) => setNodeForm((f) => ({ ...f, description: e.target.value }))}
          />
          <label className="block">
            <span className="text-sm text-gray-600">Node type</span>
            <select
              className="mt-1 block w-full border rounded px-2 py-1"
              value={nodeForm.node_type}
              onChange={(e) => setNodeForm((f) => ({ ...f, node_type: e.target.value }))}
            >
              {NODE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <Input
            label="Component type (for rules)"
            value={nodeForm.component_type}
            onChange={(e) => setNodeForm((f) => ({ ...f, component_type: e.target.value }))}
            placeholder="e.g. electrical, mechanical"
          />
          <label className="block">
            <span className="text-sm text-gray-600">Parent node</span>
            <select
              className="mt-1 block w-full border rounded px-2 py-1"
              value={nodeForm.parent_id}
              onChange={(e) => setNodeForm((f) => ({ ...f, parent_id: e.target.value }))}
            >
              <option value="">— None (root) —</option>
              {selectedArch?.nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name}
                </option>
              ))}
            </select>
          </label>
          <Button onClick={handleCreateNode}>Add node</Button>
        </div>
      </Modal>

      <Modal open={showInterfaceModal} onClose={() => setShowInterfaceModal(false)} title="Add interface">
        <div className="space-y-2">
          <label className="block">
            <span className="text-sm text-gray-600">From node</span>
            <select
              className="mt-1 block w-full border rounded px-2 py-1"
              value={interfaceForm.from_node_id}
              onChange={(e) =>
                setInterfaceForm((f) => ({ ...f, from_node_id: e.target.value }))
              }
            >
              <option value="">— Select —</option>
              {selectedArch?.nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-sm text-gray-600">To node</span>
            <select
              className="mt-1 block w-full border rounded px-2 py-1"
              value={interfaceForm.to_node_id}
              onChange={(e) =>
                setInterfaceForm((f) => ({ ...f, to_node_id: e.target.value }))
              }
            >
              <option value="">— Select —</option>
              {selectedArch?.nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name}
                </option>
              ))}
            </select>
          </label>
          <Input
            label="Name"
            value={interfaceForm.name}
            onChange={(e) => setInterfaceForm((f) => ({ ...f, name: e.target.value }))}
          />
          <Input
            label="Interface type (for rules)"
            value={interfaceForm.interface_type}
            onChange={(e) =>
              setInterfaceForm((f) => ({ ...f, interface_type: e.target.value }))
            }
            placeholder="e.g. electrical, data"
          />
          <Button onClick={handleCreateInterface}>Add interface</Button>
        </div>
      </Modal>
    </div>
  );
};
