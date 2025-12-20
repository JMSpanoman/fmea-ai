import axios from '../axios';

export interface VVTest {
  id: string;
  project_id: string;
  design_output_id: string;
  test_method: string;
  acceptance_criteria: string;
  rationale?: string;
  created_at: string;
}

export async function getVvTest(
  projectId: string,
  vvTestId: string
): Promise<VVTest> {
  const response = await axios.get<VVTest>(
    `/projects/${projectId}/vv-tests/${vvTestId}`
  );
  return response.data;
}

