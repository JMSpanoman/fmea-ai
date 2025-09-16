import React from 'react';
import TemplateManager from '../components/TemplateManager';

const TemplateManagementPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Template Management</h1>
        <p className="text-gray-600">
          Upload, manage, and organize Word templates for various report types including Risk Management Reports, 
          FMEA Reports, Hazard Analysis, and more.
        </p>
      </div>

      {/* Template Manager */}
      <TemplateManager
        showUpload={true}
        showList={true}
        showActions={true}
      />
    </div>
  );
};

export default TemplateManagementPage;
