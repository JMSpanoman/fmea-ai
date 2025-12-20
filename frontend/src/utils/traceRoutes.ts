import { ArtifactType } from "../types/traceability";

/**
 * Helper to get navigation routes for different artifact types
 */
export function getArtifactRoute(
  artifactType: ArtifactType,
  artifactId: string | number,
  projectId: string | number
): string | null {
  const basePath = `/projects/${projectId}`;

  switch (artifactType) {
    case 'risk_item':
      return `${basePath}/risk-items/${artifactId}`;
    case 'risk_item_version':
      // Versions are shown within risk item detail page
      // Extract risk_item_id if possible, otherwise return null
      return null; // Versions don't have standalone pages
    case 'risk_control':
      // Controls are shown within risk item detail page
      return null; // Controls don't have standalone pages
    case 'design_input':
      return `${basePath}/design-inputs/${artifactId}`;
    case 'design_output':
      return `${basePath}/design-outputs/${artifactId}`;
    case 'vv_test':
      return `${basePath}/vv-tests/${artifactId}`;
    case 'capa':
      return `${basePath}/capas/${artifactId}`;
    case 'change_control':
      return `${basePath}/change-controls/${artifactId}`;
    case 'fmea_row':
      return `${basePath}/fmea/${artifactId}`;
    default:
      return null;
  }
}

/**
 * Get display label for artifact type
 */
export function getArtifactTypeLabel(artifactType: string): string {
  const labels: Record<string, string> = {
    risk_item: 'Risk Item',
    risk_item_version: 'Risk Version',
    risk_control: 'Risk Control',
    design_input: 'Design Input',
    design_output: 'Design Output',
    vv_test: 'V&V Test',
    capa: 'CAPA',
    change_control: 'Change Control',
    fmea_row: 'FMEA Row',
  };
  return labels[artifactType] || artifactType;
}

