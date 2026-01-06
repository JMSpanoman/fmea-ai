import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useProject } from '../../../contexts/ProjectContext';
import {
  getRiskControlMeasuresData,
  exportRiskControlMeasuresHtml,
  ComponentFilter
} from '../../../services/apiService';
import api from '../../../axios';

const RiskControlMeasuresReportPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();
  const [components, setComponents] = useState<string[]>([]);
  const [componentInput, setComponentInput] = useState('');
  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [availableComponents, setAvailableComponents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Options
  const [activeOnly, setActiveOnly] = useState(true);
  
  // Preview
  const [showPreview, setShowPreview] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [previewData, setPreviewData] = useState<any>(null);
  const [counts, setCounts] = useState<any>(null);

  const finalProjectId = projectId || currentProject?.id;

  useEffect(() => {
    if (finalProjectId) {
      loadComponents();
    }
  }, [finalProjectId]);

  const loadComponents = async () => {
    if (!finalProjectId) return;
    
    try {
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      const response = await api.get(`/projects/${projectIdStr}/components`);
      setAvailableComponents(response.data || []);
    } catch (err: any) {
      console.error('Error loading components:', err);
      setAvailableComponents([]);
    }
  };

  const handleAddComponent = () => {
    if (componentInput.trim() && !components.includes(componentInput.trim())) {
      setComponents([...components, componentInput.trim()]);
      setComponentInput('');
    }
  };

  const handleRemoveComponent = (component: string) => {
    setComponents(components.filter(c => c !== component));
  };

  const handleToggleComponent = (componentId: string) => {
    if (selectedComponents.includes(componentId)) {
      setSelectedComponents(selectedComponents.filter(id => id !== componentId));
    } else {
      setSelectedComponents([...selectedComponents, componentId]);
    }
  };

  const handleGeneratePreview = async () => {
    if (!finalProjectId) {
      setError('Please select a project first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Build component list
      const componentList: string[] = [];
      
      // Add selected components from dropdown
      for (const compId of selectedComponents) {
        const comp = availableComponents.find(c => c.id === compId);
        if (comp) {
          componentList.push(comp.name);
        }
      }
      
      // Add manually entered components
      componentList.push(...components);
      
      const componentsStr = componentList.length > 0 ? componentList.join(',') : undefined;

      const data = await getRiskControlMeasuresData(
        finalProjectId,
        componentsStr,
        activeOnly
      );
      
      setPreviewData(data);
      setCounts(data.counts);
      setShowPreview(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate Risk Control Measures report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportHTML = async () => {
    if (!finalProjectId) return;

    try {
      setLoading(true);
      setError(null);
      
      // Build component list
      const componentList: string[] = [];
      
      for (const compId of selectedComponents) {
        const comp = availableComponents.find(c => c.id === compId);
        if (comp) {
          componentList.push(comp.name);
        }
      }
      
      componentList.push(...components);
      
      const componentsStr = componentList.length > 0 ? componentList.join(',') : undefined;
      const html = await exportRiskControlMeasuresHtml(
        finalProjectId,
        componentsStr,
        activeOnly
      );
      
      // Open in new tab
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const newWindow = window.open(url, '_blank');
      if (newWindow) {
        newWindow.onload = () => URL.revokeObjectURL(url);
      } else {
        // Fallback to download
        const a = document.createElement('a');
        a.href = url;
        a.download = `Risk_Control_Measures_${currentProject?.name || 'report'}_${new Date().toISOString().split('T')[0]}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to export Risk Control Measures HTML');
    } finally {
      setLoading(false);
    }
  };

  // Group data by component and risk
  const groupedData = React.useMemo(() => {
    if (!previewData?.rows) return {};
    
    const grouped: Record<string, Record<string, any[]>> = {};
    
    previewData.rows.forEach((row: any) => {
      const compName = row.component_name || 'Unknown';
      const riskKey = row.risk_key || 'Unknown';
      
      if (!grouped[compName]) {
        grouped[compName] = {};
      }
      if (!grouped[compName][riskKey]) {
        grouped[compName][riskKey] = [];
      }
      
      grouped[compName][riskKey].push(row);
    });
    
    return grouped;
  }, [previewData]);

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Please select a project first to generate Risk Control Measures report.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Control Measures Report</h1>
        <p className="text-gray-600">Generate documentation of risk control measures for {currentProject?.name || 'selected project'}</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Component Selection</h2>
        
        {availableComponents.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select from Project Components</label>
            <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-300 rounded-md p-3">
              {availableComponents.map((comp) => (
                <label key={comp.id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedComponents.includes(comp.id)}
                    onChange={() => handleToggleComponent(comp.id)}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm text-gray-900">{comp.name}</span>
                </label>
              ))}
            </div>
          </div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Or Enter Component Names</label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={componentInput}
              onChange={(e) => setComponentInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddComponent()}
              placeholder="Component name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleAddComponent}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Add
            </button>
          </div>
          {components.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {components.map((comp, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {comp}
                  <button
                    onClick={() => handleRemoveComponent(comp)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
          <p className="text-sm text-gray-500 mt-2">
            Leave empty to include all components
          </p>
        </div>
      </div>

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Options</h2>
        
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
            className="rounded border-gray-300"
          />
          <span className="text-sm text-gray-900">Active controls only (Default)</span>
        </label>
      </div>

      {counts && (
        <div className="bg-gray-200 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Controls</p>
              <p className="text-2xl font-bold text-gray-900">{counts.controls || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Missing Implementation</p>
              <p className="text-2xl font-bold text-gray-900">{counts.missing_implementation || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Missing Verification</p>
              <p className="text-2xl font-bold text-gray-900">{counts.missing_verification || 0}</p>
            </div>
          </div>
        </div>
      )}

      {/* Preview Table - Grouped by Component → Risk Key → Controls */}
      {previewData && Object.keys(groupedData).length > 0 && (
        <div className="bg-gray-200 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Preview</h2>
          <div className="space-y-6">
            {Object.entries(groupedData).map(([componentName, risks]) => (
              <div key={componentName} className="border border-gray-300 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Component: {componentName}</h3>
                {Object.entries(risks).map(([riskKey, controls]) => (
                  <div key={riskKey} className="mb-4 pl-4 border-l-2 border-blue-500">
                    <h4 className="text-md font-medium text-gray-800 mb-2">Risk: {riskKey}</h4>
                    <div className="space-y-3">
                      {controls.map((control: any, index: number) => (
                        <div key={index} className="bg-white rounded p-3 border border-gray-200">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-semibold text-gray-900">{control.control_key}</span>
                            <span className="text-gray-700">{control.control_name}</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              control.control_type.includes('inherent') ? 'bg-blue-100 text-blue-800' :
                              control.control_type.includes('protective') ? 'bg-green-100 text-green-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {control.control_type}
                            </span>
                            {control.flags.missing_implementation && (
                              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs font-medium">
                                Missing Implementation
                              </span>
                            )}
                            {control.flags.missing_verification && (
                              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs font-medium">
                                Missing Verification
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{control.control_description || 'No description'}</p>
                          {control.implementation_refs.length > 0 && (
                            <div className="mb-2">
                              <p className="text-xs font-medium text-gray-700 mb-1">Implementation References:</p>
                              <ul className="list-disc list-inside text-xs text-gray-600">
                                {control.implementation_refs.map((ref: any, i: number) => (
                                  <li key={i}>{ref.display}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {control.verification_methods.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-gray-700 mb-1">Verification Methods:</p>
                              <ul className="list-disc list-inside text-xs text-gray-600">
                                {control.verification_methods.map((method: any, i: number) => (
                                  <li key={i}>{method.display}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={handleGeneratePreview}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Preview'}
        </button>
        {previewData && (
          <button
            onClick={handleExportHTML}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            Export HTML
          </button>
        )}
      </div>
    </div>
  );
};

export default RiskControlMeasuresReportPage;

