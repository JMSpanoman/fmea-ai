import type { DocsGroup, DocumentTypeDef } from './docsTypes';

export const docsGroups: DocsGroup[] = [
  { id: 'risk_management_core', name: 'Risk Management Core' },
  { id: 'design_controls', name: 'Design Controls' },
  { id: 'vv_vc_clinical', name: 'Verification, Validation & Clinical' },
  { id: 'traceability_impact', name: 'Traceability & Impact' },
  { id: 'post_market_capa', name: 'Post-Market & CAPA' },
  { id: 'usability_hf', name: 'Usability & Human Factors' },
  { id: 'quality_system_governance', name: 'Quality System & Governance' },
  { id: 'regulatory_audit_outputs', name: 'Regulatory & Audit Outputs' },
];

const req = (d: Partial<DocumentTypeDef>) => ({
  required: true,
  supportsAiDraft: false,
  exportable: true,
  dependencies: [],
  ...d,
});

export const documentTypes: DocumentTypeDef[] = [
  // 1) Risk Management Core
  req({
    id: 'rmp',
    name: 'Risk Management Plan (RMP)',
    groupId: 'risk_management_core',
    authority: 'manual',
    description: 'Scope, intended use, methodology, acceptability criteria, roles, and governance.',
    includes: [
      'Intended use, scope, and component list',
      'Risk acceptability criteria and decision rules',
      'Roles, reviews, and lifecycle governance',
    ],
    auditorQuestions: [
      'Show me your risk management plan and acceptance criteria.',
      'How do you control changes and keep the RMF current?',
      'Who reviews/approves risk activities and when?',
    ],
    exportable: true,
  }),
  req({
    id: 'risk_acceptability_criteria',
    name: 'Risk Acceptability Criteria',
    groupId: 'risk_management_core',
    authority: 'manual',
    description: 'Defines acceptability thresholds and decision rules used for residual risk.',
    includes: [
      'Document header, purpose, scope, regulatory basis',
      'Definitions (risk, severity, probability, ALARP, etc.)',
      'Configurable severity and probability scales',
      'Risk acceptability matrix (Acceptable / ALARP / Unacceptable)',
      'Decision rules and residual risk evaluation rules',
      'Benefit–risk trigger criteria and control effectiveness',
      'Roles, review/approval, traceability, AI transparency',
    ],
  }),
  req({
    id: 'hazard_analysis',
    name: 'Hazard Analysis',
    groupId: 'risk_management_core',
    authority: 'ai',
    supportsAiDraft: true,
    description: 'Hazard identification and chain evidence derived from risk item versions.',
    includes: [
      'Hazard → hazardous situation → harm chain',
      'Version scope and approval status evidence',
      'Coverage summary by component',
    ],
    auditorQuestions: [
      'How did you identify hazards and harms?',
      'Which version of the risk file does this reflect?',
      'Show evidence that unapproved data is excluded/included as intended.',
    ],
  }),
  req({
    id: 'fmea',
    name: 'FMEA',
    groupId: 'risk_management_core',
    authority: 'ai',
    supportsAiDraft: true,
    description: 'Failure Modes and Effects Analysis table and risk ranking.',
    includes: [
      'Failure mode → effects → causes',
      'Severity / probability / detection scoring',
      'Recommended mitigations and residual scoring',
    ],
    auditorQuestions: [
      'How were FMEA scores determined and reviewed?',
      'Which mitigations were implemented and verified?',
      'How do you control updates/versioning of the FMEA?',
    ],
  }),
  req({
    id: 'risk_controls_doc',
    name: 'Risk Control Measures Documentation',
    groupId: 'risk_management_core',
    authority: 'ai',
    supportsAiDraft: true,
    dependencies: ['hazard_analysis', 'fmea'],
    description: 'Risk controls, implementation references, and trace evidence to design and V&V.',
  }),
  req({
    id: 'residual_risk',
    name: 'Residual Risk Evaluation',
    groupId: 'risk_management_core',
    authority: 'ai',
    supportsAiDraft: true,
    dependencies: ['risk_acceptability_criteria', 'risk_controls_doc'],
    description: 'Residual risk evaluation aligned to acceptability criteria.',
  }),
  req({
    id: 'benefit_risk_analysis',
    name: 'Benefit-Risk Analysis',
    groupId: 'risk_management_core',
    authority: 'ai',
    supportsAiDraft: true,
    dependencies: ['residual_risk'],
    description: 'Documents benefit-risk rationale for non-acceptable residual risks.',
  }),
  req({
    id: 'rmf',
    name: 'Risk Management File (RMF/RMR)',
    groupId: 'risk_management_core',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['rmp', 'hazard_analysis', 'risk_controls_doc', 'residual_risk'],
    description: 'Compilation document; combines generated evidence with manual review signoffs.',
    includes: [
      'Pointers to hazard analysis, controls, residual risk evaluation',
      'Versioned evidence with review status',
      'Audit-friendly compilation of outputs',
    ],
    auditorQuestions: [
      'Show the complete RMF and the versions used.',
      'Where is residual risk evaluated against acceptability?',
      'How do you ensure the RMF is consistent with traceability and V&V evidence?',
    ],
  }),
  req({
    id: 'risk_management_review',
    name: 'Risk Management Review',
    groupId: 'risk_management_core',
    authority: 'manual',
    dependencies: ['rmf'],
    description: 'Formal review record of the RMF/RMR and conclusions.',
  }),
  // 2) Design Controls
  req({
    id: 'design_dev_plan',
    name: 'Design & Development Plan',
    groupId: 'design_controls',
    authority: 'manual',
    description: 'Plan for design activities, reviews, verification/validation, and responsibilities.',
  }),
  req({
    id: 'design_inputs_doc',
    name: 'Design Inputs Documentation',
    groupId: 'design_controls',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['risk_controls_doc'],
    description: 'Testable requirements derived from risk controls with trace evidence.',
  }),
  req({
    id: 'design_outputs_doc',
    name: 'Design Outputs Documentation',
    groupId: 'design_controls',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['design_inputs_doc'],
    description: 'Implementation artifacts and references (schematics, code, drawings) with trace links.',
  }),
  req({
    id: 'design_reviews',
    name: 'Design Reviews',
    groupId: 'design_controls',
    authority: 'manual',
    dependencies: ['design_inputs_doc', 'design_outputs_doc'],
    description: 'Review minutes and approval records across design phases.',
  }),
  req({
    id: 'design_change_record',
    name: 'Design Change Record',
    groupId: 'design_controls',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['design_outputs_doc', 'traceability_matrix'],
    description: 'Captures changes, rationale, linked impacts, and verification activities.',
  }),

  // 3) Verification, Validation & Clinical
  req({
    id: 'vv_plan',
    name: 'V&V Plan',
    groupId: 'vv_vc_clinical',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['design_inputs_doc'],
    description: 'Plan for verification/validation including methods, acceptance criteria and coverage.',
  }),
  req({
    id: 'vv_evidence',
    name: 'V&V Evidence Report',
    groupId: 'vv_vc_clinical',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['design_outputs_doc', 'design_inputs_doc', 'risk_controls_doc'],
    description: 'Objective verification/validation evidence compiled via trace links.',
  }),
  req({
    id: 'validation_summary',
    name: 'Validation Summary',
    groupId: 'vv_vc_clinical',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['vv_evidence'],
    description: 'High-level conclusions of validation activities with residual gaps and actions.',
  }),
  req({
    id: 'clinical_evaluation',
    name: 'Clinical Evaluation',
    groupId: 'vv_vc_clinical',
    authority: 'manual',
    description: 'Clinical evaluation / literature appraisal / clinical evidence summary as required.',
  }),

  // 4) Traceability & Impact
  req({
    id: 'traceability_matrix',
    name: 'Traceability Matrix',
    groupId: 'traceability_impact',
    authority: 'ai',
    supportsAiDraft: true,
    dependencies: ['design_inputs_doc', 'design_outputs_doc', 'vv_evidence', 'risk_controls_doc'],
    description: 'Cross-artifact trace links: Risk → Control → DI → DO → V&V.',
    includes: [
      'Risk → control → design input → design output → V&V test linkage',
      'Gaps: missing links and shortcut evidence called out',
      'Component-scoped view and export',
    ],
    auditorQuestions: [
      'Show me end-to-end traceability from risk controls to verification evidence.',
      'Where are broken/missing links and how are they addressed?',
      'How do you ensure trace links remain current after changes?',
    ],
  }),
  req({
    id: 'change_impact_analysis',
    name: 'Change Impact Analysis',
    groupId: 'traceability_impact',
    authority: 'manual',
    supportsAiDraft: false,
    dependencies: ['traceability_matrix', 'vv_evidence'],
    description: 'Auto-assisted impact identification of a change on downstream evidence.',
  }),

  // 5) Post-Market & CAPA
  req({
    id: 'pms_plan',
    name: 'PMS Plan',
    groupId: 'post_market_capa',
    authority: 'manual',
    description: 'Post-market surveillance plan and signal management process.',
  }),
  req({
    id: 'pms_report',
    name: 'PMS Report',
    groupId: 'post_market_capa',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['pms_plan'],
    description: 'Periodic post-market report and signal summary.',
  }),
  req({
    id: 'capa',
    name: 'CAPA',
    groupId: 'post_market_capa',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['pms_report'],
    description: 'Corrective and preventive actions with verification of effectiveness.',
  }),

  // 6) Usability & Human Factors
  req({
    id: 'usability_risk_analysis',
    name: 'Usability Risk Analysis',
    groupId: 'usability_hf',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['hazard_analysis'],
    description: 'Use-related hazards and mitigations; aligns with IEC 62366 evidence.',
  }),
  req({
    id: 'hf_validation',
    name: 'Human Factors Validation',
    groupId: 'usability_hf',
    authority: 'hybrid',
    supportsAiDraft: true,
    dependencies: ['usability_risk_analysis'],
    description: 'Human factors validation evidence and conclusions.',
  }),

  // 7) Quality System & Governance
  req({
    id: 'document_control_procedure',
    name: 'Document Control Procedure',
    groupId: 'quality_system_governance',
    authority: 'manual',
    description: 'Defines document lifecycle, approvals, versioning, and training triggers.',
  }),
  req({
    id: 'training_records',
    name: 'Training Records',
    groupId: 'quality_system_governance',
    authority: 'manual',
    description: 'Evidence of personnel training for controlled procedures.',
    exportable: false,
  }),
  req({
    id: 'supplier_risk_assessment',
    name: 'Supplier Risk Assessment',
    groupId: 'quality_system_governance',
    authority: 'manual',
    description: 'Supplier qualification and risk review evidence.',
  }),

  // 8) Regulatory & Audit Outputs
  req({
    id: 'essential_requirements_checklist',
    name: 'Essential Requirements Checklist',
    groupId: 'regulatory_audit_outputs',
    authority: 'manual',
    supportsAiDraft: false,
    dependencies: ['traceability_matrix', 'rmf'],
    description: 'Compile-only checklist mapping requirements to available evidence references (Not assessed by default).',
  }),
  req({
    id: 'submission_index',
    name: 'Submission Index',
    groupId: 'regulatory_audit_outputs',
    authority: 'manual',
    supportsAiDraft: false,
    dependencies: ['audit_package'],
    description: 'Compile-only index of project documents, versions, and statuses.',
  }),
  req({
    id: 'audit_package',
    name: 'Audit Package',
    groupId: 'regulatory_audit_outputs',
    authority: 'manual',
    supportsAiDraft: false,
    dependencies: ['rmf', 'traceability_matrix', 'vv_evidence'],
    description: 'Compile-only audit package view listing artifacts + statuses + gaps.',
  }),
];

export const docTypeById: Record<string, DocumentTypeDef> = Object.fromEntries(
  documentTypes.map((d) => [d.id, d])
);

export const groupById: Record<string, DocsGroup> = Object.fromEntries(docsGroups.map((g) => [g.id, g]));

