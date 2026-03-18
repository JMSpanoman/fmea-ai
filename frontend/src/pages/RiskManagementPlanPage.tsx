import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import authService from '../services/authService';
import { documentsApi } from '../services/apiPhase3';
import type { Document } from '../types';

const RiskManagementPlanPage: React.FC = () => {
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (!authService.isAuthenticated()) {
          await authService.authenticate();
        }
      } catch (error) {
        console.error('Failed to authenticate:', error);
        setError('Failed to authenticate. Please refresh the page.');
      } finally {
        setIsAuthenticating(false);
      }
    };

    initAuth();
  }, []);

  useEffect(() => {
    const go = async () => {
      if (isAuthenticating) return;
      if (!currentProject?.id) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      // Ensure authentication before making API calls
      if (!authService.isAuthenticated()) {
        try {
          await authService.authenticate();
        } catch {
          setError('Failed to authenticate. Please refresh the page.');
          setLoading(false);
          return;
        }
      }

      try {
        const docs = await documentsApi.getAll(currentProject.id);
        const rmpDoc = (docs as Document[]).find((d) => (d.type || '').toLowerCase() === 'rmp');
        if (rmpDoc) {
          navigate(`/projects/${currentProject.id}/documents/${rmpDoc.id}`);
          return;
        }

        // If not found, still send the user to the project dashboard where they can reload/backfill.
        navigate(`/projects/${currentProject.id}/dashboard`);
      } catch (e: any) {
        setError(e?.message || 'Failed to locate the Risk Management Plan document.');
        setLoading(false);
      }
    };

    go();
  }, [currentProject?.id, isAuthenticating, navigate]);

  if (isAuthenticating || loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-gray-600">Opening Risk Management Plan…</span>
        </div>
      </div>
    );
  }

  if (!currentProject) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Select or create a project to continue.</p>
          <button
            className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            onClick={() => navigate('/projects')}
          >
            Go to Projects
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-700">
          Couldn’t auto-open the Risk Management Plan. Use the Project Dashboard to open it.
        </p>
        <button
          className="mt-4 bg-purple-300 text-gray-900 px-4 py-2 rounded-md hover:bg-purple-400"
          onClick={() => navigate(`/projects/${currentProject.id}/dashboard`)}
        >
          Go to Project Dashboard
        </button>
      </div>
    </div>
  );
};

export default RiskManagementPlanPage;
