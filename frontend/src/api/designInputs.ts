import axios from '../axios';

export interface DesignInput {
  id: string;
  project_id: string;
  text: string;
  source: string;
  linked_risk_ids?: string[];
  created_at: string;
}

export async function getDesignInput(
  projectId: string,
  designInputId: string
): Promise<DesignInput> {
  const response = await axios.get<DesignInput>(
    `/projects/${projectId}/design-inputs/${designInputId}`
  );
  return response.data;
}

