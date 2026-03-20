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
import { LibrariesLayout } from './pages/libraries/LibrariesLayout';
import HazardLibraryPage from './pages/libraries/HazardLibraryPage';
import HarmLibraryPage from './pages/libraries/HarmLibraryPage';
import RiskControlLibraryPage from './pages/libraries/RiskControlLibraryPage';
import VerificationLibraryPage from './pages/libraries/VerificationLibraryPage';
import HazardGenerationRulesPage from './pages/libraries/HazardGenerationRulesPage';
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
import LandingPage from './pages/LandingPage';
import ProjectDashboardPage from './pages/ProjectDashboardPage';
import ProjectDocumentPage from './pages/ProjectDocumentPage';
import DocumentsPage from './features/docs/DocumentsPage';
import RiskItemListPage from './pages/RiskItems/RiskItemListPage';
import DeviceArchitecturePage from './pages/DeviceArchitecturePage';
import ComponentDetailPage from './pages/ComponentDetailPage';
import ProjectRiskOutputsPage from './pages/ProjectRiskOutputsPage';
import RiskAcceptabilityCriteriaPage from './pages/RiskAcceptabilityCriteriaPage';
import ProjectRiskRuleCriteriaPage from './pages/ProjectRiskRuleCriteriaPage';
import RiskItemDetailPage from './pages/RiskItems/RiskItemDetailPage';
import DesignInputDetailPage from './pages/DesignInputs/DesignInputDetailPage';
import DesignOutputDetailPage from './pages/DesignOutputs/DesignOutputDetailPage';
import VVTestDetailPage from './pages/VVTests/VVTestDetailPage';
import CAPADetailPage from './pages/CAPAs/CAPADetailPage';
import ChangeControlDetailPage from './pages/ChangeControls/ChangeControlDetailPage';
import ProjectFMEAPage from './pages/ProjectFMEAPage';
import ProjectSetupWizard from './pages/ProjectSetupWizard';
import { Api403ProListener } from './components/Api403ProListener';
import { ProRoute } from './components/ProRoute';
import DeviceRiskLayout from './pages/DeviceRisk/DeviceRiskLayout';
import DeviceFmeaPage from './pages/DeviceRisk/DeviceFmeaPage';
import DeviceHazardAnalysisPage from './pages/DeviceRisk/DeviceHazardAnalysisPage';
import DeviceRiskTraceabilityPage from './pages/DeviceRisk/DeviceRiskTraceabilityPage';
import DeviceResidualRiskPage from './pages/DeviceRisk/DeviceResidualRiskPage';
import DeviceReportPage from './pages/DeviceRisk/DeviceReportPage';
import DevicesListPage from './pages/Devices/DevicesListPage';
import DeviceDetailPage from './pages/Devices/DeviceDetailPage';
import DeviceComponentsPage from './pages/Devices/DeviceComponentsPage';
import DeviceComponentDetailPage from './pages/Devices/DeviceComponentDetailPage';
import DeviceRiskItemsPage from './pages/DeviceRisk/DeviceRiskItemsPage';

function App() {
  return (
    <AuthProvider>
      <ProjectProvider>
        <ToastProvider>
          <Api403ProListener />
          {/* Opt-in to React Router v7 future behavior to silence future-flag warnings. */}
          <Router future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
            <ProtectedRoute>
              <AppShell>
                <ErrorBoundary>
                  <Routes>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/dashboard" element={<LandingPage />} />
                  <Route path="/home" element={<HomePage />} />
                  <Route path="/nonconformance" element={<NonConformancePage />} />
                  <Route path="/capa" element={<CapaPage />} />
                  <Route path="/change-control" element={<ChangeControlPage />} />
                  <Route path="/dfmea" element={<FmeaPage />} />
                  {/* Pro-only project routes */}
                  <Route path="/projects" element={<ProRoute />}>
                    <Route index element={<ProjectPage />} />
                    <Route path=":projectId/fmea" element={<ProjectFMEAPage />} />
                    <Route path=":projectId/setup" element={<ProjectSetupWizard />} />
                    <Route path=":projectId/dashboard" element={<ProjectDashboardPage />} />
                    <Route path=":projectId/documents" element={<DocumentControlPage />} />
                    <Route path=":projectId/documents/:docId" element={<ProjectDocumentPage />} />
                    <Route path=":projectId/docs" element={<DocumentsPage />} />
                    <Route path=":projectId/docs/:groupId" element={<DocumentsPage />} />
                    <Route path=":projectId/docs/:groupId/:docTypeId" element={<DocumentsPage />} />
                    <Route path=":projectId/audits" element={<AuditPage />} />
                    <Route path=":projectId/suppliers" element={<SupplierQualityPage />} />
                    <Route path=":projectId/ncrs" element={<NCRPage />} />
                    <Route path=":projectId/complaints" element={<ComplaintPage />} />
                    <Route path=":projectId/equipment" element={<EquipmentPage />} />
                    <Route path=":projectId/risk-items" element={<RiskItemListPage />} />
                    <Route path=":projectId/risk-items/:riskItemId" element={<RiskItemDetailPage />} />
                    <Route path=":projectId/design-inputs/:id" element={<DesignInputDetailPage />} />
                    <Route path=":projectId/design-outputs/:id" element={<DesignOutputDetailPage />} />
                    <Route path=":projectId/vv-tests/:id" element={<VVTestDetailPage />} />
                    <Route path=":projectId/capas/:id" element={<CAPADetailPage />} />
                    <Route path=":projectId/change-controls/:id" element={<ChangeControlDetailPage />} />
                    <Route path=":projectId/changes/:id" element={<ChangeControlDetailPage />} />
                    <Route path=":projectId/rmf" element={<RmfExportPage />} />
                    <Route path=":projectId/hazard-analysis" element={<HazardAnalysisPage />} />
                    <Route path=":projectId/risk-acceptability-criteria" element={<RiskAcceptabilityCriteriaPage />} />
                    <Route path=":projectId/risk-rule-criteria" element={<ProjectRiskRuleCriteriaPage />} />
                    <Route path=":projectId/residual-risk" element={<ResidualRiskReportPage />} />
                    <Route path=":projectId/risk-evaluation" element={<ResidualRiskReportPage />} />
                    <Route path=":projectId/risk-controls-documentation" element={<RiskControlsDocumentationPage />} />
                    <Route path=":projectId/reports/risk-control-measures" element={<RiskControlMeasuresReportPage />} />
                    <Route path=":projectId/reports/design-inputs" element={<DesignInputsReportPage />} />
                    <Route path=":projectId/reports/vv-evidence" element={<VVEvidenceReportPage />} />
                    <Route path=":projectId/pms/signals" element={<PmsSignalsPage />} />
                    <Route path=":projectId/pms/reports/signal-feedback" element={<PmsSignalReportPage />} />
                    <Route path=":projectId/device-architecture" element={<DeviceArchitecturePage />} />
                    <Route path=":projectId/components/:componentId" element={<ComponentDetailPage />} />
                    <Route path=":projectId/risk-outputs" element={<ProjectRiskOutputsPage />} />
                  </Route>
                  {/* Devices: list, detail, components, risk outputs */}
                  <Route path="/devices" element={<ProRoute />}>
                    <Route index element={<DevicesListPage />} />
                    <Route path=":id" element={<DeviceRiskLayout />}>
                      <Route index element={<DeviceDetailPage />} />
                      <Route path="components" element={<DeviceComponentsPage />} />
                      <Route path="components/:componentId" element={<DeviceComponentDetailPage />} />
                      <Route path="risk-items" element={<DeviceRiskItemsPage />} />
                      <Route path="fmea" element={<DeviceFmeaPage />} />
                      <Route path="hazard-analysis" element={<DeviceHazardAnalysisPage />} />
                      <Route path="risk-traceability" element={<DeviceRiskTraceabilityPage />} />
                      <Route path="residual-risk" element={<DeviceResidualRiskPage />} />
                      <Route path="report" element={<DeviceReportPage />} />
                    </Route>
                  </Route>
                  <Route path="/documents" element={<DocumentControlPage />} />
                  <Route path="/training" element={<TrainingPage />} />
                  <Route path="/audits" element={<AuditPage />} />
                  <Route path="/suppliers" element={<SupplierQualityPage />} />
                  <Route path="/ncrs" element={<NCRPage />} />
                  <Route path="/complaints" element={<ComplaintPage />} />
                  <Route path="/equipment" element={<EquipmentPage />} />
                  <Route path="/risk-items" element={<RiskItemListPage />} />
                  <Route path="/design-inputs/:id" element={<DesignInputDetailPage />} />
                  <Route path="/design-outputs/:id" element={<DesignOutputDetailPage />} />
                  <Route path="/vv-tests/:id" element={<VVTestDetailPage />} />
                  <Route path="/capas/:id" element={<CAPADetailPage />} />
                  <Route path="/change-controls/:id" element={<ChangeControlDetailPage />} />
                  <Route path="/hazard-analysis" element={<HazardAnalysisPage />} />
                  <Route path="/fault-tree-report" element={<FaultTreeReportPage />} />
                  <Route path="/risk-management-report" element={<RiskManagementReportPage />} />
                  <Route path="/libraries" element={<LibrariesLayout />}>
                    <Route index element={<Navigate to="/libraries/hazards" replace />} />
                    <Route path="hazards" element={<HazardLibraryPage />} />
                    <Route path="harms" element={<HarmLibraryPage />} />
                    <Route path="risk-controls" element={<RiskControlLibraryPage />} />
                    <Route path="verifications" element={<VerificationLibraryPage />} />
                    <Route path="hazard-rules" element={<HazardGenerationRulesPage />} />
                  </Route>

                  <Route path="/risk-management-plan" element={<RiskManagementPlanPage />} />
                  <Route path="/risk-management-procedure" element={<RiskManagementPlanPage />} />
                  <Route path="/rmf" element={<RmfExportPage />} />
                  <Route path="/hazard-analysis" element={<HazardAnalysisPage />} />
                  <Route path="/residual-risk" element={<ResidualRiskReportPage />} />
                  <Route path="/risk-evaluation" element={<ResidualRiskReportPage />} />
                  <Route path="/risk-controls-documentation" element={<RiskControlsDocumentationPage />} />
                  <Route path="/reports/risk-control-measures" element={<RiskControlMeasuresReportPage />} />
                  <Route path="/reports/design-inputs" element={<DesignInputsReportPage />} />
                  <Route path="/reports/vv-evidence" element={<VVEvidenceReportPage />} />
                  <Route path="/pms/signals" element={<PmsSignalsPage />} />
                  <Route path="/pms/reports/signal-feedback" element={<PmsSignalReportPage />} />
                  <Route path="/traceability-matrix" element={<RiskTraceabilityMatrixPage />} />
                  <Route path="/residual-risk" element={<ResidualRiskRiskBenefitPage />} />
                  <Route path="/risk-control-implementation" element={<RiskControlImplementationPage />} />
                  <Route path="/risk-evaluation-report" element={<RiskEvaluationReportPage />} />
                  <Route path="/cache-clear" element={<CacheClearPage />} />
                  <Route path="/post-market" element={<PostMarket />} />
                  <Route path="/welcome" element={<WelcomePage />} />
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
