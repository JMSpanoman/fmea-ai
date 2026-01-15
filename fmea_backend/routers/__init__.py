# routers package
from . import auth
from . import ai
from . import tracibility
from . import mitigations
from . import nonconformance
from . import capa
from . import change_control
from . import templates
# Phase 1 routers
from . import projects
from . import components
from . import fmea
from . import ai_phase1
from . import export
# Phase 2 routers
from . import design_controls
from . import vv
from . import capa_phase2
from . import pms
from . import traceability
from . import ai_phase2
# Phase 3 routers
from . import document_control
from . import document_guidance
from . import training_phase3
from . import change_control_phase3
from . import audit_phase3
from . import supplier_phase3
from . import ncr_phase3
from . import complaint_phase3
from . import equipment_phase3
from . import quality_event_phase3
from . import approval_phase3
from . import ai_phase3
from . import risk_items

__all__ = [
    "auth", "ai", "tracibility", "mitigations", "nonconformance", "capa", "change_control", "templates",
    "projects", "components", "fmea", "ai_phase1", "export",  # Phase 1
    "design_controls", "vv", "capa_phase2", "pms", "traceability", "ai_phase2",  # Phase 2
    "document_control", "training_phase3", "change_control_phase3", "audit_phase3", "supplier_phase3",  # Phase 3
    "ncr_phase3", "complaint_phase3", "equipment_phase3", "quality_event_phase3", "approval_phase3", "ai_phase3",  # Phase 3 continued
    "document_guidance",
    "risk_items"  # Risk Items
]
