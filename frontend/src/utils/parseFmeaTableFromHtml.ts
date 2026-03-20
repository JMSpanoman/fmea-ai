/**
 * Parse FMEA export HTML tables into structured rows for analytics and version diff.
 *
 * INTEGRATION (backend): Prefer a dedicated endpoint that returns canonical row payloads
 * (stable project_risk_item / fmea_row IDs, numeric fields, mitigation text) instead of
 * re-parsing HTML. Replace callers of this parser when `GET .../documents/{id}/fmea-snapshot?version=`
 * (or similar) is available — keep `matchKey` aligned with server-side row identity.
 */

export type FmeaReportRow = {
  /** Display ID from first column (e.g. FMEA-01) when present */
  rowId: string;
  component: string;
  hazard: string;
  failureMode: string;
  effect: string;
  cause: string;
  s: number;
  o: number;
  d: number;
  rpn: number;
  mitigation: string;
  /** Heuristic extra columns when the table has more than the 11-column simple export */
  actionTaken?: string;
  revisedS?: number;
  revisedO?: number;
  revisedD?: number;
  revisedRpn?: number;
  residualRpn?: number;
  /** Column count on this row (for UI hints) */
  cellCount: number;
  /**
   * Best-effort stable key for row alignment across versions.
   * Uses display ID when it looks like FMEA-##; else composite of component + mode + effect + cause.
   */
  matchKey: string;
};

function stripTags(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function firstInt(text: string): number {
  const n = Number((text || '').match(/\d+/)?.[0] ?? NaN);
  return Number.isFinite(n) ? n : 0;
}

/** Normalize for composite matching when ID is not reliable */
function norm(s: string): string {
  return (s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

export function buildFmeaRowMatchKey(cells: string[]): string {
  const rowId = (cells[0] || '').trim();
  if (/^FMEA-\d+$/i.test(rowId)) {
    return `id:${rowId.toUpperCase()}`;
  }
  const comp = norm(cells[1] || '');
  const fm = norm(cells[3] || '');
  const eff = norm(cells[4] || '');
  const cause = norm(cells[5] || '');
  return `row:${comp}|${fm}|${eff}|${cause}`;
}

/**
 * Parse the first FMEA-style table in HTML document string.
 * Expects thead/tbody with columns aligned to backend `document_control` FMEA export (11 cols minimum).
 */
export function parseFmeaTableFromHtml(html: string | null | undefined): FmeaReportRow[] {
  if (!html || typeof html !== 'string') return [];
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const table = doc.querySelector('table');
    if (!table) return [];
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    return rows.map((row) => {
      const cells = Array.from(row.querySelectorAll('td')).map((c) => stripTags(c.innerHTML || c.textContent || ''));
      const rpnText = cells[9] || '';
      const mitigation = cells[10] || '';
      const rpn = firstInt(rpnText);
      const s = firstInt(cells[6] || '');
      const o = firstInt(cells[7] || '');
      const d = firstInt(cells[8] || '');

      const out: FmeaReportRow = {
        rowId: cells[0] || '',
        component: cells[1] || '',
        hazard: cells[2] || '',
        failureMode: cells[3] || '',
        effect: cells[4] || '',
        cause: cells[5] || '',
        s,
        o,
        d,
        rpn,
        mitigation,
        cellCount: cells.length,
        matchKey: buildFmeaRowMatchKey(cells),
      };

      // Extended layouts (heuristic): align with preview parsing in ProjectDocumentPage (residual at index 14).
      if (cells.length >= 12) {
        out.actionTaken = cells[11] || '';
      }
      if (cells.length >= 15) {
        out.residualRpn = firstInt(cells[14] || '');
        out.revisedRpn = out.residualRpn;
      }
      // If backend adds explicit Rev. S/O/D columns before residual, remap when documented.
      if (cells.length >= 18) {
        out.revisedS = firstInt(cells[12] || '');
        out.revisedO = firstInt(cells[13] || '');
        out.revisedD = firstInt(cells[14] || '');
        out.residualRpn = firstInt(cells[17] || '');
        out.revisedRpn = out.residualRpn;
      }

      return out;
    });
  } catch {
    return [];
  }
}
