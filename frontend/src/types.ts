// src/types.ts

export interface FmeaRow {
  id: number;
  location: string;
  component: string;
  failure_mode: string;
  effect: string;
  cause: string;
  severity: number;
  probability: number;
  detection: number;
  rpn: number;
  mitigation: string;
  action_taken: string;
  revised_severity: number;
  revised_probability: number;
  revised_detection: number;
  revised_rpn: number;
}
