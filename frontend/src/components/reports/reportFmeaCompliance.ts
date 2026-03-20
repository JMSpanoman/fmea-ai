/**
 * FMEA preview row signals for compliance + filtering (client-side, matches export column layout).
 * TODO: Replace with server-provided row flags when export API returns structured row metadata.
 */

export type RiskRowFilter =
  | 'all'
  | 'high'
  | 'medium'
  | 'low'
  | 'unmitigated'
  | 'needs_review'
  | 'closed';

export type SavedReportView = 'executive' | 'engineering' | 'audit';

export type FmeaRowForCompliance = {
  failureMode: string;
  rpn: number;
  s: number;
  o: number;
  d: number;
  mitigation: string;
  residualRpn: number;
};

export function rowMatchesFilter(row: FmeaRowForCompliance, f: RiskRowFilter): boolean {
  const mit = row.mitigation.trim();
  switch (f) {
    case 'all':
      return true;
    case 'high':
      return row.rpn >= 100;
    case 'medium':
      return row.rpn >= 50 && row.rpn < 100;
    case 'low':
      return row.rpn > 0 && row.rpn < 50;
    case 'unmitigated':
      return !mit;
    case 'needs_review':
      return row.rpn >= 50 || !mit;
    case 'closed':
      /* No workflow status in default export — treat "closed" as low RPN with mitigation recorded */
      return row.rpn > 0 && row.rpn < 50 && !!mit;
    default:
      return true;
  }
}

export type ComplianceCheckItem = {
  id: string;
  label: string;
  ok: boolean;
  detail: string;
  severity: 'pass' | 'warn' | 'fail';
};

export type FmeaComplianceSummary = {
  items: ComplianceCheckItem[];
  /** Row indices (0-based) with any compliance flag */
  issueRowIndices: number[];
  /** Row indices needing strong visual (critical) */
  criticalRowIndices: number[];
  hasResidualColumn: boolean;
};

const MIN_SO = 1;
const MAX_SO = 10;

export function analyzeFmeaCompliance(
  rows: FmeaRowForCompliance[],
  tableColumnCount: number
): FmeaComplianceSummary {
  const hasResidualColumn = tableColumnCount >= 15;

  let missingMitigation = 0;
  let missingResidual = 0;
  let incompleteScoring = 0;
  const issueRowIndices: number[] = [];
  const criticalRowIndices: number[] = [];

  rows.forEach((r, i) => {
    const mit = r.mitigation.trim();
    const sodIncomplete =
      r.s < MIN_SO ||
      r.s > MAX_SO ||
      r.o < MIN_SO ||
      r.o > MAX_SO ||
      r.d < MIN_SO ||
      r.d > MAX_SO ||
      r.rpn < 1;
    const noMit = !mit;
    const resMissing = hasResidualColumn && (!r.residualRpn || r.residualRpn < 1);

    if (noMit || sodIncomplete || resMissing) {
      issueRowIndices.push(i);
    }
    if (noMit && r.rpn >= 100) {
      criticalRowIndices.push(i);
    }
    if (noMit) missingMitigation += 1;
    if (resMissing) missingResidual += 1;
    if (sodIncomplete) incompleteScoring += 1;
  });

  const items: ComplianceCheckItem[] = [
    {
      id: 'mitigation',
      label: 'Mitigation / recommended actions',
      ok: missingMitigation === 0,
      detail:
        missingMitigation === 0
          ? 'All visible rows include mitigation text.'
          : `${missingMitigation} row(s) missing mitigation text in the export.`,
      severity: missingMitigation === 0 ? 'pass' : missingMitigation >= rows.length / 2 ? 'fail' : 'warn',
    },
    {
      id: 'residual',
      label: 'Residual risk data',
      ok: !hasResidualColumn || missingResidual === 0,
      detail: !hasResidualColumn
        ? 'This export layout has no residual RPN column (≤14 columns). Use a full FMEA export when available.'
        : missingResidual === 0
          ? 'Residual RPN present where column exists.'
          : `${missingResidual} row(s) missing residual RPN in column 15.`,
      severity: !hasResidualColumn ? 'pass' : missingResidual === 0 ? 'pass' : 'warn',
    },
    {
      id: 'scoring',
      label: 'Initial scoring (S, O, D, RPN)',
      ok: incompleteScoring === 0,
      detail:
        incompleteScoring === 0
          ? 'S, O, D and RPN are in range (1–10 for factors, RPN ≥ 1).'
          : `${incompleteScoring} row(s) with incomplete or out-of-range scoring.`,
      severity: incompleteScoring === 0 ? 'pass' : 'warn',
    },
  ];

  return { items, issueRowIndices, criticalRowIndices, hasResidualColumn };
}

/** Presets for saved views — user can still override filter / compliance toggle manually */
export const SAVED_VIEW_PRESETS: Record<
  SavedReportView,
  { label: string; description: string; complianceMode: boolean; riskFilter: RiskRowFilter }
> = {
  executive: {
    label: 'Executive',
    description: 'High-level risk profile and top items; compliance overlay off by default.',
    complianceMode: false,
    riskFilter: 'high',
  },
  engineering: {
    label: 'Engineering',
    description: 'Full table, all rows; turn on Compliance mode when reviewing gaps.',
    complianceMode: false,
    riskFilter: 'all',
  },
  audit: {
    label: 'Audit',
    description: 'Compliance on, version history emphasized in layout.',
    complianceMode: true,
    riskFilter: 'all',
  },
};
