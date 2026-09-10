import type { Document } from '../../../types';

export function makeDocument(overrides: Partial<Document> & Pick<Document, 'id' | 'type'>): Document {
  return {
    project_id: 'proj-1',
    name: overrides.name || overrides.type,
    version: 1,
    status: 'draft',
    content: 'draft content',
    created_at: '2026-09-01T00:00:00.000Z',
    updated_at: '2026-09-01T00:00:00.000Z',
    ...overrides,
  };
}

export function pacemakerLikeDocuments(): Document[] {
  const approved = [
    'design_inputs_doc',
    'design_outputs_doc',
    'document_control_procedure',
    'training_records',
    'supplier_risk_assessment',
    'design_reviews',
  ];
  const drafts = [
    'rmp',
    'hazard_analysis',
    'fmea',
    'risk_controls_doc',
    'residual_risk',
    'rmf',
    'traceability_matrix',
    'vv_evidence',
    'capa',
    'design_change_record',
    'pms_plan',
    'usability_file',
    'clinical_eval',
    'benefit_risk_analysis',
    'risk_acceptability_criteria',
    'risk_management_review',
    'design_dev_plan',
    'vv_plan',
    'audit_package',
    'submission_index',
    'essential_requirements_checklist',
    'dhf',
    'dmr',
    'sop',
  ];

  const docs: Document[] = [];
  approved.forEach((type, index) => {
    docs.push(
      makeDocument({
        id: `approved-${index}`,
        type,
        name: type,
        status: 'approved',
        content: 'approved content',
      })
    );
  });
  drafts.forEach((type, index) => {
    docs.push(
      makeDocument({
        id: `draft-${index}`,
        type,
        name: type === 'capa' ? 'CAPA' : type === 'design_reviews' ? 'Design Reviews' : type,
        status: 'draft',
        content: 'draft content',
        updated_at: '2026-01-15T19:34:53.000Z',
      })
    );
  });
  return docs;
}
