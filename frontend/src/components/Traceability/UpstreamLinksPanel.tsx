import React, { useMemo } from "react";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { useUpstreamLinks, UpstreamLink } from "../../hooks/useUpstreamLinks";
import { getArtifactRoute } from "../../utils/traceRoutes";
import { ArtifactType } from "../../types/traceability";

type Props = {
  projectId: string | number;
  artifactType: ArtifactType;
  artifactId: string | number;
  title?: string;
  onNavigate?: (route: string) => void; // Optional SPA navigation handler
};

function formatDate(iso?: string) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

function displayFrom(link: UpstreamLink) {
  // Prefer enriched display
  if (link.from_display) return link.from_display;
  if (link.from_key) return `${link.from_type}: ${link.from_key}`;
  return `${link.from_type}: ${String(link.from_id)}`;
}

function copyToClipboard(text: string) {
  if (!text) return;
  navigator.clipboard?.writeText(text).catch(() => {});
}

function LinkRow({
  link,
  projectId,
  onNavigate,
}: {
  link: UpstreamLink;
  projectId: string | number;
  onNavigate?: (route: string) => void;
}) {
  const route = useMemo(() => {
    return getArtifactRoute(link.from_type as ArtifactType, link.from_id, projectId);
  }, [link.from_type, link.from_id, projectId]);

  const label = displayFrom(link);

  const handleNavigate = () => {
    if (!route) {
      copyToClipboard(String(link.from_id));
      return;
    }

    if (onNavigate) {
      onNavigate(route);
    } else {
      window.location.href = route;
    }
  };

  return (
    <div className="flex items-center justify-between gap-2 py-2 border-b last:border-b-0">
      <div className="flex items-center gap-2 min-w-0">
        <Badge>{link.from_type}</Badge>
        {link.link_type ? <Badge>{link.link_type}</Badge> : null}
        <div className="truncate text-sm">
          <span className="font-medium">{label}</span>
          {link.created_at ? (
            <span className="text-xs opacity-70"> · {formatDate(link.created_at)}</span>
          ) : null}
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {route ? (
          <Button
            variant="secondary"
            onClick={handleNavigate}
          >
            View
          </Button>
        ) : (
          <Button
            variant="secondary"
            onClick={() => copyToClipboard(String(link.from_id))}
          >
            Copy ID
          </Button>
        )}
      </div>
    </div>
  );
}

export function UpstreamLinksPanel({
  projectId,
  artifactType,
  artifactId,
  title,
  onNavigate,
}: Props) {
  const { riskLinks, otherLinks, loading, error, refresh } = useUpstreamLinks({
    projectId,
    artifactType,
    artifactId,
  });

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold">
            {title || "Upstream Links"}
          </div>
          <div className="text-xs opacity-70 truncate">
            For {artifactType}:{String(artifactId)}
          </div>
        </div>
        <Button variant="secondary" onClick={refresh} disabled={loading}>
          Refresh
        </Button>
      </div>

      {loading ? (
        <div className="text-sm opacity-70">Loading upstream links…</div>
      ) : error ? (
        <div className="text-sm text-red-600">{error}</div>
      ) : (
        <>
          <div className="mb-4">
            <div className="text-xs font-semibold opacity-70 mb-2">
              Risk Links ({riskLinks.length})
            </div>
            {riskLinks.length === 0 ? (
              <div className="text-sm opacity-70">No risk-related upstream links.</div>
            ) : (
              <div>
                {riskLinks.map((l) => (
                  <LinkRow
                    key={String(l.id ?? `${l.from_type}-${l.from_id}-${l.to_id}`)}
                    link={l}
                    projectId={projectId}
                    onNavigate={onNavigate}
                  />
                ))}
              </div>
            )}
          </div>

          <div>
            <div className="text-xs font-semibold opacity-70 mb-2">
              Other Links ({otherLinks.length})
            </div>
            {otherLinks.length === 0 ? (
              <div className="text-sm opacity-70">No other upstream links.</div>
            ) : (
              <div>
                {otherLinks.map((l) => (
                  <LinkRow
                    key={String(l.id ?? `${l.from_type}-${l.from_id}-${l.to_id}`)}
                    link={l}
                    projectId={projectId}
                    onNavigate={onNavigate}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </Card>
  );
}

