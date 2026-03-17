# Import all CRUD modules
from . import project
from . import fmea
from . import component
from . import user
# Phase 2 modules
from . import design_control
from . import vv
from . import capa as capa_crud
from . import pms
from . import traceability
# Phase 3 modules
from . import document
from . import training
from . import change_control_phase3
from . import audit_phase3
from . import supplier_phase3
from . import ncr_phase3
from . import complaint_phase3
from . import equipment_phase3
from . import quality_event_phase3
from . import approval_phase3
from . import risk_knowledge_base

__all__ = [
    "project", "fmea", "component", "user",  # Phase 1
    "design_control", "vv", "capa_crud", "pms", "traceability",  # Phase 2
    "document", "training", "change_control_phase3", "audit_phase3", "supplier_phase3",  # Phase 3
    "ncr_phase3", "complaint_phase3", "equipment_phase3", "quality_event_phase3", "approval_phase3",  # Phase 3 continued
    "risk_knowledge_base",  # Risk Knowledge Base (Hazard, Harm, Risk Control, Verification libraries)
]
