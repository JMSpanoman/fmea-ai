# Import all models to ensure they are registered with SQLAlchemy
from .project import Project
from .fmea import FMEARow
from .user import User
from .component import Component
from .fmea_version import FMEAVersion
# Phase 2 models
from .design_input import DesignInput
from .design_output import DesignOutput
from .vv_test import VVTest
from .capa import CAPA
from .pms_signal import PMSSignal
from .trace_link import TraceLink
# Phase 3 models
from .document import Document, DocumentVersion
from .training_record import TrainingRecord
from .change_control import ChangeControl
from .audit import Audit
from .supplier import Supplier, SupplierEvaluation
from .ncr import NCR
from .complaint import Complaint
from .equipment import Equipment, CalibrationRecord
from .quality_event import QualityEvent
from .approval import Approval
from .risk_item import RiskItem
from .risk_item_version import RiskItemVersion
from .risk_control import RiskControl
from .risk_management_plan import RiskManagementPlan
from .ai_event import AIEvent
from .audit_log_event import AuditLogEvent
from .idempotency_request import IdempotencyRequest
from .generated_artifact import GeneratedArtifact
from .project_profile import ProjectProfile
from .generated_vv import GeneratedVVRecord
# Risk Knowledge Base libraries (reusable for FMEA, hazard analysis, risk controls)
from .hazard_library import HazardLibrary
from .harm_library import HarmLibrary
from .risk_control_library import RiskControlLibrary
from .verification_library import VerificationLibrary
from .device_architecture import DeviceArchitecture, DeviceArchitectureNode, DeviceInterface
from .device import Device
from .generated_document import GeneratedDocument
from .project_risk_item import ProjectRiskItem
from .project_risk_control import ProjectRiskControl
from .project_verification import ProjectVerification
from .hazard_generation_rule import HazardGenerationRule
from .hazard_analysis_item import HazardAnalysisItem
from .risk_acceptability_criteria import (
    RiskAcceptabilityCriteria,
    OrganizationRiskCriteriaConfig,
    ProjectRiskCriteriaOverride,
)
from . import suggested_risk_analysis
from .suggested_risk_analysis import (
    RiskAnalysisSuggestionSet,
    SuggestedFailureMode,
    SuggestedHazard as SuggestedHazardRow,
    SuggestedHazardousSituation,
    SuggestedHarm,
    SuggestedControl,
    SuggestedVerificationMethod,
)

__all__ = [
    "Project", "FMEARow", "User", "Component", "FMEAVersion",  # Phase 1
    "DesignInput", "DesignOutput", "VVTest", "CAPA", "PMSSignal", "TraceLink",  # Phase 2
    "Document", "DocumentVersion", "TrainingRecord", "ChangeControl", "Audit",  # Phase 3
    "Supplier", "SupplierEvaluation", "NCR", "Complaint", "Equipment", "CalibrationRecord",
    "QualityEvent", "Approval", "RiskItem", "RiskItemVersion", "RiskControl", "RiskManagementPlan", "AIEvent",  # Phase 3 continued + Risk Items
    "AuditLogEvent", "IdempotencyRequest", "GeneratedArtifact", "ProjectProfile", "GeneratedVVRecord",  # + generated V&V from risk
    "HazardLibrary", "HarmLibrary", "RiskControlLibrary", "VerificationLibrary",  # Risk Knowledge Base
    "DeviceArchitecture", "DeviceArchitectureNode", "DeviceInterface",  # SmartRisk device architecture
    "Device", "GeneratedDocument", "ProjectRiskItem", "ProjectRiskControl", "ProjectVerification",  # Project risk items, controls, verifications
    "HazardGenerationRule",  # SmartRisk hazard generation rules (Phase 2)
    "HazardAnalysisItem",  # ISO 14971 full hazard analysis items
    "RiskAcceptabilityCriteria",
    "OrganizationRiskCriteriaConfig",
    "ProjectRiskCriteriaOverride",
    "RiskAnalysisSuggestionSet",
    "SuggestedFailureMode",
    "SuggestedHazardRow",
    "SuggestedHazardousSituation",
    "SuggestedHarm",
    "SuggestedControl",
    "SuggestedVerificationMethod",
]
