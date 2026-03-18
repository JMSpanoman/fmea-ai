/**
 * API client for Device Architecture (SmartRisk Phase 1) and hazard generation.
 */
import api from '../axios';

// ----- Types -----
export interface DeviceArchitectureRecord {
  id: string;
  project_id: string;
  name: string;
  description?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DeviceArchitectureCreate {
  name: string;
  description?: string;
}

export interface DeviceArchitectureUpdate {
  name?: string;
  description?: string;
}

export interface DeviceArchitectureNodeRecord {
  id: string;
  architecture_id: string;
  parent_id?: string | null;
  name: string;
  description?: string | null;
  node_type: string;
  component_type?: string | null;
  sort_order?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DeviceArchitectureNodeCreate {
  name: string;
  description?: string;
  node_type: string;
  component_type?: string;
  parent_id?: string;
  sort_order?: number;
}

export interface DeviceArchitectureNodeUpdate {
  name?: string;
  description?: string;
  node_type?: string;
  component_type?: string;
  parent_id?: string;
  sort_order?: number;
}

export interface DeviceInterfaceRecord {
  id: string;
  architecture_id: string;
  from_node_id: string;
  to_node_id: string;
  name?: string | null;
  description?: string | null;
  interface_type?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DeviceInterfaceCreate {
  from_node_id: string;
  to_node_id: string;
  name?: string;
  description?: string;
  interface_type?: string;
}

export interface DeviceInterfaceUpdate {
  name?: string;
  description?: string;
  interface_type?: string;
}

export interface DeviceArchitectureDetail extends DeviceArchitectureRecord {
  nodes: DeviceArchitectureNodeRecord[];
  interfaces: DeviceInterfaceRecord[];
}

export interface SuggestedHazard {
  source_type: string;
  source_id: string;
  source_name: string;
  source_extra?: string | null;
  rule_id: string;
  hazard_library_id: string;
  hazard_code?: string | null;
  hazard_name?: string | null;
  hazard_description?: string | null;
}

export interface GenerateHazardsRequest {
  create_risk_items?: boolean;
  created_by?: string | null;
}

export interface GenerateHazardsResponse {
  suggestions: SuggestedHazard[];
  created_risk_item_ids?: string[] | null;
}

export interface HazardLogRow {
  source_type: string;
  source_id: string;
  source_name: string;
  source_extra?: string | null;
  hazard_code?: string | null;
  hazard_name?: string | null;
  hazard_description?: string | null;
  hazard_library_id: string;
  risk_item_id?: string | null;
}

export interface HazardLogTable {
  architecture_id: string;
  architecture_name: string;
  project_id: string;
  rows: HazardLogRow[];
}

// ----- API -----
function base(projectId: string) {
  return `/projects/${projectId}/device-architectures`;
}

export const deviceArchitectureApi = {
  list(projectId: string): Promise<DeviceArchitectureRecord[]> {
    return api.get(base(projectId)).then((r) => r.data);
  },

  get(projectId: string, architectureId: string): Promise<DeviceArchitectureDetail> {
    return api.get(`${base(projectId)}/${architectureId}`).then((r) => r.data);
  },

  create(projectId: string, data: DeviceArchitectureCreate): Promise<DeviceArchitectureRecord> {
    return api.post(base(projectId), data).then((r) => r.data);
  },

  update(
    projectId: string,
    architectureId: string,
    data: DeviceArchitectureUpdate
  ): Promise<DeviceArchitectureRecord> {
    return api.patch(`${base(projectId)}/${architectureId}`, data).then((r) => r.data);
  },

  delete(projectId: string, architectureId: string): Promise<void> {
    return api.delete(`${base(projectId)}/${architectureId}`);
  },

  // Nodes
  listNodes(
    projectId: string,
    architectureId: string,
    parentId?: string | null
  ): Promise<DeviceArchitectureNodeRecord[]> {
    const params = parentId != null ? { parent_id: parentId } : {};
    return api
      .get(`${base(projectId)}/${architectureId}/nodes`, { params })
      .then((r) => r.data);
  },

  createNode(
    projectId: string,
    architectureId: string,
    data: DeviceArchitectureNodeCreate
  ): Promise<DeviceArchitectureNodeRecord> {
    return api
      .post(`${base(projectId)}/${architectureId}/nodes`, data)
      .then((r) => r.data);
  },

  updateNode(
    projectId: string,
    architectureId: string,
    nodeId: string,
    data: DeviceArchitectureNodeUpdate
  ): Promise<DeviceArchitectureNodeRecord> {
    return api
      .patch(`${base(projectId)}/${architectureId}/nodes/${nodeId}`, data)
      .then((r) => r.data);
  },

  deleteNode(
    projectId: string,
    architectureId: string,
    nodeId: string
  ): Promise<void> {
    return api.delete(`${base(projectId)}/${architectureId}/nodes/${nodeId}`);
  },

  // Interfaces
  listInterfaces(
    projectId: string,
    architectureId: string
  ): Promise<DeviceInterfaceRecord[]> {
    return api.get(`${base(projectId)}/${architectureId}/interfaces`).then((r) => r.data);
  },

  createInterface(
    projectId: string,
    architectureId: string,
    data: DeviceInterfaceCreate
  ): Promise<DeviceInterfaceRecord> {
    return api
      .post(`${base(projectId)}/${architectureId}/interfaces`, data)
      .then((r) => r.data);
  },

  updateInterface(
    projectId: string,
    architectureId: string,
    interfaceId: string,
    data: DeviceInterfaceUpdate
  ): Promise<DeviceInterfaceRecord> {
    return api
      .patch(`${base(projectId)}/${architectureId}/interfaces/${interfaceId}`, data)
      .then((r) => r.data);
  },

  deleteInterface(
    projectId: string,
    architectureId: string,
    interfaceId: string
  ): Promise<void> {
    return api.delete(
      `${base(projectId)}/${architectureId}/interfaces/${interfaceId}`
    );
  },

  // Hazard generation
  generateHazards(
    projectId: string,
    architectureId: string,
    options?: GenerateHazardsRequest,
    onlyActiveRules = true
  ): Promise<GenerateHazardsResponse> {
    const params = { only_active_rules: onlyActiveRules };
    return api
      .post(
        `${base(projectId)}/${architectureId}/generate-hazards`,
        options ?? {},
        { params }
      )
      .then((r) => r.data);
  },

  getHazardLog(
    projectId: string,
    architectureId: string,
    onlyActiveRules = true
  ): Promise<HazardLogTable> {
    return api
      .get(`${base(projectId)}/${architectureId}/hazard-log`, {
        params: { only_active_rules: onlyActiveRules },
      })
      .then((r) => r.data);
  },
};
