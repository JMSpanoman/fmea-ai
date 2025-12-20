import axios from '../axios';

export interface ChangeControl {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  reason?: string;
  status: string;
  linked_risk_ids?: string[];
  created_at: string;
}

export async function getChangeControl(
  projectId: string,
  changeId: string
): Promise<ChangeControl> {
  const response = await axios.get<ChangeControl>(
    `/projects/${projectId}/changes/${changeId}`
  );
  return response.data;
}

