import React, { useEffect, useState } from 'react';
import Footer from '../components/Footer';

const API_URL = 'http://localhost:8000';

const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editRoles, setEditRoles] = useState<{ [userId: number]: string }>({});
  const [saving, setSaving] = useState<{ [userId: number]: boolean }>({});

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/admin/users`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('jwt')}` },
      });
      if (!res.ok) throw new Error('Failed to fetch users');
      const data = await res.json();
      setUsers(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = (userId: number, value: string) => {
    setEditRoles((prev) => ({ ...prev, [userId]: value }));
  };

  const handleSaveRoles = async (userId: number) => {
    setSaving((prev) => ({ ...prev, [userId]: true }));
    try {
      const roles = editRoles[userId].split(',').map((r) => r.trim()).filter(Boolean);
      const res = await fetch(`${API_URL}/admin/users/${userId}/roles`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('jwt')}`,
        },
        body: JSON.stringify(roles),
      });
      if (!res.ok) throw new Error('Failed to update roles');
      await fetchUsers();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving((prev) => ({ ...prev, [userId]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-4">User Role Management</h1>
        {loading ? (
          <div>Loading users...</div>
        ) : error ? (
          <div className="text-red-600">Error: {error}</div>
        ) : (
          <table className="w-full border-collapse border border-gray-300 text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border p-2">Email</th>
                <th className="border p-2">Name</th>
                <th className="border p-2">Roles</th>
                <th className="border p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="border p-2">{user.email}</td>
                  <td className="border p-2">{user.name}</td>
                  <td className="border p-2">
                    <input
                      type="text"
                      value={editRoles[user.id] ?? user.roles.join(',')}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="border p-1 rounded w-40"
                    />
                  </td>
                  <td className="border p-2">
                    <button
                      className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                      onClick={() => handleSaveRoles(user.id)}
                      disabled={saving[user.id]}
                    >
                      {saving[user.id] ? 'Saving...' : 'Save'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default AdminPage; 