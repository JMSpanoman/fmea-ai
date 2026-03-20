import type { TopRiskItem } from '../components/reports/TopRisksPanel';

/**
 * Heuristic parsers for executive "top risks" from exported report HTML.
 * TODO (production): Replace with structured JSON from GET /documents/{id}/export/summary
 * or embedded data-* attributes in server-rendered HTML for stable column mapping.
 */

function parseFirstNumber(text: string): number {
  const m = (text || '').match(/(\d+(?:\.\d+)?)/);
  return m ? parseFloat(m[1]) : 0;
}

function qualitativeScore(cell: string): number {
  const t = (cell || '').toLowerCase();
  if (t.includes('critical')) return 1000;
  if (t.includes('high')) return 100;
  if (t.includes('medium') || t.includes('moderate')) return 50;
  if (t.includes('low')) return 10;
  return parseFirstNumber(cell);
}

type TableData = { headers: string[]; rows: string[][] };

function extractTables(html: string): TableData[] {
  if (!html?.trim()) return [];
  try {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const tables = Array.from(doc.querySelectorAll('table'));
    const out: TableData[] = [];
    for (const table of tables) {
      const headerCells = Array.from(table.querySelectorAll('thead tr th')).map((th) =>
        (th.textContent || '').trim()
      );
      const bodyRows = Array.from(table.querySelectorAll('tbody tr')).map((tr) =>
        Array.from(tr.querySelectorAll('td')).map((td) => (td.textContent || '').trim())
      );
      if (headerCells.length && bodyRows.length) {
        out.push({ headers: headerCells, rows: bodyRows });
      }
    }
    return out;
  } catch {
    return [];
  }
}

function headerKey(h: string): string {
  return h.toLowerCase().replace(/\s+/g, ' ').trim();
}

function colIndex(headers: string[], ...mustInclude: string[]): number {
  const lowered = headers.map(headerKey);
  for (let i = 0; i < lowered.length; i++) {
    const h = lowered[i];
    if (mustInclude.every((k) => h.includes(k))) return i;
  }
  return -1;
}

/**
 * Hazard Analysis export: wide table with Hazard, Init Risk, Res Risk, etc.
 */
function parseHazardAnalysis(tables: TableData[], limit: number): TopRiskItem[] {
  const scored: { score: number; item: TopRiskItem }[] = [];

  for (const { headers, rows } of tables) {
    const hHazard = colIndex(headers, 'hazard');
    const hFail = colIndex(headers, 'failure', 'mode');
    const hCause = colIndex(headers, 'cause');
    const hSit = colIndex(headers, 'hazardous', 'situation');
    const hHarm = colIndex(headers, 'harm');
    const hInitRisk = colIndex(headers, 'init', 'risk');
    const hResRisk = colIndex(headers, 'res', 'risk');
    const hControls = colIndex(headers, 'risk', 'control');
    if (hHazard < 0 && hFail < 0) continue;

    for (const cells of rows) {
      if (!cells.length) continue;
      const init = hInitRisk >= 0 ? cells[hInitRisk] || '' : '';
      const res = hResRisk >= 0 ? cells[hResRisk] || '' : '';
      const score = Math.max(qualitativeScore(init), qualitativeScore(res), parseFirstNumber(init), parseFirstNumber(res));

      const title = (hFail >= 0 && cells[hFail]) || (hHazard >= 0 && cells[hHazard]) || '—';
      const hazard = hHazard >= 0 ? cells[hHazard] || '' : '';
      const situation = hSit >= 0 ? cells[hSit] || '' : '';
      const harm = hHarm >= 0 ? cells[hHarm] || '' : '';
      const cause = hCause >= 0 ? cells[hCause] || '' : '';
      const controls = hControls >= 0 ? cells[hControls] || '' : '';

      scored.push({
        score: score || 0,
        item: {
          failureMode: title,
          effect: situation || harm || '—',
          cause: cause || hazard || '—',
          rpn: Math.min(999, Math.round(score || qualitativeScore(init + res))),
          mitigation: controls.slice(0, 500) || '—',
          status: init.toLowerCase().includes('high') || res.toLowerCase().includes('high') ? 'Escalated' : 'Review',
          headline: hazard && title !== hazard ? hazard : undefined,
        },
      });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  const seen = new Set<string>();
  const out: TopRiskItem[] = [];
  for (const { item } of scored) {
    const key = `${item.failureMode}|${item.effect}`.slice(0, 200);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(item);
    if (out.length >= limit) break;
  }
  return out;
}

/**
 * Residual risk report: prefer compact tables with residual score / acceptability.
 */
function parseResidualRisk(tables: TableData[], limit: number): TopRiskItem[] {
  const scored: { score: number; item: TopRiskItem }[] = [];

  for (const { headers, rows } of tables) {
    const joined = headers.map(headerKey).join(' | ');
    if (!joined.includes('risk') && !joined.includes('hazard')) continue;

    const idxKey = colIndex(headers, 'risk', 'key');
    const idxId = colIndex(headers, 'risk', 'id');
    const hKey = idxKey >= 0 ? idxKey : idxId;
    const hHazard = colIndex(headers, 'hazard');
    const hResScore =
      colIndex(headers, 'residual', 'score') >= 0
        ? colIndex(headers, 'residual', 'score')
        : colIndex(headers, 'residual', 'risk');
    const hAccept = colIndex(headers, 'acceptability');
    if (hHazard < 0 && hKey < 0) continue;

    for (const cells of rows) {
      if (!cells.length) continue;
      const key = hKey >= 0 ? cells[hKey] || '' : '';
      const hazard = hHazard >= 0 ? cells[hHazard] || '' : '';
      const resText = hResScore >= 0 ? cells[hResScore] || '' : '';
      const acc = hAccept >= 0 ? cells[hAccept] || '' : '';
      const score = Math.max(parseFirstNumber(resText), qualitativeScore(resText + acc));

      scored.push({
        score,
        item: {
          failureMode: key || hazard || 'Risk item',
          effect: hazard || '—',
          cause: acc || '—',
          rpn: Math.min(999, Math.round(score || 50)),
          mitigation: resText || '—',
          status: acc.toLowerCase().includes('unaccept') ? 'Needs action' : 'Tracked',
        },
      });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, limit).map((s) => s.item);
}

/**
 * Public entry: top risks for executive panel from preview HTML.
 */
export function parseTopRisksFromPreviewHtml(previewHtml: string, docType: string, limit = 6): TopRiskItem[] {
  const tables = extractTables(previewHtml);
  if (!tables.length) return [];

  switch (docType) {
    case 'hazard_analysis':
      return parseHazardAnalysis(tables, limit);
    case 'residual_risk':
      return parseResidualRisk(tables, limit);
    case 'risk_controls_doc':
      // TODO: Aggregate per-control records from export HTML or use GET /risk-controls/summary?project=&doc=
      return [];
    case 'benefit_risk_analysis':
      // TODO: Parse structured sections when export uses stable section anchors or JSON-LD
      return [];
    default:
      return [];
  }
}

/** Band counts for charts — prefer columns whose headers look like risk/acceptability. */
export function parseQualitativeRiskBands(
  previewHtml: string,
  docType: string
): { high: number; medium: number; low: number } {
  if (docType === 'fmea') {
    return { high: 0, medium: 0, low: 0 };
  }

  const tables = extractTables(previewHtml);
  let high = 0,
    medium = 0,
    low = 0;

  const bump = (text: string) => {
    const t = (text || '').toLowerCase();
    if (t.includes('high') || t.includes('critical') || t.includes('unacceptable')) high += 1;
    else if (t.includes('medium') || t.includes('moderate')) medium += 1;
    else if (t.includes('low') && t.length < 48) low += 1;
  };

  for (const { headers, rows } of tables) {
    const riskCols = headers
      .map((h, i) => ({ h: h.toLowerCase(), i }))
      .filter(
        ({ h }) =>
          h.includes('risk') ||
          h.includes('accept') ||
          h.includes('level') ||
          h.includes('severity') ||
          h.includes('residual') ||
          h.includes('initial')
      )
      .map((x) => x.i);

    if (riskCols.length) {
      for (const cells of rows) {
        for (const ci of riskCols) {
          if (cells[ci] != null) bump(cells[ci]);
        }
      }
    } else {
      /* Fallback: one pass per row (reduces noise vs scanning every numeric cell) */
      for (const cells of rows) {
        bump(cells.slice(-3).join(' '));
      }
    }
  }

  return { high, medium, low };
}
