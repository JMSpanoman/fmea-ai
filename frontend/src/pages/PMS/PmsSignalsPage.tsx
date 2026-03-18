import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import {
  getPMSSignals,
  createPMSSignal,
  updatePMSSignal,
  deletePMSSignal,
  linkPMSSignalToRisk,
  handoffPMSSignalToCAPA,
  handoffPMSSignalToChange,
  PMSSignal,
  PMSSignalCreate,
  PMSSignalUpdate
} from '../../services/apiService';
import api from '../../axios';

const PmsSignalsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [signals, setSignals] = useState<PMSSignal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [componentFilter, setComponentFilter] = useState<string>('');
  const [signalTypeFilter, setSignalTypeFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [dateFromFilter, setDateFromFilter] = useState<string>('');
  const [dateToFilter, setDateToFilter] = useState<string>('');
  
  // Create/Edit Modal
  const [showModal, setShowModal] = useState(false);
  const [editingSignal, setEditingSignal] = useState<PMSSignal | null>(null);
  const [formData, setFormData] = useState<Partial<PMSSignalCreate>>({
    signal_key: '',
    signal_type: 'complaint',
    component_names_json: [],
    title: '',
    description: '',
    source_ref: '',
    date_detected: new Date().toISOString().split('T')[0],
    trend_status: 'under_review',
    trigger_status: 'not_triggered',
    status: 'open'
  });
  const [componentInput, setComponentInput] = useState('');
  
  // Available components
  const [availableComponents, setAvailableComponents] = useState<any[]>([]);

  const finalProjectId = projectId || currentProject?.id;

  useEffect(() => {
    if (finalProjectId) {
      loadSignals();
      loadComponents();
    }
  }, [finalProjectId, componentFilter, signalTypeFilter, statusFilter, dateFromFilter, dateToFilter]);

  const loadComponents = async () => {
    if (!finalProjectId) return;
    try {
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      const response = await api.get(`/projects/${projectIdStr}/components`);
      setAvailableComponents(response.data || []);
    } catch (err: any) {
      console.error('Error loading components:', err);
    }
  };

  const loadSignals = async () => {
    if (!finalProjectId) return;
    try {
      setLoading(true);
      setError(null);
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      const data = await getPMSSignals(
        projectIdStr,
        componentFilter || undefined,
        signalTypeFilter || undefined,
        statusFilter || undefined,
        dateFromFilter || undefined,
        dateToFilter || undefined
      );
      setSignals(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load PMS signals');
    } finally {
      setLoading(false);
    }
  };

  const handleAddComponent = () => {
    if (componentInput.trim() && !formData.component_names_json?.includes(componentInput.trim())) {
      setFormData({
        ...formData,
        component_names_json: [...(formData.component_names_json || []), componentInput.trim()]
      });
      setComponentInput('');
    }
  };

  const handleRemoveComponent = (component: string) => {
    setFormData({
      ...formData,
      component_names_json: formData.component_names_json?.filter(c => c !== component) || []
    });
  };

  const handleOpenCreate = () => {
    setEditingSignal(null);
    setFormData({
      signal_key: '',
      signal_type: 'complaint',
      component_names_json: [],
      title: '',
      description: '',
      source_ref: '',
      date_detected: new Date().toISOString().split('T')[0],
      trend_status: 'under_review',
      trigger_status: 'not_triggered',
      status: 'open'
    });
    setShowModal(true);
  };

  const handleOpenEdit = (signal: PMSSignal) => {
    setEditingSignal(signal);
    setFormData({
      signal_key: signal.signal_key,
      signal_type: signal.signal_type,
      component_names_json: signal.component_names_json,
      title: signal.title,
      description: signal.description || '',
      source_ref: signal.source_ref || '',
      date_detected: signal.date_detected.split('T')[0],
      severity_observed: signal.severity_observed,
      frequency_observed: signal.frequency_observed,
      rate_observed: signal.rate_observed,
      trend_status: signal.trend_status,
      trigger_status: signal.trigger_status,
      recommended_action: signal.recommended_action || '',
      owner: signal.owner || '',
      status: signal.status
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!finalProjectId) return;
    try {
      setLoading(true);
      setError(null);
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      
      if (editingSignal) {
        const update: PMSSignalUpdate = {
          ...formData,
          date_detected: formData.date_detected ? new Date(formData.date_detected).toISOString() : undefined
        };
        await updatePMSSignal(projectIdStr, editingSignal.id, update);
      } else {
        const create: PMSSignalCreate = {
          signal_key: formData.signal_key!,
          signal_type: formData.signal_type!,
          component_names_json: formData.component_names_json || [],
          title: formData.title!,
          description: formData.description,
          source_ref: formData.source_ref,
          date_detected: new Date(formData.date_detected || new Date()).toISOString(),
          severity_observed: formData.severity_observed,
          frequency_observed: formData.frequency_observed,
          rate_observed: formData.rate_observed,
          trend_status: formData.trend_status || 'under_review',
          trigger_status: formData.trigger_status || 'not_triggered',
          recommended_action: formData.recommended_action,
          owner: formData.owner,
          status: formData.status || 'open'
        };
        await createPMSSignal(projectIdStr, create);
      }
      
      setShowModal(false);
      loadSignals();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to save PMS signal');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (signalId: string) => {
    if (!finalProjectId || !window.confirm('Are you sure you want to delete this signal?')) return;
    try {
      setLoading(true);
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      await deletePMSSignal(projectIdStr, signalId);
      loadSignals();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to delete PMS signal');
    } finally {
      setLoading(false);
    }
  };

  const handleLinkToRisk = async (signal: PMSSignal) => {
    const riskItemId = prompt('Enter Risk Item ID to link:');
    if (!riskItemId || !finalProjectId) return;
    try {
      setLoading(true);
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      await linkPMSSignalToRisk(projectIdStr, signal.id, { risk_item_id: riskItemId });
      alert('Signal linked to risk item successfully');
      loadSignals();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to link signal to risk');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCAPA = async (signal: PMSSignal) => {
    if (!finalProjectId) return;
    try {
      setLoading(true);
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      const result = await handoffPMSSignalToCAPA(projectIdStr, signal.id, {});
      alert(`CAPA created successfully: ${result.capa_id}`);
      loadSignals();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create CAPA');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChange = async (signal: PMSSignal) => {
    if (!finalProjectId) return;
    try {
      setLoading(true);
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      const result = await handoffPMSSignalToChange(projectIdStr, signal.id, {});
      alert(`Change Control created successfully: ${result.change_id}`);
      loadSignals();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create Change Control');
    } finally {
      setLoading(false);
    }
  };

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Please select a project first.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">PMS Signals</h1>
            <p className="text-gray-600">Manage Post-Market Surveillance signals for {currentProject?.name || 'selected project'}</p>
          </div>
          <button
            onClick={handleOpenCreate}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            + Create Signal
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Filters</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Component</label>
            <input
              type="text"
              value={componentFilter}
              onChange={(e) => setComponentFilter(e.target.value)}
              placeholder="Component name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Signal Type</label>
            <select
              value={signalTypeFilter}
              onChange={(e) => setSignalTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">All</option>
              <option value="complaint">Complaint</option>
              <option value="field_data">Field Data</option>
              <option value="trend">Trend</option>
              <option value="service">Service</option>
              <option value="literature">Literature</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">All</option>
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
            <input
              type="date"
              value={dateFromFilter}
              onChange={(e) => setDateFromFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
            <input
              type="date"
              value={dateToFilter}
              onChange={(e) => setDateToFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
      </div>

      {/* Signals Table */}
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Signals</h2>
        {loading ? (
          <p className="text-gray-600">Loading...</p>
        ) : signals.length === 0 ? (
          <p className="text-gray-600">No signals found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Signal Key</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Components</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trend</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trigger</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {signals.map((signal) => (
                  <tr key={signal.id}>
                    <td className="px-4 py-3 text-sm text-gray-900">{signal.signal_key}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{signal.signal_type}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{signal.title}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{signal.component_names_json.join(', ')}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{signal.date_detected.split('T')[0]}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        signal.trend_status === 'confirmed' ? 'bg-red-100 text-red-800' :
                        signal.trend_status === 'under_review' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {signal.trend_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        signal.trigger_status !== 'not_triggered' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {signal.trigger_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        signal.status === 'open' ? 'bg-yellow-100 text-yellow-800' :
                        signal.status === 'closed' ? 'bg-green-100 text-green-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {signal.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleOpenEdit(signal)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleLinkToRisk(signal)}
                          className="text-purple-700 hover:text-purple-800"
                        >
                          Link Risk
                        </button>
                        <button
                          onClick={() => handleCreateCAPA(signal)}
                          className="text-green-600 hover:text-green-800"
                        >
                          CAPA
                        </button>
                        <button
                          onClick={() => handleCreateChange(signal)}
                          className="text-orange-600 hover:text-orange-800"
                        >
                          Change
                        </button>
                        <button
                          onClick={() => handleDelete(signal.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-200 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-auto">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {editingSignal ? 'Edit Signal' : 'Create Signal'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Signal Key *</label>
                <input
                  type="text"
                  value={formData.signal_key}
                  onChange={(e) => setFormData({ ...formData, signal_key: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Signal Type *</label>
                <select
                  value={formData.signal_type}
                  onChange={(e) => setFormData({ ...formData, signal_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="complaint">Complaint</option>
                  <option value="field_data">Field Data</option>
                  <option value="trend">Trend</option>
                  <option value="service">Service</option>
                  <option value="literature">Literature</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Components *</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={componentInput}
                    onChange={(e) => setComponentInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddComponent()}
                    placeholder="Component name"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                  />
                  <button
                    onClick={handleAddComponent}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.component_names_json?.map((comp, idx) => (
                    <span key={idx} className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {comp}
                      <button onClick={() => handleRemoveComponent(comp)} className="ml-2 text-blue-600">×</button>
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date Detected *</label>
                <input
                  type="date"
                  value={formData.date_detected}
                  onChange={(e) => setFormData({ ...formData, date_detected: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Trend Status</label>
                  <select
                    value={formData.trend_status}
                    onChange={(e) => setFormData({ ...formData, trend_status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="none">None</option>
                    <option value="under_review">Under Review</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="false_alarm">False Alarm</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Trigger Status</label>
                  <select
                    value={formData.trigger_status}
                    onChange={(e) => setFormData({ ...formData, trigger_status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="not_triggered">Not Triggered</option>
                    <option value="risk_review_required">Risk Review Required</option>
                    <option value="capa_required">CAPA Required</option>
                    <option value="change_required">Change Required</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="open">Open</option>
                  <option value="investigating">Investigating</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
            </div>
            
            <div className="flex gap-4 mt-6">
              <button
                onClick={handleSave}
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PmsSignalsPage;

