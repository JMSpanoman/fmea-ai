import axios from '../axios';

export interface DesignOutput {
  id: string;
  project_id: string;
  text: string;
  source: string;
  linked_input_id?: string;
  created_at: string;
}

export async function getDesignOutput(
  projectId: string,
  designOutputId: string
): Promise<DesignOutput> {
  const response = await axios.get<DesignOutput>(
    `/projects/${projectId}/design-outputs/${designOutputId}`
  );
  return response.data;
}

