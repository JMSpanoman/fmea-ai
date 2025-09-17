import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import { ProjectProvider } from './contexts/ProjectContext';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import NonConformancePage from './pages/NonConformancePage';
import CapaPage from './pages/CapaPage';
import ChangeControlPage from './pages/ChangeControlPage';
import FmeaPage from './pages/FMEAPage';
import HazardAnalysisPage from './pages/HazardAnalysisPage';
import FaultTreeReportPage from './pages/FaultTreeReportPage';
import RiskManagementReportPage from './pages/RiskManagementReportPage';

import RiskManagementPlanPage from './pages/RiskManagementPlanPage';
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

function App() {
  return (
    <AuthProvider>
      <ProjectProvider>
        <Router>
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50 flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <TrialStatusBanner />
                <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/nonconformance" element={<NonConformancePage />} />
                <Route path="/capa" element={<CapaPage />} />
                <Route path="/change-control" element={<ChangeControlPage />} />
                <Route path="/dfmea" element={<FmeaPage />} />
                <Route path="/hazard-analysis" element={<HazardAnalysisPage />} />
                <Route path="/fault-tree-report" element={<FaultTreeReportPage />} />
                <Route path="/risk-management-report" element={<RiskManagementReportPage />} />

                <Route path="/risk-management-plan" element={<RiskManagementPlanPage />} />
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
              </div>
            </div>
          </ProtectedRoute>
        </Router>
      </ProjectProvider>
    </AuthProvider>
  );
}

export default App;
