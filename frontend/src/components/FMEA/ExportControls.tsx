import React from 'react';
import { Box, Button, ButtonGroup } from '@mui/material';
import { Download, PictureAsPdf, TableChart } from '@mui/icons-material';
import { exportApi } from '../../services/apiPhase1';

interface ExportControlsProps {
  projectId: string;
  projectName?: string;
}

const ExportControls: React.FC<ExportControlsProps> = ({ projectId, projectName }) => {
  const handleExportCSV = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const url = exportApi.csv(projectId);
      
      const response = await fetch(url, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${projectName || 'project'}_${projectId}_fmea.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('CSV export error:', error);
      alert('Failed to export CSV. Please try again.');
    }
  };

  const handleExportPDF = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const url = exportApi.pdf(projectId);
      
      const response = await fetch(url, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${projectName || 'project'}_${projectId}_fmea.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('PDF export error:', error);
      alert('Failed to export PDF. Please try again.');
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
      <ButtonGroup variant="outlined" aria-label="export controls">
        <Button
          startIcon={<TableChart />}
          onClick={handleExportCSV}
          disabled={!projectId}
        >
          Export CSV
        </Button>
        <Button
          startIcon={<PictureAsPdf />}
          onClick={handleExportPDF}
          disabled={!projectId}
        >
          Export PDF
        </Button>
      </ButtonGroup>
    </Box>
  );
};

export default ExportControls;

