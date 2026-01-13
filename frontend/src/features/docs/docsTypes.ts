export type DocAuthority = 'manual' | 'ai' | 'hybrid';

export type DocStatus = 'not_started' | 'draft' | 'in_review' | 'approved';

export interface DocsGroup {
  id: string;
  name: string;
}

export interface DocumentTypeDef {
  id: string; // e.g. "hazard_analysis"
  name: string;
  groupId: string;
  authority: DocAuthority;
  description: string;
  includes?: string[];
  auditorQuestions?: string[];
  required?: boolean; // default true
  supportsAiDraft?: boolean;
  exportable?: boolean;
  dependencies?: string[];
}

export interface DocApproval {
  name: string;
  date: string; // ISO
  comment?: string;
}

export interface DocumentInstance {
  docTypeId: string;
  backendDocId?: string; // maps to /projects/:projectId/documents/:documentId when present
  status: DocStatus;
  updatedAt?: string; // ISO
  owner?: string;
  version?: string;
  impacted?: boolean;
  lastGeneratedAt?: string; // ISO
  content?: string; // markdown or html
  approvals?: DocApproval[];
  // internal helper: stores last change timestamp of dependencies at time of generation/approval
  dependencyStamp?: Record<string, string>;
}

export interface DocsFilters {
  search: string;
  authority: DocAuthority | 'all';
  status: DocStatus | 'all';
  impactedOnly: boolean;
  requiredOnly: boolean;
  sort: 'status' | 'updatedAt' | 'name';
}

