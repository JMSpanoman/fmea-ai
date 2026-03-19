"""
Centralized hardcoded defaults for editable Risk Acceptability Criteria wording.
"""

DEFAULT_DECISION_RULE_WORDING = """Risk acceptability is determined by evaluating the combination of severity and probability using the defined risk acceptability matrix.

- Acceptable:
Risks classified as Acceptable do not require further risk reduction. However, risk control measures may still be implemented if they are readily achievable and do not introduce additional risk. The rationale for acceptability shall be documented.

- Acceptable with Justification (ALARP):
Risks classified as Acceptable with Justification require documented evaluation demonstrating that further risk reduction is not reasonably practicable. Additional risk control measures shall be considered and implemented unless they are technically infeasible or disproportionate to the benefit gained. Approval is required.

- Unacceptable:
Risks classified as Unacceptable are not permitted. Risk control measures shall be implemented to reduce the risk to an acceptable level. If risk cannot be reduced, a formal benefit-risk analysis shall be performed and approved prior to acceptance.
"""

DEFAULT_ALARP_TERMINOLOGY = "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)"

DEFAULT_SEVERITY_RATIONALE = """The severity scale is defined to reflect clinically meaningful outcomes associated with medical device hazards, ranging from negligible impact to catastrophic harm including death.

Severity levels are aligned with typical medical device risk management practices and are intended to support consistent evaluation of potential patient harm. The scale emphasizes clinical consequences, reversibility of harm, and the level of medical intervention required.

For this project, the severity definitions are conservatively interpreted due to the implantable and life-sustaining nature of the device. Higher severity categories are emphasized to ensure that potentially serious outcomes are appropriately prioritized during risk evaluation and control.
"""

DEFAULT_PROBABILITY_RATIONALE = """The probability scale is defined to provide a structured and consistent approach to estimating the likelihood of occurrence of hazardous situations.

Where available, probability estimates should be informed by empirical data such as testing, field data, or literature. In early development stages, probability may be estimated qualitatively based on engineering judgment and state-of-the-art knowledge.

The defined categories are intended to support relative comparison of risks rather than precise prediction. For this project, probability assessments are interpreted conservatively due to the critical function of the device and the potential for serious harm.
"""

DEFAULT_MATRIX_RATIONALE = """The risk acceptability matrix defines how combinations of severity and probability are classified into Acceptable, Acceptable with Justification (ALARP), or Unacceptable regions.

The matrix is structured to ensure that risks associated with high severity outcomes are subject to stricter acceptability criteria, even at lower probabilities. Conversely, lower severity risks may be acceptable at higher probabilities, provided the impact is limited.

For this project, the matrix is intentionally conservative due to the implantable and life-sustaining nature of the device. Risks with high severity are generally not considered acceptable without strong justification, and emphasis is placed on risk reduction rather than acceptance.

This matrix serves as a decision-support tool and shall be applied consistently across hazard analyses and residual risk evaluations. Final acceptability decisions require appropriate review and approval.
"""

DEFAULT_DECISION_RULES_RATIONALE = """The decision rules are defined to ensure consistent and transparent application of risk acceptability criteria across the project.

These rules support:
- Objective classification of risks based on defined criteria
- Consistent decision-making across teams
- Documentation of justification for residual risks
- Alignment with ISO 14971 principles for risk evaluation and control

The rules emphasize that risk reduction is preferred over justification wherever feasible. Acceptance of residual risk requires appropriate documentation and review, particularly for risks that fall within the Acceptable with Justification (ALARP) region.

For high-risk scenarios, escalation to benefit-risk analysis ensures that acceptance decisions are supported by consideration of clinical benefits and overall device performance.

These decision rules are intended to guide the risk management process and do not replace the need for expert judgment and cross-functional review.
"""

EDITABLE_DEFAULTS = {
    "decision_rule_wording": DEFAULT_DECISION_RULE_WORDING,
    "alarp_terminology": DEFAULT_ALARP_TERMINOLOGY,
    "severity_rationale": DEFAULT_SEVERITY_RATIONALE,
    "probability_rationale": DEFAULT_PROBABILITY_RATIONALE,
    "matrix_rationale": DEFAULT_MATRIX_RATIONALE,
    "decision_rules_rationale": DEFAULT_DECISION_RULES_RATIONALE,
}

