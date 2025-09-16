import React, { useState } from 'react';
import api from '../axios';

interface TraceabilityItem {
  user_need: string;
  design_input: string;
  design_output: string;
  verification: string;
  validation: string;
}

const TraceabilityMatrix: React.FC = () => {
  const [component, setComponent] = useState('');
  const [matrix, setMatrix] = useState<TraceabilityItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [mock, setMock] = useState<boolean | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await api.post('/fmea/ai/traceability/suggest', { component });
      setMatrix(response.data.matrix);
      setMock(response.data.mock);
    } catch (error) {
      alert('Error generating traceability matrix');
      setMock(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold mb-1">Traceability Matrix Generator</h1>
          <p className="text-gray-600 text-base mb-4">Enter component details and generate an AI-powered Post Market Analysis</p>
          <div className="flex space-x-4 mb-6">
            <input
              type="text"
              value={component}
              onChange={(e) => setComponent(e.target.value)}
              placeholder="Enter component (e.g., infusion pump)"
              className="border p-2 rounded w-1/2"
            />
            <button
              onClick={handleGenerate}
              className="bg-blue-600 text-white px-4 py-2 rounded"
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Matrix'}
            </button>
          </div>

          {mock !== null && (
            <div className="mb-2">
              <span className={`text-xs font-semibold px-2 py-1 rounded ${mock ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}> 
                {mock ? 'Mock Data (not AI generated)' : 'AI Generated Data'}
              </span>
            </div>
          )}

          {matrix.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tl-lg">User Need</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Design Input</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Design Output</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Verification</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tr-lg">Validation</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {matrix.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">{item.user_need}</td>
                      <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">{item.design_input}</td>
                      <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">{item.design_output}</td>
                      <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">{item.verification}</td>
                      <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">{item.validation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default TraceabilityMatrix;
