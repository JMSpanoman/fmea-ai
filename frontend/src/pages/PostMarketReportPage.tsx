import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import PostMarketReport from '../components/postmarket/PostMarketReport';
import PostMarketReportSummaryCard from '../components/postmarket/PostMarketReportSummaryCard';

/**
 * Project-scoped MAUDE / openFDA structured report (Pro).
 * Route: /projects/:projectId/postmarket-report
 */
const PostMarketReportPage: React.FC = () => {
  const { projectId: paramId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();
  const projectId = paramId || currentProject?.id || '';

  if (!projectId) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <p className="text-gray-700">Select a project to view the post-market report.</p>
        <Link to="/projects" className="text-sky-600 text-sm mt-2 inline-block hover:underline">
          Go to projects
        </Link>
      </div>
    );
  }

  return (
    <div className="postmarket-report-page -m-6 min-h-full max-w-6xl mx-auto p-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 text-sm text-neutral-600">
          <Link to={`/projects/${projectId}/dashboard`} className="text-sky-700 hover:underline">
            ← Mission Control
          </Link>
          <span className="text-neutral-300">|</span>
          <Link to={`/projects/${projectId}/pms/signals`} className="text-sky-700 hover:underline">
            PMS signals
          </Link>
        </div>
      </div>

      <div className="mb-8">
        <PostMarketReportSummaryCard projectId={projectId} autoRefresh />
      </div>

      <PostMarketReport projectId={projectId} />
    </div>
  );
};

export default PostMarketReportPage;
