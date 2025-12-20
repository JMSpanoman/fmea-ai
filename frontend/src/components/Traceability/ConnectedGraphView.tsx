import React, { useMemo } from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { TraceLink } from '../../api/riskItems';
import { RiskItem, RiskControl } from '../../api/riskItems';
import { getArtifactRoute } from '../../utils/traceRoutes';

type Props = {
  riskItem: RiskItem;
  controls: RiskControl[];
  traceLinks: { from: TraceLink[]; to: TraceLink[] };
  projectId?: string;
  onNavigate?: (route: string) => void;
};

type GraphNode = {
  id: string;
  type: string;
  label: string;
  category: 'risk' | 'control' | 'artifact';
  x?: number;
  y?: number;
};

type GraphEdge = {
  from: string;
  to: string;
  type: string;
  label: string;
};

function buildGraph(
  riskItem: RiskItem,
  controls: RiskControl[],
  traceLinks: { from: TraceLink[]; to: TraceLink[] }
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  // Add risk item as central node
  const riskKey = riskItem.title || riskItem.id.slice(0, 8);
  nodes.push({
    id: riskItem.id,
    type: 'risk_item',
    label: `Risk: ${riskKey}`,
    category: 'risk',
  });

  // Add controls
  controls.forEach(control => {
    const controlKey = control.control_name || control.id.slice(0, 8);
    nodes.push({
      id: control.id,
      type: 'risk_control',
      label: `Control: ${controlKey}`,
      category: 'control',
    });
    
    // Edge from risk to control (implicit relationship)
    edges.push({
      from: riskItem.id,
      to: control.id,
      type: 'has_control',
      label: 'has control',
    });
  });

  // Add outgoing links (to artifacts)
  traceLinks.from.forEach(link => {
    const artifactId = `${link.to_type}:${link.to_id}`;
    const linkTypeLabel = link.link_type || 'traces_to';
    
    // Check if node already exists
    if (!nodes.find(n => n.id === artifactId)) {
      nodes.push({
        id: artifactId,
        type: link.to_type,
        label: `${link.to_type.replace(/_/g, ' ')}: ${link.to_id.slice(0, 8)}`,
        category: 'artifact',
      });
    }

    // Edge from risk/control to artifact
    edges.push({
      from: link.from_type === 'risk_control' && controls.find(c => c.id === link.from_id)
        ? controls.find(c => c.id === link.from_id)!.id
        : riskItem.id,
      to: artifactId,
      type: linkTypeLabel,
      label: linkTypeLabel.replace(/_/g, ' '),
    });
  });

  // Add incoming links (from other artifacts)
  traceLinks.to.forEach(link => {
    const artifactId = `${link.from_type}:${link.from_id}`;
    
    if (!nodes.find(n => n.id === artifactId)) {
      nodes.push({
        id: artifactId,
        type: link.from_type,
        label: `${link.from_type.replace(/_/g, ' ')}: ${link.from_id.slice(0, 8)}`,
        category: 'artifact',
      });
    }

    edges.push({
      from: artifactId,
      to: riskItem.id,
      type: link.link_type || 'traces_to',
      label: (link.link_type || 'traces_to').replace(/_/g, ' '),
    });
  });

  return { nodes, edges };
}

function getNodeColor(category: string): string {
  switch (category) {
    case 'risk':
      return '#ef4444'; // red
    case 'control':
      return '#3b82f6'; // blue
    case 'artifact':
      return '#10b981'; // green
    default:
      return '#6b7280'; // gray
  }
}

export function ConnectedGraphView({
  riskItem,
  controls,
  traceLinks,
  projectId,
  onNavigate,
}: Props) {
  const { nodes, edges } = useMemo(
    () => buildGraph(riskItem, controls, traceLinks),
    [riskItem, controls, traceLinks]
  );

  if (nodes.length === 1 && edges.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center text-text-secondary">
          No connections yet. Add controls or trace links to see the graph.
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Connected Graph</h3>
          <p className="text-sm text-text-secondary">
            {nodes.length} nodes, {edges.length} connections
          </p>
        </div>
      </div>

      {/* Simple list-based graph visualization */}
      <div className="space-y-6">
        {/* Risk Item (Center) */}
        <div className="flex flex-col items-center">
          <div
            className="px-4 py-2 rounded-lg text-white font-medium shadow-md"
            style={{ backgroundColor: getNodeColor('risk') }}
          >
            {nodes.find(n => n.type === 'risk_item')?.label || 'Risk Item'}
          </div>
        </div>

        {/* Controls */}
        {nodes.filter(n => n.type === 'risk_control').length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-text-secondary mb-2">Controls</h4>
            <div className="flex flex-wrap gap-2">
              {nodes
                .filter(n => n.type === 'risk_control')
                .map(node => (
                  <div
                    key={node.id}
                    className="px-3 py-1 rounded-lg text-white text-sm"
                    style={{ backgroundColor: getNodeColor('control') }}
                  >
                    {node.label}
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Outgoing Artifacts */}
        {edges.filter(e => nodes.find(n => n.id === e.from)?.category === 'risk' || nodes.find(n => n.id === e.from)?.category === 'control').length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-text-secondary mb-2">Linked Artifacts</h4>
            <div className="space-y-2">
              {edges
                .filter(e => {
                  const fromNode = nodes.find(n => n.id === e.from);
                  return fromNode?.category === 'risk' || fromNode?.category === 'control';
                })
                .map((edge, idx) => {
                  const toNode = nodes.find(n => n.id === edge.to);
                  if (!toNode) return null;
                  
                  return (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-surface-secondary rounded-lg">
                      <Badge variant="secondary">{edge.label}</Badge>
                      <span className="text-sm">{toNode.label}</span>
                      {onNavigate && toNode.type !== 'risk_control' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            // Extract ID from artifact node ID (format: "type:id")
                            const [type, id] = toNode.id.split(':');
                            if (type && id && projectId) {
                              const route = getArtifactRoute(type as any, id, projectId);
                              if (route && onNavigate) {
                                onNavigate(route);
                              }
                            }
                          }}
                        >
                          View →
                        </Button>
                      )}
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* Incoming Links */}
        {edges.filter(e => {
          const fromNode = nodes.find(n => n.id === e.from);
          return fromNode?.category === 'artifact' && nodes.find(n => n.id === e.to)?.category === 'risk';
        }).length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-text-secondary mb-2">Linked From</h4>
            <div className="space-y-2">
              {edges
                .filter(e => {
                  const fromNode = nodes.find(n => n.id === e.from);
                  const toNode = nodes.find(n => n.id === e.to);
                  return fromNode?.category === 'artifact' && toNode?.category === 'risk';
                })
                .map((edge, idx) => {
                  const fromNode = nodes.find(n => n.id === edge.from);
                  if (!fromNode) return null;
                  
                  return (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-surface-secondary rounded-lg">
                      <span className="text-sm">{fromNode.label}</span>
                      <Badge variant="secondary">{edge.label}</Badge>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-border">
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: getNodeColor('risk') }} />
            <span className="text-text-secondary">Risk Item</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: getNodeColor('control') }} />
            <span className="text-text-secondary">Control</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: getNodeColor('artifact') }} />
            <span className="text-text-secondary">Artifact</span>
          </div>
        </div>
      </div>
    </Card>
  );
}

