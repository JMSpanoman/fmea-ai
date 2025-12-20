import axios from '../axios';

export interface CAPA {
  id: string;
  project_id: string;
  root_cause: string;
  capa_plan: string;
  effectiveness_check?: string;
  linked_risk_ids?: string[];
  created_at: string;
}

export async function getCAPA(
  projectId: string,
  capaId: string
): Promise<CAPA> {
  const response = await axios.get<CAPA>(
    `/projects/${projectId}/capas/${capaId}`
  );
  return response.data;
}

