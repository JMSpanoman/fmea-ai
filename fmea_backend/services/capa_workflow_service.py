"""
Workflow gating and compliance validation for CAPA.
Enforces: no effectiveness confirmation without evidence; closure rules; RCA evidence for approval.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

from schemas.capa_workflow import (
    ActionStatus,
    ApprovalKind,
    ApprovalRecord,
    ApprovalStatus,
    CAPAWorkflowPayload,
    CAPAWorkflowState,
    EffectivenessResults,
    RootCauseStatus,
)


class CapaWorkflowError(Exception):
    """Business rule violation for CAPA transitions or payload."""

    def __init__(self, message: str, code: str = "capa_workflow"):
        super().__init__(message)
        self.code = code
        self.message = message


def _truthy_str(s: str) -> bool:
    return bool(s and str(s).strip())


def _status_is_complete(status: Any) -> bool:
    v = status.value if hasattr(status, "value") else status
    return str(v) == ActionStatus.COMPLETE.value


def intake_sections_complete(payload: CAPAWorkflowPayload) -> bool:
    """A + B + C minimum fields for progression to RCA."""
    t = payload.trigger
    p = payload.problem
    c = payload.containment
    return (
        t.trigger_type is not None
        and _truthy_str(t.source_reference)
        and _truthy_str(p.problem_statement)
        and p.scope is not None
        and _truthy_str(c.containment_actions)
        and c.containment_verified is True
    )


def rca_has_objective_evidence(payload: CAPAWorkflowPayload) -> bool:
    d = payload.rca
    if _truthy_str(d.objective_evidence):
        return True
    if d.evidence_attachment_references and len([x for x in d.evidence_attachment_references if str(x).strip()]):
        return True
    return False


def all_corrective_actions_linked(payload: CAPAWorkflowPayload) -> bool:
    for a in payload.corrective_actions:
        if not str(a.linked_root_cause_id or "").strip():
            return False
    return True


def all_corrective_actions_complete(payload: CAPAWorkflowPayload) -> bool:
    for a in payload.corrective_actions:
        if not _status_is_complete(a.status):
            return False
    return True


def approvals_satisfied_for_closure(payload: CAPAWorkflowPayload) -> bool:
    """Require approved status for RCA, action plan, and closure approval records."""
    needed = {
        ApprovalKind.RCA.value,
        ApprovalKind.ACTION_PLAN.value,
        ApprovalKind.CLOSURE.value,
    }
    found: dict[str, Any] = {}
    for a in payload.approvals:
        k = a.kind.value if hasattr(a.kind, "value") else str(a.kind)
        found[k] = a
    for k in needed:
        rec = found.get(k)
        if not rec:
            return False
        st = rec.status.value if hasattr(rec.status, "value") else rec.status
        if st != "approved":
            return False
    return True


def closure_checklist_ready(payload: CAPAWorkflowPayload) -> bool:
    ch = payload.closure.checklist
    return (
        ch.root_cause_verified
        and ch.actions_implemented
        and ch.effectiveness_supported_by_evidence
        and ch.risk_documentation_updated
        and ch.required_approvals_complete
        and ch.documentation_complete
    )


def validate_effectiveness_results(
    payload: CAPAWorkflowPayload,
    evidence_row_count: int,
    referenced_ids: Optional[List[str]] = None,
) -> None:
    """
    Effectiveness 'results' must not be stored without objective evidence.
    """
    if payload.effectiveness_results is None:
        return
    er = payload.effectiveness_results
    refs = referenced_ids or er.referenced_evidence_ids or []
    has_refs = bool(refs) and all(str(x).strip() for x in refs)
    has_table = evidence_row_count > 0
    if not (has_table or has_refs):
        raise CapaWorkflowError(
            "Effectiveness results require objective evidence: add at least one evidence record "
            "or reference evidence IDs before recording effectiveness.",
            "effectiveness_requires_evidence",
        )
    if not _truthy_str(er.evidence_summary) and not _truthy_str(er.result):
        raise CapaWorkflowError(
            "Effectiveness results require an evidence summary or documented result.",
            "effectiveness_incomplete",
        )


def validate_referenced_evidence_ids_exist(
    referenced_ids: List[str],
    existing_ids: set[str],
) -> None:
    for rid in referenced_ids:
        if str(rid).strip() and str(rid) not in existing_ids:
            raise CapaWorkflowError(
                f"Referenced evidence id not found on this CAPA: {rid}",
                "evidence_id_invalid",
            )


def validate_payload_for_state(
    workflow_state: str,
    payload: CAPAWorkflowPayload,
    evidence_row_count: int,
    evidence_ids: Optional[set[str]] = None,
) -> None:
    """Raise CapaWorkflowError if payload violates rules for target state."""
    try:
        st = CAPAWorkflowState(workflow_state)
    except ValueError:
        raise CapaWorkflowError(f"Unknown workflow state: {workflow_state}", "bad_state")

    if payload.effectiveness_results and payload.effectiveness_results.referenced_evidence_ids and evidence_ids is not None:
        validate_referenced_evidence_ids_exist(
            payload.effectiveness_results.referenced_evidence_ids,
            evidence_ids,
        )

    if st in (CAPAWorkflowState.RCA_IN_PROGRESS, CAPAWorkflowState.RCA_PENDING_APPROVAL):
        if not intake_sections_complete(payload):
            raise CapaWorkflowError(
                "Trigger, problem definition, and containment must be complete before RCA.",
                "gate_intake",
            )

    if st == CAPAWorkflowState.RCA_PENDING_APPROVAL:
        if not rca_has_objective_evidence(payload):
            raise CapaWorkflowError(
                "Root cause approval requires objective evidence or attachment references.",
                "rca_evidence_required",
            )
        if payload.rca.root_cause_status == RootCauseStatus.CONFIRMED and not rca_has_objective_evidence(payload):
            raise CapaWorkflowError(
                "Confirmed root cause status requires objective evidence.",
                "rca_confirmed_requires_evidence",
            )

    if st in (
        CAPAWorkflowState.ACTIONS_DEFINED,
        CAPAWorkflowState.IMPLEMENTATION,
        CAPAWorkflowState.EFFECTIVENESS_PLANNED,
        CAPAWorkflowState.EFFECTIVENESS_PENDING,
        CAPAWorkflowState.PENDING_CLOSURE,
        CAPAWorkflowState.CLOSED,
    ):
        if payload.corrective_actions and not all_corrective_actions_linked(payload):
            raise CapaWorkflowError(
                "Each corrective action must link to a root cause identifier.",
                "action_requires_root_cause_link",
            )

    if st in (CAPAWorkflowState.EFFECTIVENESS_PENDING, CAPAWorkflowState.PENDING_CLOSURE, CAPAWorkflowState.CLOSED):
        if payload.effectiveness_results is not None:
            validate_effectiveness_results(
                payload,
                evidence_row_count,
                payload.effectiveness_results.referenced_evidence_ids if payload.effectiveness_results else None,
            )

    if st == CAPAWorkflowState.CLOSED:
        if payload.corrective_actions and not all_corrective_actions_complete(payload):
            raise CapaWorkflowError(
                "Cannot close: all corrective actions must be marked complete.",
                "actions_incomplete",
            )
        if not approvals_satisfied_for_closure(payload):
            raise CapaWorkflowError(
                "Cannot close: RCA, action plan, and closure approvals must be approved.",
                "approvals_incomplete",
            )
        if not closure_checklist_ready(payload):
            raise CapaWorkflowError(
                "Cannot close: complete the closure checklist with required items checked.",
                "closure_checklist",
            )
        if payload.effectiveness_results is None:
            raise CapaWorkflowError(
                "Cannot close: effectiveness results must be recorded with objective evidence.",
                "closure_effectiveness",
            )
        er = payload.effectiveness_results
        assert er is not None
        validate_effectiveness_results(payload, evidence_row_count, er.referenced_evidence_ids)
        if er.conclusion is None:
            raise CapaWorkflowError(
                "Cannot close: effectiveness conclusion (effective / ineffective / monitoring) is required.",
                "closure_conclusion",
            )


def coerce_payload(raw: Optional[Any]) -> CAPAWorkflowPayload:
    if raw is None:
        return CAPAWorkflowPayload()
    if isinstance(raw, CAPAWorkflowPayload):
        return raw
    return CAPAWorkflowPayload.model_validate(raw)


def legacy_to_payload(
    root_cause: str,
    capa_plan: str,
    effectiveness_check: Optional[str],
    linked_risk_ids: Optional[List[str]],
) -> CAPAWorkflowPayload:
    """Map legacy CAPA columns into workflow payload for read compatibility."""
    p = CAPAWorkflowPayload()
    p.rca.root_cause_summary = root_cause or ""
    p.rca.root_cause_status = RootCauseStatus.HYPOTHESIS
    p.voe_plan.success_criteria = capa_plan or ""
    if effectiveness_check:
        p.effectiveness_results = EffectivenessResults(
            evidence_summary=effectiveness_check,
            result="",
            conclusion=None,
            referenced_evidence_ids=[],
        )
    if linked_risk_ids:
        p.risk_linkage.related_fmea_row_ids = list(linked_risk_ids)
    return p


def payload_to_legacy_fields(payload: CAPAWorkflowPayload) -> Tuple[str, str, Optional[str], List[str]]:
    """Sync minimal legacy columns from payload."""
    root = payload.rca.root_cause_summary or ""
    plan_parts = [a.description for a in payload.corrective_actions if a.description]
    capa_plan = "\n".join(plan_parts) if plan_parts else (payload.voe_plan.success_criteria or "")
    eff: Optional[str] = None
    if payload.effectiveness_results:
        eff = payload.effectiveness_results.evidence_summary or None
    risks = list(payload.risk_linkage.related_fmea_row_ids or [])
    return root, capa_plan, eff, risks


def default_approval_scaffold() -> List[Any]:
    """Three pending approvals for QA-style workflow (names TBD for e-sign)."""
    import uuid as _uuid

    return [
        ApprovalRecord(
            id=str(_uuid.uuid4()),
            kind=ApprovalKind.RCA,
            status=ApprovalStatus.PENDING,
        ),
        ApprovalRecord(
            id=str(_uuid.uuid4()),
            kind=ApprovalKind.ACTION_PLAN,
            status=ApprovalStatus.PENDING,
        ),
        ApprovalRecord(
            id=str(_uuid.uuid4()),
            kind=ApprovalKind.CLOSURE,
            status=ApprovalStatus.PENDING,
        ),
    ]
