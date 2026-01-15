import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ProjectProvider } from './contexts/ProjectContext';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { AppShell } from './components/layout/AppShell';
import { ToastProvider } from './components/ui/Toast';
import ErrorBoundary from './components/ErrorBoundary';

import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import NonConformancePage from './pages/NonConformancePage';
import CapaPage from './pages/CapaPage';
import ChangeControlPage from './pages/ChangeControlPage';
import FmeaPage from './pages/FMEAPage';
// Phase 3 pages
import DocumentControlPage from './pages/DocumentControlPage';
import TrainingPage from './pages/TrainingPage';
import AuditPage from './pages/AuditPage';
import SupplierQualityPage from './pages/SupplierQualityPage';
import NCRPage from './pages/NCRPage';
import ComplaintPage from './pages/ComplaintPage';
import EquipmentPage from './pages/EquipmentPage';
import HazardAnalysisPage from './pages/HazardAnalysisPage';
import FaultTreeReportPage from './pages/FaultTreeReportPage';
import RiskManagementReportPage from './pages/RiskManagementReportPage';

import RiskManagementPlanPage from './pages/RiskManagementPlanPage';
import RmfExportPage from './pages/RmfExportPage';
import ResidualRiskReportPage from './pages/ResidualRiskReportPage';
import RiskControlsDocumentationPage from './pages/RiskControlsDocumentationPage';
import RiskControlMeasuresReportPage from './pages/Risk/Reports/RiskControlMeasuresReportPage';
import DesignInputsReportPage from './pages/Design/Reports/DesignInputsReportPage';
import VVEvidenceReportPage from './pages/VV/Reports/VVEvidenceReportPage';
import PmsSignalsPage from './pages/PMS/PmsSignalsPage';
import PmsSignalReportPage from './pages/PMS/PmsSignalReportPage';
import RiskTraceabilityMatrixPage from './pages/RiskTraceabilityMatrixPage';
import ResidualRiskRiskBenefitPage from './pages/ResidualRiskRiskBenefitPage';
import RiskControlImplementationPage from './pages/RiskControlImplementationPage';
import RiskEvaluationReportPage from './pages/RiskEvaluationReportPage';
import CacheClearPage from './pages/CacheClearPage';
import PostMarket from './pages/PostMarket';
import WelcomePage from './pages/WelcomePage';
import ProjectPage from './pages/ProjectPage';
import TracabilityMatrix from './pages/TracabilityMatrix';
import ExportPage from './pages/ExportPage';
import HelpPage from './pages/HelpPage';
import MitigationPage from './pages/MitigationPage';
import AdminPage from './pages/AdminPage';
import EmailManagement from './components/EmailManagement';
import EmailListViewer from './components/EmailListViewer';
import LoginNotifications from './components/LoginNotifications';
import TrialStatusBanner from './components/TrialStatusBanner';
import UsageDashboard from './components/UsageDashboard';
import DashboardPageNew from './pages/DashboardPageNew';
import ProjectDashboardPage from './pages/ProjectDashboardPage';
import ProjectDocumentPage from './pages/ProjectDocumentPage';
import DocumentsPage from './features/docs/DocumentsPage';
import RiskItemListPage from './pages/RiskItems/RiskItemListPage';
import RiskItemDetailPage from './pages/RiskItems/RiskItemDetailPage';
import DesignInputDetailPage from './pages/DesignInputs/DesignInputDetailPage';
import DesignOutputDetailPage from './pages/DesignOutputs/DesignOutputDetailPage';
import VVTestDetailPage from './pages/VVTests/VVTestDetailPage';
import CAPADetailPage from './pages/CAPAs/CAPADetailPage';
import ChangeControlDetailPage from './pages/ChangeControls/ChangeControlDetailPage';
import ProjectFMEAPage from './pages/ProjectFMEAPage';
import ProjectSetupWizard from './pages/ProjectSetupWizard';

function App() {
  return (
    <AuthProvider>
      <ProjectProvider>
        <ToastProvider>
          {/* Opt-in to React Router v7 future behavior to silence future-flag warnings. */}
          <Router future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
            <ProtectedRoute>
              <AppShell>
                <ErrorBoundary>
                  <Routes>
                  <Route path="/" element={<DashboardPageNew />} />
                  <Route path="/dashboard" element={<DashboardPageNew />} />
                  <Route path="/home" element={<HomePage />} />
                  <Route path="/nonconformance" element={<NonConformancePage />} />
                  <Route path="/capa" element={<CapaPage />} />
                  <Route path="/change-control" element={<ChangeControlPage />} />
                  <Route path="/dfmea" element={<FmeaPage />} />
                  <Route path="/projects/:projectId/fmea" element={<ProjectFMEAPage />} />
                  <Route path="/projects/:projectId/setup" element={<ProjectSetupWizard />} />
                  <Route path="/projects/:projectId/dashboard" element={<ProjectDashboardPage />} />
                  {/* Phase 3 Routes */}
                  <Route path="/projects/:projectId/documents" element={<DocumentControlPage />} />
                  <Route path="/projects/:projectId/documents/:docId" element={<ProjectDocumentPage />} />
                  <Route path="/documents" element={<DocumentControlPage />} />
                  {/* SmartQS Documentation Area */}
                  <Route path="/projects/:projectId/docs" element={<DocumentsPage />} />
                  <Route path="/projects/:projectId/docs/:groupId" element={<DocumentsPage />} />
                  <Route path="/projects/:projectId/docs/:groupId/:docTypeId" element={<DocumentsPage />} />
                  <Route path="/training" element={<TrainingPage />} />
                  <Route path="/projects/:projectId/audits" element={<AuditPage />} />
                  <Route path="/audits" element={<AuditPage />} />
                  <Route path="/projects/:projectId/suppliers" element={<SupplierQualityPage />} />
                  <Route path="/suppliers" element={<SupplierQualityPage />} />
                  <Route path="/projects/:projectId/ncrs" element={<NCRPage />} />
                  <Route path="/ncrs" element={<NCRPage />} />
                  <Route path="/projects/:projectId/complaints" element={<ComplaintPage />} />
                  <Route path="/complaints" element={<ComplaintPage />} />
                  <Route path="/projects/:projectId/equipment" element={<EquipmentPage />} />
                  <Route path="/equipment" element={<EquipmentPage />} />
                  <Route path="/projects/:projectId/risk-items" element={<RiskItemListPage />} />
                  <Route path="/projects/:projectId/risk-items/:riskItemId" element={<RiskItemDetailPage />} />
                  <Route path="/risk-items" element={<RiskItemListPage />} />
                  <Route path="/projects/:projectId/design-inputs/:id" element={<DesignInputDetailPage />} />
                  <Route path="/design-inputs/:id" element={<DesignInputDetailPage />} />
                  <Route path="/projects/:projectId/design-outputs/:id" element={<DesignOutputDetailPage />} />
                  <Route path="/design-outputs/:id" element={<DesignOutputDetailPage />} />
                  <Route path="/projects/:projectId/vv-tests/:id" element={<VVTestDetailPage />} />
                  <Route path="/vv-tests/:id" element={<VVTestDetailPage />} />
                  <Route path="/projects/:projectId/capas/:id" element={<CAPADetailPage />} />
                  <Route path="/capas/:id" element={<CAPADetailPage />} />
                  <Route path="/projects/:projectId/change-controls/:id" element={<ChangeControlDetailPage />} />
                  <Route path="/projects/:projectId/changes/:id" element={<ChangeControlDetailPage />} />
                  <Route path="/change-controls/:id" element={<ChangeControlDetailPage />} />
                  <Route path="/hazard-analysis" element={<HazardAnalysisPage />} />
                  <Route path="/fault-tree-report" element={<FaultTreeReportPage />} />
                  <Route path="/risk-management-report" element={<RiskManagementReportPage />} />

                  <Route path="/risk-management-plan" element={<RiskManagementPlanPage />} />
                  <Route path="/risk-management-procedure" element={<RiskManagementPlanPage />} />
                  <Route path="/rmf" element={<RmfExportPage />} />
                  <Route path="/projects/:projectId/rmf" element={<RmfExportPage />} />
                  <Route path="/hazard-analysis" element={<HazardAnalysisPage />} />
                  <Route path="/projects/:projectId/hazard-analysis" element={<HazardAnalysisPage />} />
                  <Route path="/residual-risk" element={<ResidualRiskReportPage />} />
                  <Route path="/projects/:projectId/residual-risk" element={<ResidualRiskReportPage />} />
                  <Route path="/risk-evaluation" element={<ResidualRiskReportPage />} />
                  <Route path="/projects/:projectId/risk-evaluation" element={<ResidualRiskReportPage />} />
                  <Route path="/risk-controls-documentation" element={<RiskControlsDocumentationPage />} />
                  <Route path="/projects/:projectId/risk-controls-documentation" element={<RiskControlsDocumentationPage />} />
                  <Route path="/projects/:projectId/reports/risk-control-measures" element={<RiskControlMeasuresReportPage />} />
                  <Route path="/reports/risk-control-measures" element={<RiskControlMeasuresReportPage />} />
                  <Route path="/projects/:projectId/reports/design-inputs" element={<DesignInputsReportPage />} />
                  <Route path="/reports/design-inputs" element={<DesignInputsReportPage />} />
                  <Route path="/projects/:projectId/reports/vv-evidence" element={<VVEvidenceReportPage />} />
                  <Route path="/reports/vv-evidence" element={<VVEvidenceReportPage />} />
                  <Route path="/projects/:projectId/pms/signals" element={<PmsSignalsPage />} />
                  <Route path="/pms/signals" element={<PmsSignalsPage />} />
                  <Route path="/projects/:projectId/pms/reports/signal-feedback" element={<PmsSignalReportPage />} />
                  <Route path="/pms/reports/signal-feedback" element={<PmsSignalReportPage />} />
                  <Route path="/traceability-matrix" element={<RiskTraceabilityMatrixPage />} />
                  <Route path="/residual-risk" element={<ResidualRiskRiskBenefitPage />} />
                  <Route path="/risk-control-implementation" element={<RiskControlImplementationPage />} />
                  <Route path="/risk-evaluation-report" element={<RiskEvaluationReportPage />} />
                  <Route path="/cache-clear" element={<CacheClearPage />} />
                  <Route path="/post-market" element={<PostMarket />} />
                  <Route path="/welcome" element={<WelcomePage />} />
                  <Route path="/projects" element={<ProjectPage />} />
                  <Route path="/tracability" element={<TracabilityMatrix />} />
                  <Route path="/export" element={<ExportPage />} />
                  <Route path="/help" element={<HelpPage />} />
                  <Route path="/mitigation" element={<MitigationPage />} />
                  <Route path="/admin" element={<AdminPage />} />
                          <Route path="/email-management" element={<EmailManagement />} />
                          <Route path="/email-list" element={<EmailListViewer />} />
                          <Route path="/login-notifications" element={<LoginNotifications />} />
                          <Route path="/usage-dashboard" element={<UsageDashboard />} />
                          <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </ErrorBoundary>
              </AppShell>
            </ProtectedRoute>
          </Router>
        </ToastProvider>
      </ProjectProvider>
    </AuthProvider>
  );
}

export default App;
