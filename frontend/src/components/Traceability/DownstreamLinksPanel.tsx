import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { TraceLink } from '../../api/riskItems';
import { getArtifactRoute } from '../../utils/traceRoutes';
import { ArtifactType } from '../../types/traceability';

type Props = {
  projectId: string | number;
  links: TraceLink[]; // Links FROM this risk item (outgoing)
  onNavigate?: (route: string) => void;
  title?: string;
};

function getArtifactTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    design_input: 'Design Input',
    design_output: 'Design Output',
    vv_test: 'V&V Test',
    capa: 'CAPA',
    change_control: 'Change Control',
    fmea_row: 'FMEA Row',
  };
  return labels[type] || type;
}

function groupLinksByType(links: TraceLink[]): Record<string, TraceLink[]> {
  const grouped: Record<string, TraceLink[]> = {};
  links.forEach(link => {
    if (!grouped[link.to_type]) {
      grouped[link.to_type] = [];
    }
    grouped[link.to_type].push(link);
  });
  return grouped;
}

export function DownstreamLinksPanel({
  projectId,
  links,
  onNavigate,
  title = 'Downstream Artifacts',
}: Props) {
  if (links.length === 0) {
    return null; // Don't show empty panel
  }

  const grouped = groupLinksByType(links);
  const categories = [
    { key: 'design_input', label: 'Design Inputs' },
    { key: 'design_output', label: 'Design Outputs' },
    { key: 'vv_test', label: 'V&V Tests' },
    { key: 'capa', label: 'CAPAs' },
    { key: 'change_control', label: 'Change Controls' },
    { key: 'fmea_row', label: 'FMEA Rows' },
  ];

  const handleNavigate = (link: TraceLink) => {
    const route = getArtifactRoute(link.to_type as ArtifactType, link.to_id, projectId);
    if (route && onNavigate) {
      onNavigate(route);
    } else if (route) {
      window.location.href = route;
    }
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
          <div className="text-xs opacity-70">
            {links.length} linked artifact{links.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {categories.map((category) => {
          const categoryLinks = grouped[category.key] || [];
          if (categoryLinks.length === 0) return null;

          return (
            <div key={category.key}>
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs font-semibold opacity-70 uppercase tracking-wide">
                  {category.label}
                </div>
                <Badge variant="secondary">{categoryLinks.length}</Badge>
              </div>
              <div className="space-y-2">
                {categoryLinks.map((link) => {
                  const route = getArtifactRoute(link.to_type as ArtifactType, link.to_id, projectId);
                  const displayId = link.to_id.slice(0, 8);

                  return (
                    <div
                      key={link.id}
                      className="flex items-center justify-between p-2 bg-surface-secondary rounded-lg hover:bg-surface-hover transition-colors"
                    >
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <span className="text-sm font-medium text-text-primary truncate">
                          {displayId}
                        </span>
                        {link.link_type && link.link_type !== 'traces_to' && (
                          <Badge variant="outline" className="text-xs shrink-0">
                            {link.link_type}
                          </Badge>
                        )}
                      </div>
                      {route ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleNavigate(link)}
                        >
                          View →
                        </Button>
                      ) : (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            navigator.clipboard?.writeText(link.to_id).catch(() => {});
                          }}
                        >
                          Copy ID
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

