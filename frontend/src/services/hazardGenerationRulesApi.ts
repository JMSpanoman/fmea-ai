/**
 * API client for Hazard Generation Rules (SmartRisk Phase 2).
 */
import api from '../axios';

const BASE = '/hazard-generation-rules';

export interface HazardGenerationRuleRecord {
  id: string;
  name?: string | null;
  trigger_type: string;
  component_type?: string | null;
  interface_type?: string | null;
  node_type?: string | null;
  hazard_library_id: string;
  priority?: number | null;
  is_active: boolean;
  condition_json?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface HazardGenerationRuleCreate {
  name?: string;
  trigger_type: string;
  component_type?: string;
  interface_type?: string;
  node_type?: string;
  hazard_library_id: string;
  priority?: number;
  is_active?: boolean;
  condition_json?: string;
}

export interface HazardGenerationRuleUpdate {
  name?: string;
  trigger_type?: string;
  component_type?: string;
  interface_type?: string;
  node_type?: string;
  hazard_library_id?: string;
  priority?: number;
  is_active?: boolean;
  condition_json?: string;
}

export const hazardGenerationRulesApi = {
  list(params?: {
    trigger_type?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<HazardGenerationRuleRecord[]> {
    return api.get(BASE, { params: params ?? {} }).then((r) => r.data);
  },

  get(ruleId: string): Promise<HazardGenerationRuleRecord> {
    return api.get(`${BASE}/${ruleId}`).then((r) => r.data);
  },

  create(data: HazardGenerationRuleCreate): Promise<HazardGenerationRuleRecord> {
    return api.post(BASE, data).then((r) => r.data);
  },

  update(
    ruleId: string,
    data: HazardGenerationRuleUpdate
  ): Promise<HazardGenerationRuleRecord> {
    return api.patch(`${BASE}/${ruleId}`, data).then((r) => r.data);
  },

  delete(ruleId: string): Promise<void> {
    return api.delete(`${BASE}/${ruleId}`);
  },
};
