import React, { useState, useEffect } from 'react';
import './UserProfileModal.css';

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

interface UserProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => void;
}

const UserProfileModal: React.FC<UserProfileModalProps> = ({ isOpen, onClose, onLogout }) => {
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
    if (isOpen) {
      loadUserData();
    }
  }, [isOpen]);

  const loadUserData = () => {
    const userData = localStorage.getItem('user');
    if (userData && userData !== 'undefined' && userData !== 'null') {
      try {
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
      } catch (error) {
        console.error('Error parsing user data:', error);
        setError('Failed to load user data. Please try logging in again.');
      }
    } else {
      setError('No user data found. Please log in again.');
    }
  };

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

  if (!isOpen) return null;

  // Check if we have valid user data before showing the modal
  const userData = localStorage.getItem('user');
  if (!userData || userData === 'undefined' || userData === 'null') {
    return null;
  }

  return (
    <div className="user-profile-modal-overlay" onClick={onClose}>
      <div className="user-profile-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>User Profile</h2>
          <button className="close-button" onClick={onClose}>
            <i className="fa-solid fa-times"></i>
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {!user ? (
          <div className="loading-state">
            <i className="fa-solid fa-spinner fa-spin"></i>
            <p>Loading profile...</p>
          </div>
        ) : (
          <div className="modal-content">
            {/* Profile Header */}
            <div className="profile-header">
              <div className="avatar">
                <span>{user.username.charAt(0).toUpperCase()}</span>
              </div>
              <div className="profile-info">
                <h3>{user.full_name || user.username}</h3>
                <p className="email">{user.email}</p>
                <span className={`role-badge ${user.role}`}>
                  {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                </span>
              </div>
            </div>

            {/* Account Information */}
            <div className="section">
              <h4>Account Information</h4>
              <div className="info-grid">
                <div className="info-item">
                  <label>Username</label>
                  <span>{user.username}</span>
                </div>
                <div className="info-item">
                  <label>Status</label>
                  <span className={`status-badge ${user.is_verified ? 'verified' : 'unverified'}`}>
                    {user.is_verified ? 'Verified' : 'Unverified'}
                  </span>
                </div>
                <div className="info-item">
                  <label>Member Since</label>
                  <span>{formatDate(user.created_at)}</span>
                </div>
                <div className="info-item">
                  <label>Last Login</label>
                  <span>{user.last_login ? formatDate(user.last_login) : 'Never'}</span>
                </div>
              </div>
            </div>

            {/* Personal Information */}
            <div className="section">
              <h4>Personal Information</h4>
              <div className="info-grid">
                <div className="info-item">
                  <label>Full Name</label>
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
                  <label>Email</label>
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
                  <label>Company</label>
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
                  <label>Department</label>
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
                  <label>Phone</label>
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

            {/* Bio */}
            <div className="section">
              <h4>Bio</h4>
              {isEditing ? (
                <textarea
                  name="bio"
                  value={editData.bio}
                  onChange={handleEditChange}
                  placeholder="Tell us about yourself..."
                  rows={3}
                />
              ) : (
                <p className="bio-text">{user.bio || 'No bio provided'}</p>
              )}
            </div>

            {/* Actions */}
            <div className="modal-actions">
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
                    {isLoading ? 'Saving...' : 'Save Changes'}
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
        )}
      </div>
    </div>
  );
};

export default UserProfileModal; 