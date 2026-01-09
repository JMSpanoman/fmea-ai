import type { DocumentInstance } from './docsTypes';

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

export async function simulateGenerate(docTypeId: string): Promise<{ content: string; version: string }> {
  // lightweight async simulation (no backend yet)
  await new Promise((r) => setTimeout(r, 900));
  const now = new Date().toISOString();
  const version = `v${Math.floor(Date.now() / 1000)}`;
  const content = `# ${docTypeId}\n\nGenerated at: ${now}\n\n(Placeholder draft — replace with backend evidence when wired.)\n`;
  return { content, version };
}

