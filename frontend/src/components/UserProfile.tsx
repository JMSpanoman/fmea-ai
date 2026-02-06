import React, { useState, useEffect } from 'react';
import './UserProfile.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  company: string;
  department: string;
  phone: string;
  bio: string;
  is_verified: boolean;
  created_at: string;
  last_login: string;
}

interface UserProfileProps {
  onLogout: () => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ onLogout }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editData, setEditData] = useState({
    full_name: '',
    email: '',
    company: '',
    department: '',
    phone: '',
    bio: ''
  });

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      setEditData({
        full_name: parsedUser.full_name || '',
        email: parsedUser.email || '',
        company: parsedUser.company || '',
        department: parsedUser.department || '',
        phone: parsedUser.phone || '',
        bio: parsedUser.bio || ''
      });
    }
  }, []);

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setEditData({
      ...editData,
      [e.target.name]: e.target.value
    });
  };

  const handleSaveProfile = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(editData)
      });

      const data = await response.json();

      if (response.ok) {
        setUser(data);
        localStorage.setItem('user', JSON.stringify(data));
        setSuccess('Profile updated successfully!');
        setIsEditing(false);
      } else {
        setError(data.detail || 'Failed to update profile');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelEdit = () => {
    if (user) {
      setEditData({
        full_name: user.full_name || '',
        email: user.email || '',
        company: user.company || '',
        department: user.department || '',
        phone: user.phone || '',
        bio: user.bio || ''
      });
    }
    setIsEditing(false);
    setError('');
    setSuccess('');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!user) {
    return <div className="user-profile-loading">Loading profile...</div>;
  }

  return (
    <div className="user-profile">
      <div className="profile-header">
        <h2>User Profile</h2>
        <div className="profile-actions">
          {!isEditing ? (
            <button
              className="edit-button"
              onClick={() => setIsEditing(true)}
            >
              Edit Profile
            </button>
          ) : (
            <div className="edit-actions">
              <button
                className="save-button"
                onClick={handleSaveProfile}
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save'}
              </button>
              <button
                className="cancel-button"
                onClick={handleCancelEdit}
                disabled={isLoading}
              >
                Cancel
              </button>
            </div>
          )}
          <button
            className="logout-button"
            onClick={onLogout}
          >
            Logout
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="profile-content">
        <div className="profile-section">
          <h3>Account Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>Username:</label>
              <span>{user.username}</span>
            </div>
            <div className="info-item">
              <label>Role:</label>
              <span className={`role-badge ${user.role}`}>
                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </span>
            </div>
            <div className="info-item">
              <label>Status:</label>
              <span className={`status-badge ${user.is_verified ? 'verified' : 'unverified'}`}>
                {user.is_verified ? 'Verified' : 'Unverified'}
              </span>
            </div>
            <div className="info-item">
              <label>Member Since:</label>
              <span>{formatDate(user.created_at)}</span>
            </div>
            <div className="info-item">
              <label>Last Login:</label>
              <span>{user.last_login ? formatDate(user.last_login) : 'Never'}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h3>Personal Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>Full Name:</label>
              {isEditing ? (
                <input
                  type="text"
                  name="full_name"
                  value={editData.full_name}
                  onChange={handleEditChange}
                  placeholder="Enter full name"
                />
              ) : (
                <span>{user.full_name || 'Not provided'}</span>
              )}
            </div>
            <div className="info-item">
              <label>Email:</label>
              {isEditing ? (
                <input
                  type="email"
                  name="email"
                  value={editData.email}
                  onChange={handleEditChange}
                  placeholder="Enter email"
                />
              ) : (
                <span>{user.email}</span>
              )}
            </div>
            <div className="info-item">
              <label>Company:</label>
              {isEditing ? (
                <input
                  type="text"
                  name="company"
                  value={editData.company}
                  onChange={handleEditChange}
                  placeholder="Enter company"
                />
              ) : (
                <span>{user.company || 'Not provided'}</span>
              )}
            </div>
            <div className="info-item">
              <label>Department:</label>
              {isEditing ? (
                <input
                  type="text"
                  name="department"
                  value={editData.department}
                  onChange={handleEditChange}
                  placeholder="Enter department"
                />
              ) : (
                <span>{user.department || 'Not provided'}</span>
              )}
            </div>
            <div className="info-item">
              <label>Phone:</label>
              {isEditing ? (
                <input
                  type="tel"
                  name="phone"
                  value={editData.phone}
                  onChange={handleEditChange}
                  placeholder="Enter phone number"
                />
              ) : (
                <span>{user.phone || 'Not provided'}</span>
              )}
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h3>Bio</h3>
          {isEditing ? (
            <textarea
              name="bio"
              value={editData.bio}
              onChange={handleEditChange}
              placeholder="Tell us about yourself..."
              rows={4}
            />
          ) : (
            <p className="bio-text">{user.bio || 'No bio provided'}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfile; 