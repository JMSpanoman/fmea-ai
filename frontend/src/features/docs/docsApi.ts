import type { DocumentInstance, DocStatus } from './docsTypes';
import api from '../../axios';
import { documentsApi } from '../../services/apiPhase3';
import type { Document as BackendDocument } from '../../types';

const storageKey = (projectId: string) => `smartqs.docs.instances:${projectId}`;

export async function loadProjectDocInstances(projectId: string): Promise<Record<string, DocumentInstance>> {
  try {
    const raw = localStorage.getItem(storageKey(projectId));
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, DocumentInstance>;
    return parsed || {};
  } catch {
    return {};
  }
}

export async function saveProjectDocInstances(
  projectId: string,
  instances: Record<string, DocumentInstance>
): Promise<void> {
  localStorage.setItem(storageKey(projectId), JSON.stringify(instances));
}

function mapBackendStatus(status?: string): DocStatus {
  if (status === 'approved') return 'approved';
  if (status === 'in_review') return 'in_review';
  if (status === 'draft') return 'draft';
  // treat obsolete or unknown as draft-ish (can be adjusted later)
  return 'draft';
}

export async function loadConnectedProjectDocInstances(
  projectId: string
): Promise<Record<string, DocumentInstance>> {
  // Local first (keeps approvals + any registry-only docs)
  const local = await loadProjectDocInstances(projectId);

  // Backend documents (project-scoped)
  let backendDocs: BackendDocument[] = [];
  try {
    backendDocs = await documentsApi.getAll(projectId);
  } catch {
    // If backend is unavailable, fall back to local-only view
    return local;
  }

  const merged: Record<string, DocumentInstance> = { ...local };
  for (const d of backendDocs) {
    const docTypeId = (d.type || '').toString();
    const prev = merged[docTypeId] || ({ docTypeId } as DocumentInstance);
    merged[docTypeId] = {
      ...prev,
      docTypeId,
      backendDocId: d.id,
      status: mapBackendStatus(d.status),
      updatedAt: d.updated_at || d.created_at,
      version: `v${d.version ?? 0}`,
      content: d.content || '',
      // best-effort: treat backend updated_at as "generated" timestamp for now
      lastGeneratedAt: d.updated_at || d.created_at,
    };
  }

  return merged;
}

export async function updateBackendDocument(
  projectId: string,
  backendDocId: string,
  patch: Partial<Pick<BackendDocument, 'content' | 'status' | 'name'>>
): Promise<BackendDocument> {
  return await documentsApi.update(projectId, backendDocId, patch);
}

export async function approveBackendDocument(projectId: string, backendDocId: string): Promise<BackendDocument> {
  return await documentsApi.approve(projectId, backendDocId);
}

export async function generateBackendDocument(
  projectId: string,
  backendDocId: string
): Promise<{ rendered_html: string; new_version_no: number; updated_at?: string }> {
  const res = await api.post(`/projects/${projectId}/documents/${backendDocId}/generate`, {
    components: [],
    version_scope: 'approved_only',
    options: {},
  });
  return res.data;
}

export async function simulateGenerate(docTypeId: string): Promise<{ content: string; version: string }> {
  // lightweight async simulation (no backend yet)
  await new Promise((r) => setTimeout(r, 900));
  const now = new Date().toISOString();
  const version = `v${Math.floor(Date.now() / 1000)}`;
  const content = `# ${docTypeId}\n\nGenerated at: ${now}\n\n(Placeholder draft — replace with backend evidence when wired.)\n`;
  return { content, version };
}

