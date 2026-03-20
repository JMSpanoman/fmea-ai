/**
 * Pure diff logic for FMEA report rows parsed from HTML snapshots.
 *
 * INTEGRATION (backend): When the API returns per-field change metadata or row UUIDs,
 * replace `matchKey` alignment with server keys and optionally trust server `diff` blobs
 * (similar to `FmeaVersion.diff` in types) instead of client-side comparison.
 */

import type { FmeaReportRow } from '../../utils/parseFmeaTableFromHtml';

export type DiffTone = 'neutral' | 'added' | 'removed' | 'improved' | 'worsened' | 'changed';

export type FieldDiff = {
  tone: DiffTone;
  before: string;
  after: string;
};

export type FmeaDiffRowStatus = 'unchanged' | 'added' | 'removed' | 'modified';

export type FmeaDiffRow = {
  matchKey: string;
  status: FmeaDiffRowStatus;
  left: FmeaReportRow | null;
  right: FmeaReportRow | null;
  fields: Partial<Record<FmeaDiffFieldKey, FieldDiff>>;
};

export type FmeaDiffFieldKey =
  | 's'
  | 'o'
  | 'd'
  | 'rpn'
  | 'mitigation'
  | 'actionTaken'
  | 'revisedS'
  | 'revisedO'
  | 'revisedD'
  | 'revisedRpn';

const NUMERIC_RISK_KEYS: FmeaDiffFieldKey[] = ['s', 'o', 'd', 'rpn', 'revisedS', 'revisedO', 'revisedD', 'revisedRpn'];

function str(v: string | number | undefined | null): string {
  if (v === undefined || v === null) return '';
  return String(v);
}

/** Higher S/O/D/RPN = worse (typical FMEA 1–10 scales) */
function numericRiskTone(before: number, after: number): DiffTone {
  if (before === after) return 'neutral';
  if (after < before) return 'improved';
  return 'worsened';
}

function textTone(a: string, b: string): DiffTone {
  if (a === b) return 'neutral';
  return 'changed';
}

function compareField(
  key: FmeaDiffFieldKey,
  beforeRaw: string | number | undefined,
  afterRaw: string | number | undefined,
): FieldDiff | null {
  const before = str(beforeRaw).trim();
  const after = str(afterRaw).trim();
  if (before === after) return null;

  if (NUMERIC_RISK_KEYS.includes(key)) {
    const bn = Number(before.match(/^\d+$/) ? before : before.match(/\d+/)?.[0] || NaN);
    const an = Number(after.match(/^\d+$/) ? after : after.match(/\d+/)?.[0] || NaN);
    if (!Number.isFinite(bn) || !Number.isFinite(an)) {
      return { tone: 'changed', before, after };
    }
    return { tone: numericRiskTone(bn, an), before, after };
  }

  return { tone: textTone(before, after), before, after };
}

export function computeFmeaReportDiff(leftRows: FmeaReportRow[], rightRows: FmeaReportRow[]): FmeaDiffRow[] {
  const leftMap = new Map<string, FmeaReportRow>();
  const rightMap = new Map<string, FmeaReportRow>();

  for (const r of leftRows) {
    if (!leftMap.has(r.matchKey)) leftMap.set(r.matchKey, r);
  }
  for (const r of rightRows) {
    if (!rightMap.has(r.matchKey)) rightMap.set(r.matchKey, r);
  }

  const keys = Array.from(new Set([...leftMap.keys(), ...rightMap.keys()])).sort((a, b) => a.localeCompare(b));

  const out: FmeaDiffRow[] = [];

  for (const matchKey of keys) {
    const L = leftMap.get(matchKey) || null;
    const R = rightMap.get(matchKey) || null;

    if (L && !R) {
      out.push({ matchKey, status: 'removed', left: L, right: null, fields: {} });
      continue;
    }
    if (!L && R) {
      out.push({ matchKey, status: 'added', left: null, right: R, fields: {} });
      continue;
    }
    if (!L || !R) continue;

    const fields: Partial<Record<FmeaDiffFieldKey, FieldDiff>> = {};

    const push = (key: FmeaDiffFieldKey, b: string | number | undefined, a: string | number | undefined) => {
      const d = compareField(key, b, a);
      if (d) fields[key] = d;
    };

    push('s', L.s, R.s);
    push('o', L.o, R.o);
    push('d', L.d, R.d);
    push('rpn', L.rpn, R.rpn);
    push('mitigation', L.mitigation, R.mitigation);
    if (L.actionTaken != null || R.actionTaken != null) {
      push('actionTaken', L.actionTaken ?? '', R.actionTaken ?? '');
    }
    if (L.revisedS != null || R.revisedS != null) push('revisedS', L.revisedS ?? L.s, R.revisedS ?? R.s);
    if (L.revisedO != null || R.revisedO != null) push('revisedO', L.revisedO ?? L.o, R.revisedO ?? R.o);
    if (L.revisedD != null || R.revisedD != null) push('revisedD', L.revisedD ?? L.d, R.revisedD ?? R.d);
    const lr = L.revisedRpn ?? L.residualRpn;
    const rr = R.revisedRpn ?? R.residualRpn;
    if (lr != null || rr != null) push('revisedRpn', lr ?? L.rpn, rr ?? R.rpn);

    const status: FmeaDiffRowStatus = Object.keys(fields).length > 0 ? 'modified' : 'unchanged';
    out.push({ matchKey, status, left: L, right: R, fields });
  }

  return out;
}

export function summarizeFmeaDiff(rows: FmeaDiffRow[]) {
  let added = 0;
  let removed = 0;
  let modified = 0;
  let unchanged = 0;
  for (const r of rows) {
    if (r.status === 'added') added++;
    else if (r.status === 'removed') removed++;
    else if (r.status === 'modified') modified++;
    else unchanged++;
  }
  return { added, removed, modified, unchanged, total: rows.length };
}
