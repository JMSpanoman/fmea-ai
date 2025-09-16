// Export utility functions for CSV and PDF exports

export interface ExportData {
  [key: string]: any;
}

export interface ExportColumn {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'severity' | 'status' | 'rpn';
}

// Helper function to convert data to CSV
export const convertToCSV = (data: ExportData[]): string => {
  if (data.length === 0) return '';
  
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row => 
      headers.map(header => {
        const value = row[header] || '';
        const escapedValue = String(value).replace(/"/g, '""');
        return `"${escapedValue}"`;
      }).join(',')
    )
  ].join('\n');
  
  return csvContent;
};

// Helper function to download CSV
export const downloadCSV = (csvContent: string, filename: string): void => {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}-${Date.now()}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// CSV Export Functions
export const exportToCSV = (data: ExportData[], columns: ExportColumn[], filename: string) => {
  if (data.length === 0) {
    alert('No data to export');
    return;
  }

  const headers = columns.map(col => col.label);
  const csvContent = [
    headers.join(','),
    ...data.map(row => 
      columns.map(col => {
        const value = row[col.key] || '';
        // Escape quotes and wrap in quotes if contains comma or newline
        const escapedValue = String(value).replace(/"/g, '""');
        return `"${escapedValue}"`;
      }).join(',')
    )
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}-${Date.now()}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// PDF Export Functions
export const exportToPDF = async (data: ExportData[], columns: ExportColumn[], filename: string, title: string) => {
  if (data.length === 0) {
    alert('No data to export');
    return;
  }

  try {
    // Dynamic import of jsPDF to avoid bundle size issues
    const { default: jsPDF } = await import('jspdf');
    const { default: autoTable } = await import('jspdf-autotable');

    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(16);
    doc.text(title, 14, 20);
    
    // Add timestamp
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 30);

    // Prepare table data
    const tableData = data.map(row => 
      columns.map(col => {
        const value = row[col.key] || '';
        return String(value);
      })
    );

    // Add table
    autoTable(doc, {
      head: [columns.map(col => col.label)],
      body: tableData,
      startY: 40,
      styles: {
        fontSize: 8,
        cellPadding: 2,
      },
      headStyles: {
        fillColor: [66, 139, 202],
        textColor: 255,
        fontStyle: 'bold',
      },
      alternateRowStyles: {
        fillColor: [245, 245, 245],
      },
      margin: { top: 40, right: 14, bottom: 14, left: 14 },
    });

    // Save PDF
    doc.save(`${filename}-${Date.now()}.pdf`);
  } catch (error) {
    console.error('PDF export error:', error);
    alert('Failed to export PDF. Please try again.');
  }
};

// FMEA Export Functions
export const exportFmeaData = (data: any[], format: 'csv' | 'pdf') => {
  const columns: ExportColumn[] = [
    { key: 'component', label: 'Component' },
    { key: 'location', label: 'Location' },
    { key: 'failure_mode', label: 'Failure Mode' },
    { key: 'effect', label: 'Effect' },
    { key: 'severity', label: 'Severity', type: 'severity' },
    { key: 'probability', label: 'Probability' },
    { key: 'detection', label: 'Detection' },
    { key: 'rpn', label: 'RPN', type: 'rpn' },
    { key: 'mitigation', label: 'Mitigation' },
    { key: 'action_taken', label: 'Action Taken' },
    { key: 'revised_severity', label: 'Post-Mitigation Severity', type: 'severity' },
    { key: 'revised_probability', label: 'Post-Mitigation Probability' },
    { key: 'revised_detection', label: 'Post-Mitigation Detection' },
    { key: 'revised_rpn', label: 'Post-Mitigation RPN', type: 'rpn' },
  ];

  if (format === 'csv') {
    exportToCSV(data, columns, 'fmea-analysis');
  } else {
    exportToPDF(data, columns, 'fmea-analysis', 'FMEA Analysis Report');
  }
};

// CAPA Export Functions
export const exportCapaData = (data: any[], format: 'csv' | 'pdf') => {
  const columns: ExportColumn[] = [
    { key: 'issueDescription', label: 'Issue Description' },
    { key: 'source', label: 'Source' },
    { key: 'detectionDate', label: 'Detection Date' },
    { key: 'severity', label: 'Severity', type: 'severity' },
    { key: 'rootCause', label: 'Root Cause' },
    { key: 'correctiveAction', label: 'Corrective Action' },
    { key: 'preventiveAction', label: 'Preventive Action' },
    { key: 'actionOwner', label: 'Action Owner' },
    { key: 'dueDate', label: 'Due Date' },
    { key: 'status', label: 'Status', type: 'status' },
    { key: 'effectivenessCheckPlan', label: 'Effectiveness Check Plan' },
    { key: 'fmeaLink', label: 'FMEA Link' },
    { key: 'regulatoryImpact', label: 'Regulatory Impact' },
    { key: 'closureSummary', label: 'Closure Summary' },
  ];

  if (format === 'csv') {
    exportToCSV(data, columns, 'capa-analysis');
  } else {
    exportToPDF(data, columns, 'capa-analysis', 'CAPA Analysis Report');
  }
};

// Non-Conformance Export Functions
export const exportNonConformanceData = (data: any[], format: 'csv' | 'pdf') => {
  const columns: ExportColumn[] = [
    { key: 'issueDescription', label: 'Issue Description' },
    { key: 'source', label: 'Source' },
    { key: 'detectionDate', label: 'Detection Date' },
    { key: 'severity', label: 'Severity', type: 'severity' },
    { key: 'rootCause', label: 'Root Cause' },
    { key: 'correctiveAction', label: 'Corrective Action' },
    { key: 'preventiveAction', label: 'Preventive Action' },
    { key: 'actionOwner', label: 'Action Owner' },
    { key: 'dueDate', label: 'Due Date' },
    { key: 'status', label: 'Status', type: 'status' },
    { key: 'effectivenessCheckPlan', label: 'Effectiveness Check Plan' },
    { key: 'fmeaLink', label: 'FMEA Link' },
    { key: 'regulatoryImpact', label: 'Regulatory Impact' },
    { key: 'closureSummary', label: 'Closure Summary' },
  ];

  if (format === 'csv') {
    exportToCSV(data, columns, 'non-conformance-analysis');
  } else {
    exportToPDF(data, columns, 'non-conformance-analysis', 'Non-Conformance Analysis Report');
  }
};

// Fault Tree Report Export Functions
export const exportFaultTreeReportData = (data: any[], filename: string) => {
  const columns: ExportColumn[] = [
    { key: 'topEvent', label: 'Top Event' },
    { key: 'faultTreeType', label: 'Fault Tree Type' },
    { key: 'complexity', label: 'Complexity', type: 'severity' },
    { key: 'riskLevel', label: 'Risk Level', type: 'severity' },
    { key: 'rootCauses', label: 'Root Causes' },
    { key: 'intermediateEvents', label: 'Intermediate Events' },
    { key: 'basicEvents', label: 'Basic Events' },
    { key: 'probability', label: 'Probability' },
    { key: 'cutSets', label: 'Cut Sets' },
    { key: 'minimalCutSets', label: 'Minimal Cut Sets' },
    { key: 'riskAssessment', label: 'Risk Assessment' },
    { key: 'mitigationStrategies', label: 'Mitigation Strategies' },
    { key: 'responsibleParty', label: 'Responsible Party' },
    { key: 'targetDate', label: 'Target Date' },
    { key: 'status', label: 'Status', type: 'status' },
    { key: 'analysisMethod', label: 'Analysis Method' },
    { key: 'fmeaLink', label: 'FMEA Link' },
    { key: 'regulatoryRequirements', label: 'Regulatory Requirements' },
    { key: 'closureSummary', label: 'Closure Summary' },
    { key: 'milestones', label: 'Milestones' },
    { key: 'riskControlsUpdate', label: 'Risk Controls Update' },
  ];

  // Default to CSV export
  exportToCSV(data, columns, filename);
};

// Hazard Analysis Export Functions
export const exportHazardAnalysisData = (data: any[], filename: string) => {
  const columns: ExportColumn[] = [
    { key: 'hazardDescription', label: 'Hazard Description' },
    { key: 'hazardType', label: 'Hazard Type' },
    { key: 'severity', label: 'Severity', type: 'severity' },
    { key: 'probability', label: 'Probability' },
    { key: 'riskLevel', label: 'Risk Level', type: 'severity' },
    { key: 'affectedComponents', label: 'Affected Components' },
    { key: 'potentialConsequences', label: 'Potential Consequences' },
    { key: 'existingControls', label: 'Existing Controls' },
    { key: 'riskAssessment', label: 'Risk Assessment' },
    { key: 'mitigationMeasures', label: 'Mitigation Measures' },
    { key: 'responsibleParty', label: 'Responsible Party' },
    { key: 'targetDate', label: 'Target Date' },
    { key: 'status', label: 'Status', type: 'status' },
    { key: 'monitoringPlan', label: 'Monitoring Plan' },
    { key: 'fmeaLink', label: 'FMEA Link' },
    { key: 'regulatoryRequirements', label: 'Regulatory Requirements' },
    { key: 'closureSummary', label: 'Closure Summary' },
    { key: 'milestones', label: 'Milestones' },
    { key: 'riskControlsUpdate', label: 'Risk Controls Update' },
  ];

  // Default to CSV export
  exportToCSV(data, columns, filename);
};

// Change Control Export Functions
export const exportChangeControlData = (data: any[], format: 'csv' | 'pdf') => {
  const columns: ExportColumn[] = [
    { key: 'changeDescription', label: 'Change Description' },
    { key: 'changeType', label: 'Change Type' },
    { key: 'requestor', label: 'Requestor' },
    { key: 'requestDate', label: 'Request Date' },
    { key: 'priority', label: 'Priority', type: 'status' },
    { key: 'impactLevel', label: 'Impact Level', type: 'status' },
    { key: 'affectedComponents', label: 'Affected Components' },
    { key: 'justification', label: 'Justification' },
    { key: 'proposedSolution', label: 'Proposed Solution' },
    { key: 'riskAssessment', label: 'Risk Assessment' },
    { key: 'approvalStatus', label: 'Approval Status', type: 'status' },
    { key: 'approvedBy', label: 'Approved By' },
    { key: 'approvalDate', label: 'Approval Date' },
    { key: 'implementationPlan', label: 'Implementation Plan' },
    { key: 'verificationPlan', label: 'Verification Plan' },
    { key: 'linkedFmea', label: 'Linked FMEA' },
    { key: 'linkedCapa', label: 'Linked CAPA' },
    { key: 'linkedNonConformance', label: 'Linked Non-Conformance' },
    { key: 'regulatoryImpact', label: 'Regulatory Impact' },
    { key: 'closureSummary', label: 'Closure Summary' },
  ];

  if (format === 'csv') {
    exportToCSV(data, columns, 'change-control-analysis');
  } else {
    exportToPDF(data, columns, 'change-control-analysis', 'Change Control Analysis Report');
  }
};

// Risk Control Implementation Export Functions
export const exportRiskControlImplementationData = (data: any[], filename: string) => {
  const columns: ExportColumn[] = [
    { key: 'controlName', label: 'Control Name' },
    { key: 'controlType', label: 'Control Type' },
    { key: 'riskCategory', label: 'Risk Category' },
    { key: 'riskLevel', label: 'Risk Level', type: 'severity' },
    { key: 'controlPriority', label: 'Control Priority', type: 'severity' },
    { key: 'implementationStatus', label: 'Implementation Status', type: 'status' },
    { key: 'controlDescription', label: 'Control Description' },
    { key: 'controlObjectives', label: 'Control Objectives' },
    { key: 'controlMechanisms', label: 'Control Mechanisms' },
    { key: 'controlFrequency', label: 'Control Frequency' },
    { key: 'controlEffectiveness', label: 'Control Effectiveness' },
    { key: 'controlOwner', label: 'Control Owner' },
    { key: 'responsibleTeam', label: 'Responsible Team' },
    { key: 'targetCompletionDate', label: 'Target Completion Date' },
    { key: 'actualCompletionDate', label: 'Actual Completion Date' },
    { key: 'implementationCost', label: 'Implementation Cost' },
    { key: 'resourceRequirements', label: 'Resource Requirements' },
    { key: 'trainingRequirements', label: 'Training Requirements' },
    { key: 'monitoringPlan', label: 'Monitoring Plan' },
    { key: 'keyPerformanceIndicators', label: 'Key Performance Indicators' },
    { key: 'successCriteria', label: 'Success Criteria' },
    { key: 'riskAssessmentMethod', label: 'Risk Assessment Method' },
    { key: 'fmeaLink', label: 'FMEA Link' },
    { key: 'regulatoryRequirements', label: 'Regulatory Requirements' },
    { key: 'implementationSummary', label: 'Implementation Summary' },
    { key: 'lessonsLearned', label: 'Lessons Learned' },
    { key: 'nextSteps', label: 'Next Steps' },
    { key: 'controlDocumentation', label: 'Control Documentation' },
  ];

  // Default to CSV export
  exportToCSV(data, columns, filename);
}; 

// Risk Evaluation Report Export Functions
export const exportRiskEvaluationReportData = (data: any[], filename: string) => {
  // Export to CSV
  const csvContent = convertToCSV(data);
  downloadCSV(csvContent, filename);

  // Export to PDF
  exportToPDF(data, [], filename, 'Risk Evaluation Report');
};

export const exportResidualRiskRiskBenefitData = (data: any[], filename: string) => {
  // Export to CSV
  const csvContent = convertToCSV(data);
  downloadCSV(csvContent, filename);

  // Export to PDF
  exportToPDF(data, [], filename, 'Residual Risk & Risk-Benefit Analysis');
};

export const exportRiskTraceabilityMatrixData = (data: any[], filename: string) => {
  // Export to CSV
  const csvContent = convertToCSV(data);
  downloadCSV(csvContent, filename);

  // Export to PDF
  exportToPDF(data, [], filename, 'Risk Traceability Matrix');
};

export const exportRiskManagementPlanData = (data: any[], filename: string) => {
  // Export to CSV
  const csvContent = convertToCSV(data);
  downloadCSV(csvContent, filename);

  // Export to PDF
  exportToPDF(data, [], filename, 'Risk Management Plan');
};

export const exportRiskManagementReportData = (data: any[], filename: string) => {
  // Export to CSV
  const csvContent = convertToCSV(data);
  downloadCSV(csvContent, filename);

  // Export to PDF
  exportToPDF(data, [], filename, 'Risk Management Report');
}; 