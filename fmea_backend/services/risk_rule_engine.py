"""
Deterministic risk acceptability rule engine for FMEA rows.

Regulatory intent:
- Classifications and flags are computed from versioned project criteria (JSON), not from LLM output.
- AI may populate ai_suggested_values_json on the row; this module never reads it for decisions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

from schemas.risk_rule_engine import FmeaRiskEvaluationInput, RiskCriteriaConfig, RiskEvaluationResult

Classification = str  # Acceptable | ALARP | Unacceptable

RowInput = Union[Dict[str, Any], FmeaRiskEvaluationInput]
CriteriaInput = Union[Dict[str, Any], RiskCriteriaConfig]


def _unwrap_row(row: RowInput) -> Dict[str, Any]:
    if isinstance(row, FmeaRiskEvaluationInput):
        return row.to_engine_dict()
    return dict(row)


def _unwrap_criteria(criteria: CriteriaInput) -> Dict[str, Any]:
    if isinstance(criteria, RiskCriteriaConfig):
        return criteria.to_engine_dict()
    return dict(criteria)

CLASS_RANK: Dict[str, int] = {"Acceptable": 0, "ALARP": 1, "Unacceptable": 2}


def _row_bool(row: Dict[str, Any], key: str) -> bool:
    """Strict attestation: only True counts as satisfied."""
    return row.get(key) is True


def _get_mandatory_policies(special_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configurable mandatory release policies under ``special_rules.mandatory_policies``.
    When the key is absent, defaults apply (regulatory defaults for this product).
    Set ``enabled: false`` to disable for legacy criteria JSON.
    """
    raw = special_rules.get("mandatory_policies")
    if not isinstance(raw, dict):
        raw = {}
    if raw.get("enabled") is False:
        return {"enabled": False}
    disciplines = raw.get("release_review_disciplines")
    if not isinstance(disciplines, list):
        disciplines = ["Engineering", "Clinical", "Quality"]
    return {
        "enabled": True,
        "death_minimum_fmea_severity": int(raw.get("death_minimum_fmea_severity", 5)),
        "residual_review_minimum_fmea_severity": int(raw.get("residual_review_minimum_fmea_severity", 4)),
        "disciplines": [str(x) for x in disciplines],
    }


def _apply_mandatory_policies(
    *,
    row: Dict[str, Any],
    evaluation_type: str,
    special: Dict[str, Any],
    benefit: bool,
    reviewer: bool,
    matched_rules: List[str],
    decision_path: List[str],
) -> Tuple[bool, bool, bool, bool, bool]:
    """
    Apply ``mandatory_policies``; returns
    (benefit_risk_formal_approval_required, cross_functional_review_required,
     formal_release_approval_required, benefit, reviewer).
    """
    mp = _get_mandatory_policies(special)
    if not mp.get("enabled"):
        return False, False, False, benefit, reviewer

    formal_bra = False
    cross_fn = False
    formal_rel = False

    init_sev = row.get("severity")
    death_min = mp["death_minimum_fmea_severity"]
    if init_sev is not None:
        try:
            if int(init_sev) >= death_min:
                benefit = True
                formal_bra = True
                matched_rules.append("mandatory:death_severity_benefit_risk_formal_approval")
                decision_path.append(
                    f"Mandatory policy: initial severity {init_sev} >= death threshold ({death_min}) "
                    "requires documented benefit-risk analysis and formal approval (regardless of probability)"
                )
        except (TypeError, ValueError):
            pass

    if evaluation_type == "residual":
        rs = row.get("residual_severity")
        rmin = mp["residual_review_minimum_fmea_severity"]
        if rs is not None:
            try:
                if int(rs) >= rmin:
                    reviewer = True
                    cross_fn = True
                    formal_rel = True
                    matched_rules.append("mandatory:residual_severity_review_and_release_approval")
                    discs = ", ".join(mp.get("disciplines", []))
                    decision_path.append(
                        f"Mandatory policy: residual severity {rs} >= {rmin} requires documented justification, "
                        f"cross-functional review ({discs}), and formal approval prior to release"
                    )
            except (TypeError, ValueError):
                pass

    return formal_bra, cross_fn, formal_rel, benefit, reviewer


def _failure_payload(
    *,
    evaluation_type: str,
    validation_errors: Optional[List[str]] = None,
    decision_path: Optional[List[str]] = None,
) -> Dict[str, Any]:
    errs = list(validation_errors or [])
    path = list(decision_path or errs or ["Evaluation aborted"])
    blockers = [f"Validation: {e}" for e in errs] if errs else ["Evaluation did not complete"]
    return {
        "ok": False,
        "evaluation_type": evaluation_type,
        "validation_errors": errs or None,
        "classification": None,
        "risk_score": None,
        "benefit_risk_required": False,
        "reviewer_justification_required": False,
        "approval_blocked": True,
        "critical_function_flag": False,
        "critical_hazard_category_match": False,
        "system_level_verification_required": False,
        "input_fmea_severity": None,
        "evaluated_fmea_severity": None,
        "benefit_risk_formal_approval_required": False,
        "cross_functional_review_required": False,
        "formal_release_approval_required": False,
        "residual_acceptable_rationale_required": False,
        "residual_alarp_feasibility_attestations_required": False,
        "benefit_risk_structured_workflow_active": False,
        "benefit_risk_documentation_gates_active": False,
        "benefit_risk_multi_party_approval_required": False,
        "acceptable_for_release": False,
        "release_status": "not_acceptable_for_release",
        "release_blockers": blockers,
        "matched_rules": [],
        "decision_path": path,
    }


# Stable row column names for benefit–risk workflow attestations (criteria JSON references logical ids only).
BRA_DOCUMENTATION_ROW_KEYS: Dict[str, str] = {
    "clinical_benefit": "bra_clinical_benefit_documented",
    "benefit_vs_residual_risk": "bra_benefit_vs_residual_risk_documented",
    "state_of_art": "bra_state_of_the_art_documented",
    "supporting_evidence": "bra_supporting_evidence_addressed",
}
BRA_APPROVAL_ROW_KEYS: Dict[str, str] = {
    "clinical_medical": "bra_approval_clinical_medical_recorded",
    "quality_regulatory": "bra_approval_quality_regulatory_recorded",
    "design_authority": "bra_approval_design_authority_recorded",
}


def _default_benefit_risk_workflow_policy() -> Dict[str, Any]:
    """Default ISO 14971–style benefit–risk documentation + multi-party acceptance (configurable via criteria)."""
    return {
        "enabled": True,
        "apply_when": "formal_bra_required",
        "use_multi_party_approval": True,
        "documentation_requirements": [
            {
                "id": "clinical_benefit",
                "label": "Description of clinical benefit",
            },
            {
                "id": "benefit_vs_residual_risk",
                "label": "Comparison of benefit vs residual risk",
            },
            {
                "id": "state_of_art",
                "label": "Consideration of state of the art",
            },
            {
                "id": "supporting_evidence",
                "label": "Supporting clinical or literature evidence (where available)",
            },
        ],
        "approval_roles": [
            {"id": "clinical_medical", "label": "Clinical/Medical"},
            {"id": "quality_regulatory", "label": "Quality/Regulatory"},
            {"id": "design_authority", "label": "Design authority (as defined by project governance)"},
        ],
    }


def _get_benefit_risk_workflow_policy(special_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Structured benefit–risk analysis documentation + acceptance approvals.

    ``special_rules.benefit_risk_workflow_policy`` — set ``enabled: false`` for legacy single-flag
    ``benefit_risk_formal_approval_recorded`` only.
    """
    raw = special_rules.get("benefit_risk_workflow_policy")
    if raw is None:
        base = _default_benefit_risk_workflow_policy()
    elif not isinstance(raw, dict):
        return {"enabled": False}
    elif raw.get("enabled") is False:
        return {"enabled": False}
    else:
        base = {**_default_benefit_risk_workflow_policy(), **raw}
        base["enabled"] = True

    docs_in = base.get("documentation_requirements")
    if not isinstance(docs_in, list):
        docs_in = _default_benefit_risk_workflow_policy()["documentation_requirements"]
    doc_items: List[Dict[str, str]] = []
    for item in docs_in:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("id") or "").strip()
        rk = BRA_DOCUMENTATION_ROW_KEYS.get(rid)
        if not rk:
            continue
        label = str(item.get("label") or rid).strip()
        doc_items.append({"id": rid, "label": label, "row_key": rk})

    appr_in = base.get("approval_roles")
    if not isinstance(appr_in, list):
        appr_in = _default_benefit_risk_workflow_policy()["approval_roles"]
    appr_items: List[Dict[str, str]] = []
    for item in appr_in:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("id") or "").strip()
        rk = BRA_APPROVAL_ROW_KEYS.get(rid)
        if not rk:
            continue
        label = str(item.get("label") or rid).strip()
        appr_items.append({"id": rid, "label": label, "row_key": rk})

    return {
        "enabled": True,
        "apply_when": str(base.get("apply_when") or "formal_bra_required"),
        "use_multi_party_approval": bool(base.get("use_multi_party_approval", True)),
        "documentation_requirements": doc_items,
        "approval_roles": appr_items,
    }


def _benefit_risk_workflow_triggers(*, formal_bra_req: bool, benefit: bool, apply_when: str) -> bool:
    aw = (apply_when or "formal_bra_required").strip().lower()
    if aw in ("benefit_risk_required", "when_benefit_risk_required"):
        return bool(benefit)
    return bool(formal_bra_req)


def _apply_benefit_risk_workflow_gates(
    *,
    row: Dict[str, Any],
    special: Dict[str, Any],
    formal_bra_req: bool,
    benefit: bool,
    matched_rules: List[str],
    decision_path: List[str],
    release_blockers: List[str],
) -> Tuple[bool, bool, bool]:
    """
    Returns (structured_active, documentation_active, multi_party_required).
    Mutates matched_rules, decision_path, release_blockers.
    """
    pol = _get_benefit_risk_workflow_policy(special)
    if not pol.get("enabled"):
        return False, False, False

    if not _benefit_risk_workflow_triggers(
        formal_bra_req=formal_bra_req,
        benefit=benefit,
        apply_when=str(pol.get("apply_when") or "formal_bra_required"),
    ):
        return False, False, False

    matched_rules.append("policy:benefit_risk_structured_documentation_and_multi_party_approval")
    decision_path.append(
        "Policy: structured benefit–risk analysis — documentation elements and multi-party acceptance "
        "per project criteria (Clinical/Medical, Quality/Regulatory, Design authority)."
    )
    for d in pol.get("documentation_requirements") or []:
        decision_path.append(f"Benefit–risk documentation required: {d['label']}")
    for a in pol.get("approval_roles") or []:
        decision_path.append(f"Benefit–risk acceptance required: {a['label']}")

    doc_active = len(pol.get("documentation_requirements") or []) > 0
    for d in pol.get("documentation_requirements") or []:
        if not _row_bool(row, d["row_key"]):
            release_blockers.append(
                f"Benefit–risk analysis: “{d['label']}” not attested as addressed in the documented analysis"
            )

    multi = bool(pol.get("use_multi_party_approval", True))
    if multi:
        for a in pol.get("approval_roles") or []:
            if not _row_bool(row, a["row_key"]):
                release_blockers.append(
                    f"Benefit–risk acceptance: {a['label']} approval not recorded"
                )
    elif formal_bra_req and not _row_bool(row, "benefit_risk_formal_approval_recorded"):
        release_blockers.append(
            "Benefit-risk formal approval not recorded (mandatory for configured death-severity pathway)"
        )
        decision_path.append("Policy: legacy single benefit–risk formal approval attestation required")

    return True, doc_active, multi


def _get_residual_acceptability_policies(special_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    ISO 14971–aligned **residual** acceptability workflow (configurable).

    Stored under ``special_rules.residual_acceptability_policies``.
    If the key is omitted, defaults apply (residual-only gates enabled).
    Set ``enabled: false`` to disable for legacy criteria.
    """
    raw = special_rules.get("residual_acceptability_policies")
    if raw is None:
        return {
            "enabled": True,
            "acceptable_requires_documented_rationale": True,
            "alarp_requires_documented_justification": True,
            "alarp_requires_feasibility_attestations": True,
            "alarp_requires_formal_release_approval": True,
        }
    if not isinstance(raw, dict):
        return {"enabled": False}
    if raw.get("enabled") is False:
        return {"enabled": False}
    return {
        "enabled": True,
        "acceptable_requires_documented_rationale": raw.get("acceptable_requires_documented_rationale", True),
        "alarp_requires_documented_justification": raw.get("alarp_requires_documented_justification", True),
        "alarp_requires_feasibility_attestations": raw.get("alarp_requires_feasibility_attestations", True),
        "alarp_requires_formal_release_approval": raw.get("alarp_requires_formal_release_approval", True),
    }


def _apply_residual_acceptability_policies(
    *,
    evaluation_type: str,
    cls_norm: str,
    special: Dict[str, Any],
    matched_rules: List[str],
    decision_path: List[str],
    reviewer: bool,
    formal_rel_req: bool,
) -> Tuple[bool, bool, bool, bool]:
    """
    Apply residual-only acceptability rules. Returns:
    (reviewer, formal_rel_req, residual_acceptable_rationale_required,
     residual_alarp_feasibility_attestations_required).
    """
    if evaluation_type != "residual":
        return reviewer, formal_rel_req, False, False

    rap = _get_residual_acceptability_policies(special)
    if not rap.get("enabled"):
        return reviewer, formal_rel_req, False, False

    matched_rules.append("policy:residual_evaluation_post_risk_controls_context")
    decision_path.append(
        "Residual risk acceptability (ISO 14971): residual classification is evaluated after implementation "
        "of applicable risk control measures for this row."
    )

    res_acc = False
    res_feas = False

    if cls_norm == "Acceptable":
        if rap.get("acceptable_requires_documented_rationale"):
            res_acc = True
            reviewer = True
            matched_rules.append("policy:residual_acceptable_documented_rationale_required")
            decision_path.append(
                "Policy: residual Acceptable — documented rationale is required to accept the residual risk"
            )
    elif cls_norm == "ALARP":
        if rap.get("alarp_requires_documented_justification"):
            reviewer = True
            matched_rules.append("policy:residual_alarp_documented_justification_required")
            decision_path.append(
                "Policy: residual ALARP — documented justification required (feasible controls implemented; "
                "further reduction not practicable)"
            )
        if rap.get("alarp_requires_feasibility_attestations"):
            res_feas = True
            matched_rules.append("policy:residual_alarp_feasibility_attestations_required")
            decision_path.append(
                "Policy: residual ALARP — row must attest all feasible controls implemented and "
                "further reduction is not practicable"
            )
        if rap.get("alarp_requires_formal_release_approval"):
            formal_rel_req = True
            matched_rules.append("policy:residual_alarp_formal_release_approval_required")
            decision_path.append("Policy: residual ALARP — formal approval required prior to release")
    elif cls_norm == "Unacceptable":
        matched_rules.append("policy:residual_unacceptable_release_constraints")
        decision_path.append(
            "Policy: residual Unacceptable — not acceptable for release unless reduced via additional controls "
            "or documented approved benefit-risk analysis"
        )

    return reviewer, formal_rel_req, res_acc, res_feas


def _get_critical_hazard_policies(special_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Life-sustaining / implantable-device critical hazard policy block (data-driven).

    ``special_rules.critical_hazard_policies`` may set:
    - ``minimum_fmea_severity_floor`` — raise numeric FMEA severity before matrix mapping (optional)
    - ``minimum_severity_matrix_index_floor`` — after mapping, floor matrix row index (e.g. 4 = S4 band)
    - ``keyword_list_ref`` — name of a string list on ``special_rules`` (default ``critical_hazard_category_keywords``)
    """
    raw = special_rules.get("critical_hazard_policies")
    if not isinstance(raw, dict):
        return {"enabled": False}
    if raw.get("enabled") is False:
        return {"enabled": False}
    ref = raw.get("keyword_list_ref", "critical_hazard_category_keywords")
    kws = _resolve_keyword_list(ref, special_rules)
    inline = raw.get("keywords_inline")
    if isinstance(inline, list):
        kws = [str(x) for x in inline] + kws
    mfea = raw.get("minimum_fmea_severity_floor")
    mxi = raw.get("minimum_severity_matrix_index_floor")
    return {
        "enabled": True,
        "keywords": kws,
        "minimum_fmea_severity_floor": int(mfea) if mfea is not None else None,
        "minimum_severity_matrix_index_floor": int(mxi) if mxi is not None else None,
        "require_system_level_verification": raw.get("require_system_level_verification", True),
        "require_justification_when_not_eliminated": raw.get("require_justification_when_not_eliminated", True),
    }


def _apply_critical_hazard_phase(
    *,
    row: Dict[str, Any],
    special: Dict[str, Any],
    corpus_lower: str,
    sev_orig: int,
    matched_rules: List[str],
    decision_path: List[str],
) -> Tuple[int, bool, bool, bool, Optional[int]]:
    """
    Returns:
        (severity_for_matrix_and_score, category_match, system_level_verification_required,
         extra_reviewer_when_not_eliminated, minimum_severity_matrix_index_floor_or_none)
    """
    cfg = _get_critical_hazard_policies(special)
    if not cfg.get("enabled") or not cfg.get("keywords"):
        return sev_orig, False, False, False, None

    if not _keyword_hit(corpus_lower, cfg["keywords"]):
        return sev_orig, False, False, False, None

    matched_rules.append("policy:critical_hazard_category_life_sustaining")
    decision_path.append(
        "Policy: text matches configured critical hazard categories for a life-sustaining implantable device — "
        "heightened scrutiny (severity floor, system-level verification, justification if not eliminated)."
    )

    waived = _row_bool(row, "critical_hazard_severity_floor_waived")
    mx_floor: Optional[int] = None
    if waived:
        sev_fm = sev_orig
        decision_path.append(
            "Attestation: critical hazard severity floors waived — alternate severity must be documented "
            "in reviewer justification."
        )
    else:
        sev_fm = sev_orig
        mf = cfg.get("minimum_fmea_severity_floor")
        if mf is not None:
            before = sev_fm
            sev_fm = max(sev_fm, int(mf))
            if sev_fm != before:
                decision_path.append(
                    f"Policy: critical hazard — FMEA severity raised from {before} to {sev_fm} "
                    f"(minimum {mf} unless waived and documented otherwise)"
                )
        mxi = cfg.get("minimum_severity_matrix_index_floor")
        if mxi is not None:
            mx_floor = int(mxi)

    sys_ver = bool(cfg.get("require_system_level_verification"))
    if sys_ver:
        matched_rules.append("policy:critical_hazard_system_level_verification_required")

    ch_rev = bool(cfg.get("require_justification_when_not_eliminated")) and not _row_bool(row, "risk_eliminated")
    if ch_rev:
        matched_rules.append("policy:critical_hazard_justification_if_not_eliminated")
        decision_path.append(
            "Policy: critical hazard and risk not attested eliminated — documented justification required"
        )

    if waived:
        mx_floor = None

    return sev_fm, True, sys_ver, ch_rev, mx_floor


def normalize_classification(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    key = s.lower()
    if key in ("acceptable", "accept"):
        return "Acceptable"
    if key in ("alarp", "as low as reasonably practicable"):
        return "ALARP"
    if key in ("unacceptable", "unaccept"):
        return "Unacceptable"
    # allow exact canonical
    if s in CLASS_RANK:
        return s
    return None


def max_classification(a: Optional[str], b: Optional[str]) -> str:
    """Return the more conservative (higher risk) classification."""
    aa = normalize_classification(a) or "Acceptable"
    bb = normalize_classification(b) or "Acceptable"
    return aa if CLASS_RANK[aa] >= CLASS_RANK[bb] else bb


def min_escalation_classification(current: str, floor: str) -> str:
    """For min_classification rules: never reduce below `floor`."""
    cur = normalize_classification(current) or "Acceptable"
    fl = normalize_classification(floor) or "ALARP"
    return cur if CLASS_RANK[cur] >= CLASS_RANK[fl] else fl


def _scale_levels(scale: Optional[List[Dict[str, Any]]]) -> int:
    if not scale or not isinstance(scale, list):
        return 4
    return max(int(x.get("level", 0)) for x in scale if isinstance(x, dict)) or 4


def _matrix_dim(matrix: Optional[Dict[str, Any]]) -> Tuple[int, int]:
    if not matrix or not isinstance(matrix, dict):
        return 4, 4
    rows = [int(k) for k in matrix.keys() if str(k).isdigit()]
    if not rows:
        return 4, 4
    max_r = max(rows)
    first = matrix.get(str(min(rows)), matrix.get(str(max_r), {}))
    if not isinstance(first, dict):
        return max_r, 4
    cols = [int(k) for k in first.keys() if str(k).isdigit()]
    max_c = max(cols) if cols else 4
    return max_r, max_c


def validate_criteria_config(criteria_dict: Dict[str, Any]) -> List[str]:
    """
    Return human-readable errors; empty list means criteria is structurally complete enough to evaluate.
    """
    errors: List[str] = []
    method = (criteria_dict.get("evaluation_method") or "matrix").lower()
    sev = criteria_dict.get("severity_scale")
    prob = criteria_dict.get("probability_scale")
    matrix = criteria_dict.get("risk_matrix")
    if not isinstance(sev, list) or len(sev) == 0:
        errors.append("severity_scale must be a non-empty list")
    if not isinstance(prob, list) or len(prob) == 0:
        errors.append("probability_scale must be a non-empty list")
    n_s = _scale_levels(sev if isinstance(sev, list) else None)
    n_p = _scale_levels(prob if isinstance(prob, list) else None)

    if method in ("matrix", "hybrid"):
        if not isinstance(matrix, dict):
            errors.append("risk_matrix must be an object mapping severity index -> probability index -> classification")
        else:
            for si in range(1, n_s + 1):
                row = matrix.get(str(si))
                if not isinstance(row, dict):
                    errors.append(f"risk_matrix missing row for severity index {si}")
                    continue
                for pi in range(1, n_p + 1):
                    cell = row.get(str(pi))
                    if cell is None or str(cell).strip() == "":
                        errors.append(f"risk_matrix incomplete at S{si} x P{pi}")
                    elif normalize_classification(str(cell)) is None:
                        errors.append(f"risk_matrix invalid classification at S{si} x P{pi}: {cell!r}")

    if method in ("score", "hybrid"):
        th = criteria_dict.get("score_thresholds")
        if not isinstance(th, dict):
            errors.append("score_thresholds required for score/hybrid evaluation_method")
        else:
            if th.get("acceptable_max_rpn") is None or th.get("alarp_max_rpn") is None:
                errors.append("score_thresholds must define acceptable_max_rpn and alarp_max_rpn")

    return errors


def validate_fmea_row_inputs(
    *,
    evaluation_type: str,
    severity: Optional[int],
    occurrence: Optional[int],
    detection: Optional[int],
    residual_severity: Optional[int],
    residual_occurrence: Optional[int],
    residual_detection: Optional[int],
) -> List[str]:
    errors: List[str] = []
    et = evaluation_type.lower()
    if et == "initial":
        if severity is None:
            errors.append("severity is required for initial risk evaluation")
        if occurrence is None:
            errors.append("occurrence/probability is required for initial risk evaluation")
    elif et == "residual":
        if residual_severity is None:
            errors.append("residual_severity is required for residual risk evaluation")
        if residual_occurrence is None:
            errors.append("residual_occurrence/residual_probability is required for residual risk evaluation")
        if detection is not None and residual_detection is None:
            # If initial used detection in RPN, residual path should also have detection for score method consistency
            pass  # optional warning only
    else:
        errors.append("evaluation_type must be initial or residual")
    return errors


def _default_map_fmea_to_matrix(
    value: int,
    thresholds: Optional[Dict[str, Any]],
    key: str,
    max_level: int,
) -> int:
    if thresholds and isinstance(thresholds.get(key), dict):
        m = thresholds[key]
        v = m.get(str(int(value)))
        if v is not None:
            try:
                return int(v)
            except (TypeError, ValueError):
                pass
    # fallback: bucket 1–10 into 1–4
    v = int(value)
    if v <= 3:
        idx = 1
    elif v <= 6:
        idx = 2
    elif v <= 8:
        idx = 3
    else:
        idx = 4
    return min(max_level, max(1, idx))


def map_to_matrix_indices(
    *,
    severity: Optional[int],
    occurrence: Optional[int],
    criteria_dict: Dict[str, Any],
) -> Tuple[int, int, List[str]]:
    path: List[str] = []
    th = criteria_dict.get("score_thresholds") if isinstance(criteria_dict.get("score_thresholds"), dict) else {}
    n_s = _scale_levels(criteria_dict.get("severity_scale"))
    n_p = _scale_levels(criteria_dict.get("probability_scale"))
    if severity is None or occurrence is None:
        raise ValueError("severity and occurrence required for mapping")
    si = _default_map_fmea_to_matrix(int(severity), th, "fmea_severity_to_matrix_index", n_s)
    pi = _default_map_fmea_to_matrix(int(occurrence), th, "fmea_occurrence_to_matrix_index", n_p)
    path.append(f"Mapped FMEA severity {severity} -> matrix index {si} (scale 1..{n_s})")
    path.append(f"Mapped FMEA occurrence {occurrence} -> matrix index {pi} (scale 1..{n_p})")
    return si, pi, path


def matrix_lookup(criteria_dict: Dict[str, Any], si: int, pi: int) -> Tuple[str, List[str]]:
    matrix = criteria_dict.get("risk_matrix") or {}
    row = matrix.get(str(si)) or matrix.get(si)  # type: ignore[arg-type]
    if not isinstance(row, dict):
        raise ValueError(f"risk_matrix missing row for severity index {si}")
    raw = row.get(str(pi)) if row.get(str(pi)) is not None else row.get(pi)
    if raw is None:
        raise ValueError(f"risk_matrix missing cell for S{si} x P{pi}")
    cls = normalize_classification(str(raw))
    if cls is None:
        raise ValueError(f"Invalid matrix cell at S{si} x P{pi}: {raw!r}")
    return cls, [f"Matrix lookup S{si} x P{pi} => {cls}"]


def score_classification(
    *,
    severity: Optional[int],
    occurrence: Optional[int],
    detection: Optional[int],
    thresholds: Dict[str, Any],
) -> Tuple[Optional[int], Optional[str], List[str]]:
    path: List[str] = []
    if severity is None or occurrence is None:
        return None, None, ["Score method skipped: missing severity or occurrence"]
    det = detection if detection is not None else 1
    rpn = int(severity) * int(occurrence) * int(det)
    path.append(f"Computed risk score (S×O×D) = {severity} × {occurrence} × {det} = {rpn}")
    am = thresholds.get("acceptable_max_rpn")
    bm = thresholds.get("alarp_max_rpn")
    try:
        am_i = int(am)
        bm_i = int(bm)
    except (TypeError, ValueError):
        raise ValueError("score_thresholds.acceptable_max_rpn and alarp_max_rpn must be integers")
    if rpn <= am_i:
        path.append(f"Score {rpn} <= acceptable_max_rpn ({am_i}) => Acceptable")
        return rpn, "Acceptable", path
    if rpn <= bm_i:
        path.append(f"Score {rpn} <= alarp_max_rpn ({bm_i}) => ALARP")
        return rpn, "ALARP", path
    path.append(f"Score {rpn} > alarp_max_rpn ({bm_i}) => Unacceptable")
    return rpn, "Unacceptable", path


def build_text_corpus(row: Dict[str, Any], component_name: str = "") -> str:
    parts = [
        component_name or "",
        row.get("device_function") or "",
        row.get("failure_mode") or "",
        row.get("effect") or "",
        row.get("harm") or "",
        row.get("hazard") or "",
        row.get("cause") or "",
        row.get("mitigation") or "",
        row.get("action_taken") or "",
    ]
    return " \n ".join(str(p) for p in parts if p)


def _keyword_hit(corpus_lower: str, keywords: List[str]) -> bool:
    for kw in keywords:
        k = str(kw).strip().lower()
        if k and k in corpus_lower:
            return True
    return False


def _resolve_keyword_list(ref: Union[str, List[str]], special_rules: Dict[str, Any]) -> List[str]:
    if isinstance(ref, list):
        return [str(x) for x in ref]
    key = str(ref)
    val = special_rules.get(key)
    if isinstance(val, list):
        return [str(x) for x in val]
    return []


def _device_context(special_rules: Dict[str, Any]) -> Dict[str, Any]:
    dc = special_rules.get("device_context")
    return dc if isinstance(dc, dict) else {}


def _match_condition(
    condition: Any,
    *,
    eval_type: str,
    ctx: Dict[str, Any],
    special_rules: Dict[str, Any],
) -> bool:
    if not isinstance(condition, dict):
        return False
    if "all" in condition:
        inner = condition.get("all")
        if not isinstance(inner, list):
            return False
        return all(_match_condition(c, eval_type=eval_type, ctx=ctx, special_rules=special_rules) for c in inner)
    if "any" in condition:
        inner = condition.get("any")
        if not isinstance(inner, list):
            return False
        return any(_match_condition(c, eval_type=eval_type, ctx=ctx, special_rules=special_rules) for c in inner)

    if "severity_matrix_gte" in condition:
        return int(ctx.get("severity_matrix_idx") or 0) >= int(condition["severity_matrix_gte"])
    if "probability_matrix_gte" in condition:
        return int(ctx.get("probability_matrix_idx") or 0) >= int(condition["probability_matrix_gte"])

    if "residual_severity_matrix_gte" in condition:
        if eval_type != "residual":
            return False
        rsi = ctx.get("residual_severity_matrix_idx")
        return rsi is not None and int(rsi) >= int(condition["residual_severity_matrix_gte"])

    if "residual_probability_matrix_gte" in condition:
        if eval_type != "residual":
            return False
        rpi = ctx.get("residual_probability_matrix_idx")
        return rpi is not None and int(rpi) >= int(condition["residual_probability_matrix_gte"])

    if "classification_eq" in condition:
        cur = normalize_classification(ctx.get("current_classification"))
        return cur == normalize_classification(str(condition["classification_eq"]))

    if "text_matches_any" in condition:
        ref = condition["text_matches_any"]
        kws = _resolve_keyword_list(ref, special_rules)
        return _keyword_hit(ctx.get("corpus_lower", ""), kws)

    if "device_context_equals" in condition:
        target = condition["device_context_equals"]
        if not isinstance(target, dict):
            return False
        dc = _device_context(special_rules)
        for k, v in target.items():
            if dc.get(k) != v:
                return False
        return True

    return False


def apply_declarative_rules(
    *,
    evaluation_type: str,
    base_classification: str,
    special_rules: Dict[str, Any],
    ctx: Dict[str, Any],
) -> Tuple[str, bool, bool, bool, List[str], List[str]]:
    """
    Returns: classification, benefit_risk_required, reviewer_just_required, critical_function_flag, matched_rules, decision_path
    """
    matched: List[str] = []
    path: List[str] = []
    cls = normalize_classification(base_classification) or "Acceptable"
    benefit = bool(ctx.get("force_benefit_risk"))
    reviewer = bool(ctx.get("force_reviewer"))
    crit_flag = bool(ctx.get("force_critical_flag"))

    rules = special_rules.get("rules")
    if not isinstance(rules, list):
        rules = []

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rid = str(rule.get("id") or "rule")
        rtype = str(rule.get("type") or "")
        cond = rule.get("condition")
        if cond is not None and not _match_condition(cond, eval_type=evaluation_type, ctx=ctx, special_rules=special_rules):
            continue

        matched.append(f"rule:{rid}:{rtype}")
        if rtype == "benefit_risk_required":
            benefit = True
            path.append(f"Rule {rid}: benefit-risk review required")
        elif rtype == "reviewer_justification_required":
            reviewer = True
            path.append(f"Rule {rid}: reviewer justification required")
        elif rtype == "min_classification":
            floor = str(rule.get("value") or "ALARP")
            before = cls
            cls = min_escalation_classification(cls, floor)
            if cls != before:
                path.append(f"Rule {rid}: escalate classification floor to {floor} => {cls}")
        elif rtype == "set_critical_function_flag":
            crit_flag = True
            path.append(f"Rule {rid}: critical function / therapy risk flagged")
        elif rtype == "approval_blocked":
            ctx["force_approval_blocked"] = True
            path.append(f"Rule {rid}: approval blocked (policy)")
        elif rtype == "benefit_risk_if_match":
            benefit = True
            path.append(f"Rule {rid}: benefit-risk review required (conditional)")

    return cls, benefit, reviewer, crit_flag, matched, path


def evaluate_row(
    *,
    evaluation_type: str,
    row: RowInput,
    criteria_dict: CriteriaInput,
    component_name: str = "",
) -> Dict[str, Any]:
    """
    Core evaluation. ``row`` / ``criteria_dict`` may be plain dicts or Pydantic models
    (:class:`FmeaRiskEvaluationInput`, :class:`RiskCriteriaConfig`).
    """
    row = _unwrap_row(row)
    criteria_dict = _unwrap_criteria(criteria_dict)
    et = evaluation_type.lower()
    cfg_errors = validate_criteria_config(criteria_dict)
    if cfg_errors:
        return _failure_payload(
            evaluation_type=et,
            validation_errors=cfg_errors,
            decision_path=["Criteria configuration invalid; evaluation aborted."],
        )

    method = (criteria_dict.get("evaluation_method") or "matrix").lower()
    th = criteria_dict.get("score_thresholds") if isinstance(criteria_dict.get("score_thresholds"), dict) else {}

    if et == "initial":
        sev, occ, det = row.get("severity"), row.get("probability"), row.get("detection")
        v_err = validate_fmea_row_inputs(
            evaluation_type="initial",
            severity=sev,
            occurrence=occ,
            detection=det,
            residual_severity=None,
            residual_occurrence=None,
            residual_detection=None,
        )
    else:
        sev, occ, det = row.get("residual_severity"), row.get("residual_probability"), row.get("residual_detection")
        v_err = validate_fmea_row_inputs(
            evaluation_type="residual",
            severity=row.get("severity"),
            occurrence=row.get("probability"),
            detection=row.get("detection"),
            residual_severity=sev,
            residual_occurrence=occ,
            residual_detection=det,
        )
    if v_err:
        return _failure_payload(evaluation_type=et, validation_errors=v_err, decision_path=v_err)

    decision_path: List[str] = []
    matched_rules: List[str] = []

    assert sev is not None and occ is not None

    special = criteria_dict.get("special_rules") if isinstance(criteria_dict.get("special_rules"), dict) else {}

    corpus = build_text_corpus(row, component_name)
    corpus_lower = corpus.lower()

    sev_row = int(sev)
    sev_fm, ch_match, sys_ver_req, ch_rev, mx_floor = _apply_critical_hazard_phase(
        row=row,
        special=special,
        corpus_lower=corpus_lower,
        sev_orig=sev_row,
        matched_rules=matched_rules,
        decision_path=decision_path,
    )

    si, pi, map_path = map_to_matrix_indices(severity=sev_fm, occurrence=int(occ), criteria_dict=criteria_dict)
    decision_path.extend(map_path)

    if mx_floor is not None:
        before_si = si
        si = max(si, mx_floor)
        if si != before_si:
            matched_rules.append("policy:critical_hazard_minimum_severity_matrix_index")
            decision_path.append(
                f"Policy: critical hazard — severity matrix index raised from {before_si} "
                f"to {si} (minimum index {mx_floor})"
            )

    matrix_cls = None
    score_val: Optional[int] = None
    score_cls = None

    if method in ("matrix", "hybrid"):
        matrix_cls, mp = matrix_lookup(criteria_dict, si, pi)
        decision_path.extend(mp)
        matched_rules.append(f"matrix:S{si}xP{pi}=>{matrix_cls}")

    if method in ("score", "hybrid"):
        score_val, score_cls, sp = score_classification(
            severity=sev_fm, occurrence=int(occ), detection=int(det) if det is not None else None, thresholds=th
        )
        decision_path.extend(sp)
        matched_rules.append(f"score:{score_val}=>{score_cls}")

    if method == "matrix":
        base_cls = matrix_cls or "Acceptable"
    elif method == "score":
        base_cls = score_cls or "Acceptable"
    else:
        base_cls = max_classification(matrix_cls, score_cls or "Acceptable")
        decision_path.append(f"Hybrid method: conservative merge => {base_cls}")

    # Residual matrix indices for declarative rules (same S×P mapping as this evaluation pass)
    rsi = rpi = None
    if et == "residual":
        rsi, rpi = si, pi

    ctx = {
        "severity_matrix_idx": si,
        "probability_matrix_idx": pi,
        "residual_severity_matrix_idx": rsi,
        "residual_probability_matrix_idx": rpi,
        "corpus_lower": corpus_lower,
        "current_classification": base_cls,
        "force_benefit_risk": False,
        "force_reviewer": False,
        "force_critical_flag": False,
        "force_approval_blocked": False,
    }

    cls, benefit, reviewer, crit_flag, mrules, rpath = apply_declarative_rules(
        evaluation_type=et,
        base_classification=base_cls,
        special_rules=special,
        ctx=ctx,
    )
    matched_rules.extend(mrules)
    decision_path.extend(rpath)

    reviewer = reviewer or ch_rev

    # Built-in safety policies (always on; documented paths for auditors)
    if si >= 4:
        benefit = True
        matched_rules.append("policy:severity_S4_benefit_risk")
        decision_path.append("Policy: severity in highest band (S4) requires benefit-risk review")

    if et == "residual" and rsi is not None and rsi >= 3:
        reviewer = True
        matched_rules.append("policy:serious_residual_S3plus_justification")
        decision_path.append("Policy: residual severity in serious/catastrophic band requires documented justification")

    formal_bra_req, cross_fn_req, formal_rel_req, benefit, reviewer = _apply_mandatory_policies(
        row=row,
        evaluation_type=et,
        special=special,
        benefit=benefit,
        reviewer=reviewer,
        matched_rules=matched_rules,
        decision_path=decision_path,
    )

    cls_norm = normalize_classification(cls) or "Acceptable"
    (
        reviewer,
        formal_rel_req,
        res_acc_rationale_req,
        res_alarp_feas_req,
    ) = _apply_residual_acceptability_policies(
        evaluation_type=et,
        cls_norm=cls_norm,
        special=special,
        matched_rules=matched_rules,
        decision_path=decision_path,
        reviewer=reviewer,
        formal_rel_req=formal_rel_req,
    )

    release_blockers: List[str] = []

    if bool(ctx.get("force_approval_blocked")):
        release_blockers.append("Approval blocked by configured criteria rule")
        decision_path.append("Policy: declarative rule blocks approval")
    unacceptable_escalation = _row_bool(row, "additional_controls_reduced_risk") or _row_bool(
        row, "benefit_risk_analysis_approved"
    )
    if cls_norm == "Unacceptable" and not unacceptable_escalation:
        release_blockers.append(
            "Unacceptable: not releasable without attested additional controls reducing risk "
            "or documented approved benefit-risk analysis"
        )
        decision_path.append(
            "Policy: Unacceptable — release requires control reduction or approved benefit-risk analysis"
        )

    just_text = (row.get("reviewer_justification") or "").strip()
    if reviewer and not just_text:
        release_blockers.append("Documented justification required but not provided")
        decision_path.append("Policy: reviewer justification required but not provided")

    if ch_match and _row_bool(row, "critical_hazard_severity_floor_waived") and not just_text:
        release_blockers.append(
            "Critical hazard severity floor waived — documented rationale for the alternate severity is required"
        )
        decision_path.append("Policy: severity floor waiver requires reviewer justification text")

    if ch_match and sys_ver_req and not _row_bool(row, "system_level_verification_recorded"):
        release_blockers.append("System-level verification not recorded (required for critical hazard categories)")
        decision_path.append("Policy: system-level verification required for critical hazard but not attested")

    bra_struct, bra_doc_active, bra_multi = _apply_benefit_risk_workflow_gates(
        row=row,
        special=special,
        formal_bra_req=formal_bra_req,
        benefit=benefit,
        matched_rules=matched_rules,
        decision_path=decision_path,
        release_blockers=release_blockers,
    )
    if formal_bra_req and not bra_struct and not _row_bool(row, "benefit_risk_formal_approval_recorded"):
        release_blockers.append(
            "Benefit-risk formal approval not recorded (mandatory for configured death-severity pathway)"
        )
        decision_path.append("Policy: benefit-risk formal approval required but not recorded")

    if cross_fn_req and not _row_bool(row, "cross_functional_review_completed"):
        release_blockers.append("Cross-functional review (Engineering, Clinical, Quality) not completed")
        decision_path.append("Policy: cross-functional review required but not completed")

    if formal_rel_req and not _row_bool(row, "formal_release_approval_recorded"):
        release_blockers.append("Formal release approval not recorded")
        decision_path.append("Policy: formal release approval required but not recorded")

    if et == "residual" and res_alarp_feas_req:
        if not _row_bool(row, "residual_all_feasible_controls_implemented"):
            release_blockers.append(
                "Residual ALARP: attestation missing — all feasible risk controls have been implemented"
            )
            decision_path.append("Policy: residual ALARP feasibility attestation (controls) not recorded")
        if not _row_bool(row, "residual_further_reduction_not_practicable"):
            release_blockers.append(
                "Residual ALARP: attestation missing — further risk reduction is not practicable"
            )
            decision_path.append("Policy: residual ALARP feasibility attestation (not practicable) not recorded")

    approval_blocked = len(release_blockers) > 0
    acceptable_for_release = not approval_blocked
    release_status = "acceptable_for_release" if acceptable_for_release else "not_acceptable_for_release"

    return {
        "ok": True,
        "evaluation_type": et,
        "classification": cls,
        "risk_score": score_val
        if method in ("score", "hybrid")
        else int(sev_fm) * int(occ) * (int(det) if det is not None else 1),
        "benefit_risk_required": benefit,
        "reviewer_justification_required": reviewer,
        "approval_blocked": approval_blocked,
        "critical_function_flag": crit_flag,
        "critical_hazard_category_match": ch_match,
        "system_level_verification_required": sys_ver_req,
        "input_fmea_severity": sev_row,
        "evaluated_fmea_severity": sev_fm,
        "benefit_risk_formal_approval_required": formal_bra_req,
        "benefit_risk_structured_workflow_active": bra_struct,
        "benefit_risk_documentation_gates_active": bra_doc_active,
        "benefit_risk_multi_party_approval_required": bra_multi,
        "cross_functional_review_required": cross_fn_req,
        "formal_release_approval_required": formal_rel_req,
        "residual_acceptable_rationale_required": res_acc_rationale_req,
        "residual_alarp_feasibility_attestations_required": res_alarp_feas_req,
        "acceptable_for_release": acceptable_for_release,
        "release_status": release_status,
        "release_blockers": release_blockers,
        "matched_rules": matched_rules,
        "decision_path": decision_path,
        "matrix_indices": {"severity": si, "probability": pi},
    }


def explain_decision(result: Dict[str, Any]) -> str:
    lines = [
        f"Evaluation: {result.get('evaluation_type')}",
        f"Classification: {result.get('classification')}",
        f"Input FMEA severity: {result.get('input_fmea_severity')}",
        f"Evaluated FMEA severity (after policies): {result.get('evaluated_fmea_severity')}",
        f"Critical hazard category match: {result.get('critical_hazard_category_match')}",
        f"System-level verification required: {result.get('system_level_verification_required')}",
        f"Benefit-risk required: {result.get('benefit_risk_required')}",
        f"Benefit-risk formal approval required: {result.get('benefit_risk_formal_approval_required')}",
        f"B-R structured workflow active: {result.get('benefit_risk_structured_workflow_active')}",
        f"B-R documentation gates active: {result.get('benefit_risk_documentation_gates_active')}",
        f"B-R multi-party approval required: {result.get('benefit_risk_multi_party_approval_required')}",
        f"Reviewer justification required: {result.get('reviewer_justification_required')}",
        f"Cross-functional review required: {result.get('cross_functional_review_required')}",
        f"Formal release approval required: {result.get('formal_release_approval_required')}",
        f"Residual acceptable rationale required: {result.get('residual_acceptable_rationale_required')}",
        f"Residual ALARP feasibility attestations required: {result.get('residual_alarp_feasibility_attestations_required')}",
        f"Approval blocked: {result.get('approval_blocked')}",
        f"Acceptable for release: {result.get('acceptable_for_release')}",
        f"Release status: {result.get('release_status')}",
        f"Critical function flag: {result.get('critical_function_flag')}",
        "",
        "Release blockers:",
    ]
    for b in result.get("release_blockers") or []:
        lines.append(f"- {b}")
    lines.extend(["", "Decision path:"])
    for step in result.get("decision_path") or []:
        lines.append(f"- {step}")
    return "\n".join(lines)


def evaluate_initial_risk(row: RowInput, criteria_dict: CriteriaInput, component_name: str = "") -> Dict[str, Any]:
    return evaluate_row(evaluation_type="initial", row=row, criteria_dict=criteria_dict, component_name=component_name)


def evaluate_residual_risk(row: RowInput, criteria_dict: CriteriaInput, component_name: str = "") -> Dict[str, Any]:
    return evaluate_row(evaluation_type="residual", row=row, criteria_dict=criteria_dict, component_name=component_name)


def evaluation_to_result(data: Dict[str, Any]) -> RiskEvaluationResult:
    """Wrap a raw engine dict as a Pydantic result (auditable / API-friendly)."""
    return RiskEvaluationResult.from_engine_dict(data)


def evaluate_initial_risk_model(
    row: FmeaRiskEvaluationInput,
    criteria: RiskCriteriaConfig,
    component_name: str = "",
) -> RiskEvaluationResult:
    """Typed entry point: initial evaluation → :class:`RiskEvaluationResult`."""
    return evaluation_to_result(evaluate_initial_risk(row, criteria, component_name))


def evaluate_residual_risk_model(
    row: FmeaRiskEvaluationInput,
    criteria: RiskCriteriaConfig,
    component_name: str = "",
) -> RiskEvaluationResult:
    """Typed entry point: residual evaluation → :class:`RiskEvaluationResult`."""
    return evaluation_to_result(evaluate_residual_risk(row, criteria, component_name))


def row_to_dict(row: Any) -> Dict[str, Any]:
    """SQLAlchemy FMEARow -> dict for engine."""
    return {
        "device_function": getattr(row, "device_function", None),
        "failure_mode": getattr(row, "failure_mode", None),
        "effect": getattr(row, "effect", None),
        "harm": getattr(row, "harm", None),
        "hazard": getattr(row, "hazard", None),
        "cause": getattr(row, "cause", None),
        "severity": getattr(row, "severity", None),
        "probability": getattr(row, "probability", None),
        "detection": getattr(row, "detection", None),
        "mitigation": getattr(row, "mitigation", None),
        "action_taken": getattr(row, "action_taken", None),
        "residual_severity": getattr(row, "residual_severity", None),
        "residual_probability": getattr(row, "residual_probability", None),
        "residual_detection": getattr(row, "residual_detection", None),
        "reviewer_justification": getattr(row, "reviewer_justification", None),
        "benefit_risk_formal_approval_recorded": getattr(row, "benefit_risk_formal_approval_recorded", None),
        "bra_clinical_benefit_documented": getattr(row, "bra_clinical_benefit_documented", None),
        "bra_benefit_vs_residual_risk_documented": getattr(row, "bra_benefit_vs_residual_risk_documented", None),
        "bra_state_of_the_art_documented": getattr(row, "bra_state_of_the_art_documented", None),
        "bra_supporting_evidence_addressed": getattr(row, "bra_supporting_evidence_addressed", None),
        "bra_approval_clinical_medical_recorded": getattr(row, "bra_approval_clinical_medical_recorded", None),
        "bra_approval_quality_regulatory_recorded": getattr(row, "bra_approval_quality_regulatory_recorded", None),
        "bra_approval_design_authority_recorded": getattr(row, "bra_approval_design_authority_recorded", None),
        "cross_functional_review_completed": getattr(row, "cross_functional_review_completed", None),
        "formal_release_approval_recorded": getattr(row, "formal_release_approval_recorded", None),
        "additional_controls_reduced_risk": getattr(row, "additional_controls_reduced_risk", None),
        "benefit_risk_analysis_approved": getattr(row, "benefit_risk_analysis_approved", None),
        "critical_hazard_severity_floor_waived": getattr(row, "critical_hazard_severity_floor_waived", None),
        "risk_eliminated": getattr(row, "risk_eliminated", None),
        "system_level_verification_recorded": getattr(row, "system_level_verification_recorded", None),
        "residual_all_feasible_controls_implemented": getattr(row, "residual_all_feasible_controls_implemented", None),
        "residual_further_reduction_not_practicable": getattr(row, "residual_further_reduction_not_practicable", None),
    }


def criteria_entity_to_dict(criteria: Any) -> Dict[str, Any]:
    return {
        "evaluation_method": getattr(criteria, "evaluation_method", "matrix"),
        "severity_scale": getattr(criteria, "severity_scale", None),
        "probability_scale": getattr(criteria, "probability_scale", None),
        "detection_scale": getattr(criteria, "detection_scale", None),
        "risk_matrix": getattr(criteria, "risk_matrix", None),
        "score_thresholds": getattr(criteria, "score_thresholds", None),
        "special_rules": getattr(criteria, "special_rules", None),
    }


def _row_attr_bool(row: Any, key: str) -> bool:
    return getattr(row, key, None) is True


def _project_attestation_true(project_attestations: Dict[str, Any], key: str) -> bool:
    """Strict: only explicit True counts (None/False omit the attestation)."""
    return project_attestations.get(key) is True


def _get_global_residual_acceptability_policy(special_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Project-level “overall residual risk acceptable” gates (ISO 14971 RMF/RMR alignment).

    ``special_rules.global_residual_acceptability_policy`` — set ``enabled: false`` to skip.
    """
    raw = special_rules.get("global_residual_acceptability_policy")
    if raw is None:
        return {
            "enabled": True,
            "require_residual_classified": True,
            "require_unacceptable_escape_attestation": True,
            "require_no_row_release_blockers": True,
            "require_overall_benefit_risk_profile_attested": True,
            "require_rmr_overall_conclusion_attested": True,
        }
    if not isinstance(raw, dict):
        return {"enabled": False}
    if raw.get("enabled") is False:
        return {"enabled": False}
    return {
        "enabled": True,
        "require_residual_classified": raw.get("require_residual_classified", True),
        "require_unacceptable_escape_attestation": raw.get("require_unacceptable_escape_attestation", True),
        "require_no_row_release_blockers": raw.get("require_no_row_release_blockers", True),
        "require_overall_benefit_risk_profile_attested": raw.get(
            "require_overall_benefit_risk_profile_attested", True
        ),
        "require_rmr_overall_conclusion_attested": raw.get("require_rmr_overall_conclusion_attested", True),
    }


def evaluate_global_residual_acceptability(
    *,
    rows: List[Any],
    criteria_dict: Optional[Dict[str, Any]] = None,
    project_attestations: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Determine whether **overall** residual risk may be considered acceptable for the device
    (aggregate of line items + project-level attestations).

    Does not mutate rows. ``project_attestations`` typically comes from ``ProjectProfile``:
    - ``overall_device_benefit_risk_profile_acceptable``
    - ``rmr_overall_residual_risk_conclusion_documented``
    """
    crit = dict(criteria_dict or {})
    special = crit.get("special_rules") if isinstance(crit.get("special_rules"), dict) else {}
    pol = _get_global_residual_acceptability_policy(special)
    atts = dict(project_attestations or {})

    matched_rules: List[str] = []
    decision_path: List[str] = []
    blockers: List[str] = []

    if not pol.get("enabled"):
        matched_rules.append("global:overall_residual_acceptability_policy_disabled")
        decision_path.append("Global residual acceptability policy disabled — no aggregate gates applied.")
        return {
            "ok": True,
            "overall_acceptable": True,
            "blockers": [],
            "decision_path": decision_path,
            "matched_rules": matched_rules,
            "policy_applied": False,
        }

    matched_rules.append("global:overall_residual_acceptability_policy_active")
    decision_path.append(
        "Global residual risk acceptability (ISO 14971): overall conclusion requires line-item compliance, "
        "no unreleased Unacceptable risks without justification, ALARP/Acceptable lines cleared for release, "
        "acceptable overall benefit–risk profile, and the conclusion documented in the Risk Management Report."
    )

    if len(rows) == 0:
        decision_path.append("No FMEA rows — overall residual risk vacuously acceptable at line-item level.")
        overall = True
        if pol.get("require_overall_benefit_risk_profile_attested") and not atts.get(
            "overall_device_benefit_risk_profile_acceptable"
        ):
            overall = False
            blockers.append(
                "Overall device benefit–risk profile not attested as acceptable (Project Setup / governance)"
            )
        if pol.get("require_rmr_overall_conclusion_attested") and not atts.get(
            "rmr_overall_residual_risk_conclusion_documented"
        ):
            overall = False
            blockers.append(
                "Overall residual risk acceptability conclusion not attested as documented in the Risk Management Report"
            )
        return {
            "ok": True,
            "overall_acceptable": overall and len(blockers) == 0,
            "blockers": blockers,
            "decision_path": decision_path,
            "matched_rules": matched_rules,
            "policy_applied": True,
        }

    for r in rows:
        rid = getattr(r, "id", None)
        rcls_raw = getattr(r, "residual_risk_classification", None)
        if pol.get("require_residual_classified") and (rcls_raw is None or str(rcls_raw).strip() == ""):
            blockers.append(f"FMEA row {rid}: residual risk not classified — run residual evaluation")
            continue

        cls = normalize_classification(rcls_raw) if rcls_raw is not None else None
        if pol.get("require_residual_classified") and cls is None:
            blockers.append(f"FMEA row {rid}: residual classification not recognized")
            continue

        if cls == "Unacceptable" and pol.get("require_unacceptable_escape_attestation"):
            escaped = _row_attr_bool(r, "benefit_risk_analysis_approved") or _row_attr_bool(
                r, "additional_controls_reduced_risk"
            )
            if not escaped:
                blockers.append(
                    f"FMEA row {rid}: residual Unacceptable without approved benefit–risk justification "
                    "or attested additional control reduction"
                )

        if pol.get("require_no_row_release_blockers") and bool(getattr(r, "approval_blocked", False)):
            blockers.append(
                f"FMEA row {rid}: line not acceptable for release (justification/approval/attestation gaps)"
            )

    if pol.get("require_overall_benefit_risk_profile_attested") and not _project_attestation_true(
        atts, "overall_device_benefit_risk_profile_acceptable"
    ):
        blockers.append(
            "Overall device benefit–risk profile not attested as acceptable (record in Project Setup)"
        )
        decision_path.append(
            "Gate: overall benefit–risk profile of the device must be determined acceptable and attested."
        )

    if pol.get("require_rmr_overall_conclusion_attested") and not _project_attestation_true(
        atts, "rmr_overall_residual_risk_conclusion_documented"
    ):
        blockers.append(
            "Overall residual risk acceptability conclusion not attested as documented in the Risk Management Report"
        )
        decision_path.append(
            "Gate: conclusion that overall residual risk is acceptable shall be documented in the Risk Management Report."
        )

    overall = len(blockers) == 0
    if overall:
        decision_path.append(
            "Aggregate check passed: line items and project attestations satisfy configured overall residual acceptability policy."
        )

    return {
        "ok": True,
        "overall_acceptable": overall,
        "blockers": blockers,
        "decision_path": decision_path,
        "matched_rules": matched_rules,
        "policy_applied": True,
    }


def build_global_residual_summary(
    *,
    project_id: str,
    criteria_version: int,
    rows: List[Any],
    top_n: int = 10,
    criteria_dict: Optional[Dict[str, Any]] = None,
    project_attestations: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    def rcls(r: Any) -> Optional[str]:
        return normalize_classification(getattr(r, "residual_risk_classification", None))

    total = len(rows)
    counts = {"Acceptable": 0, "ALARP": 0, "Unacceptable": 0, "Unknown": 0}
    for r in rows:
        c = rcls(r)
        if c in counts:
            counts[c] += 1
        else:
            counts["Unknown"] += 1

    benefit = sum(1 for r in rows if getattr(r, "benefit_risk_required", False))
    blocked = sum(1 for r in rows if getattr(r, "approval_blocked", False))
    crit = sum(1 for r in rows if getattr(r, "critical_function_flag", False))

    unresolved: List[Dict[str, Any]] = []
    for r in rows:
        cls = rcls(r) or "Unknown"
        if cls == "Unacceptable" or getattr(r, "approval_blocked", False) or (
            cls == "ALARP" and getattr(r, "benefit_risk_required", False)
        ):
            unresolved.append(
                {
                    "fmea_row_id": getattr(r, "id", None),
                    "residual_risk_classification": cls,
                    "residual_rpn": getattr(r, "residual_rpn", None),
                    "failure_mode": getattr(r, "failure_mode", None),
                    "effect": getattr(r, "effect", None),
                    "benefit_risk_required": getattr(r, "benefit_risk_required", False),
                    "approval_blocked": getattr(r, "approval_blocked", False),
                    "critical_function_flag": getattr(r, "critical_function_flag", False),
                }
            )
    unresolved.sort(
        key=lambda x: (
            0 if x.get("residual_risk_classification") == "Unacceptable" else 1,
            -(x.get("residual_rpn") or 0),
        )
    )

    summary = {
        "project_id": project_id,
        "criteria_version": criteria_version,
        "total_rows": total,
        "residual_summary": {
            "acceptable": counts["Acceptable"],
            "alarp": counts["ALARP"],
            "unacceptable": counts["Unacceptable"],
            "unknown": counts["Unknown"],
        },
        "benefit_risk_required_count": benefit,
        "approval_blocked_count": blocked,
        "critical_function_count": crit,
        "top_unresolved_risks": unresolved[:top_n],
    }
    summary["global_residual_acceptability"] = evaluate_global_residual_acceptability(
        rows=rows,
        criteria_dict=criteria_dict,
        project_attestations=project_attestations,
    )
    return summary


__all__ = [
    "criteria_entity_to_dict",
    "evaluate_initial_risk",
    "evaluate_initial_risk_model",
    "evaluate_residual_risk",
    "evaluate_residual_risk_model",
    "evaluate_row",
    "evaluation_to_result",
    "explain_decision",
    "row_to_dict",
    "validate_criteria_config",
    "validate_fmea_row_inputs",
    "build_global_residual_summary",
    "evaluate_global_residual_acceptability",
]
