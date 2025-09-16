import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Mitigation {
  id: number;
  title: string;
  description: string;
  fda_reference: string;
  category: string;
}

const MitigationPage: React.FC = () => {
  const [mitigations, setMitigations] = useState<Mitigation[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMitigations = async () => {
      setLoading(true);
      try {
        const res = await axios.get('/fmea/mitigations');
        setMitigations(res.data);
        setError(null);
      } catch (err: any) {
        setError('Failed to load mitigations');
      } finally {
        setLoading(false);
      }
    };
    fetchMitigations();
  }, []);

  const filtered = mitigations.filter(m =>
    m.title.toLowerCase().includes(search.toLowerCase()) ||
    m.description.toLowerCase().includes(search.toLowerCase()) ||
    m.fda_reference.toLowerCase().includes(search.toLowerCase()) ||
    m.category.toLowerCase().includes(search.toLowerCase())
  );

  console.log('Mitigations:', mitigations, 'Loading:', loading, 'Error:', error);
  
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Mitigation Library</h1>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4 flex flex-col md:flex-row md:items-center md:justify-between">
            <input
              type="text"
              placeholder="Search mitigations..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="border p-2 rounded w-full md:w-1/3 mb-2 md:mb-0"
            />
            {loading && <span className="text-gray-500 ml-4">Loading...</span>}
            {error && <span className="text-red-500 ml-4">{error}</span>}
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">FDA Reference</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filtered.length === 0 && !loading && (
                  <tr>
                    <td colSpan={4} className="text-center text-gray-400 py-6">No mitigations found.</td>
                  </tr>
                )}
                {filtered.map(m => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-semibold text-gray-900 max-w-xs">{m.title}</td>
                    <td className="px-4 py-3 text-gray-700 max-w-lg">{m.description}</td>
                    <td className="px-4 py-3 text-blue-700 font-mono">{m.fda_reference}</td>
                    <td className="px-4 py-3 text-gray-700">{m.category}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MitigationPage; 