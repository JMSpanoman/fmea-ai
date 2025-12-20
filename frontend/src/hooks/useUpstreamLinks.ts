import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "../axios";

export type UpstreamLink = {
  id?: string | number;
  project_id?: string | number;
  from_type: string;
  from_id: string | number;
  to_type: string;
  to_id: string | number;
  link_type?: string;
  rationale?: string | null;
  created_at?: string;
  // Optional enrichment fields (backward compatible)
  from_key?: string | null;
  from_display?: string | null;
  to_display?: string | null;
};

export type UpstreamLinksResponse = {
  links: UpstreamLink[];
};

export type UseUpstreamLinksResult = {
  riskLinks: UpstreamLink[];
  otherLinks: UpstreamLink[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

const RISK_FROM_TYPES = new Set(["risk_item", "risk_item_version", "risk_control"]);

function normalizeLinks(raw: any): UpstreamLink[] {
  // Backend might return { links: [...] } or just [...]
  // Also handle { upstream_links: [...], all_upstream: [...] } format
  let linksArray: any[] = [];
  
  if (Array.isArray(raw)) {
    linksArray = raw;
  } else if (raw?.links && Array.isArray(raw.links)) {
    linksArray = raw.links;
  } else if (raw?.upstream_links && Array.isArray(raw.upstream_links)) {
    linksArray = raw.upstream_links;
  } else if (raw?.all_upstream && Array.isArray(raw.all_upstream)) {
    linksArray = raw.all_upstream;
  }

  if (!Array.isArray(linksArray)) return [];

  return linksArray.map((l: any) => ({
    id: l.id ?? l.trace_link_id ?? l.link_id,
    project_id: l.project_id,
    from_type: l.from_type,
    from_id: l.from_id,
    to_type: l.to_type,
    to_id: l.to_id,
    link_type: l.link_type ?? l.relationship ?? l.type,
    rationale: l.rationale ?? null,
    created_at: l.created_at ?? l.createdAt ?? l.timestamp,
    from_key: l.from_key ?? null,
    from_display: l.from_display ?? null,
    to_display: l.to_display ?? null,
  }));
}

export function useUpstreamLinks(params: {
  projectId?: string | number;
  artifactType?: string;
  artifactId?: string | number;
}): UseUpstreamLinksResult {
  const { projectId, artifactType, artifactId } = params;

  const [links, setLinks] = useState<UpstreamLink[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canFetch = Boolean(projectId && artifactType && artifactId);

  const refresh = useCallback(async () => {
    if (!canFetch) return;
    setLoading(true);
    setError(null);

    try {
      const res = await axios.get(
        `/projects/${projectId}/trace/upstream/${artifactType}/${artifactId}`
      );
      const normalized = normalizeLinks(res.data);

      // Sort newest first (if created_at exists)
      normalized.sort((a, b) => {
        const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
        const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
        return tb - ta;
      });

      setLinks(normalized);
    } catch (e: any) {
      const msg =
        e?.response?.data?.detail ||
        e?.response?.data?.message ||
        e?.message ||
        "Failed to load upstream links";
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  }, [canFetch, projectId, artifactType, artifactId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const { riskLinks, otherLinks } = useMemo(() => {
    const risk: UpstreamLink[] = [];
    const other: UpstreamLink[] = [];

    for (const l of links) {
      if (RISK_FROM_TYPES.has(l.from_type)) risk.push(l);
      else other.push(l);
    }

    return { riskLinks: risk, otherLinks: other };
  }, [links]);

  return { riskLinks, otherLinks, loading, error, refresh };
}

