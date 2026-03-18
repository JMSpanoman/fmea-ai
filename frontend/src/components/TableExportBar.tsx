import React from 'react';
import { Button } from './ui/Button';

export interface ExportColumn {
  key: string;
  header: string;
}

interface TableExportBarProps {
  title: string;
  data: Record<string, unknown>[];
  columns: ExportColumn[];
  filenameBase: string;
  className?: string;
}

function escapeCsvCell(value: unknown): string {
  if (value == null) return '';
  const s = String(value);
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function toCsv(data: Record<string, unknown>[], columns: ExportColumn[]): string {
  const header = columns.map((c) => escapeCsvCell(c.header)).join(',');
  const rows = data.map((row) =>
    columns.map((c) => escapeCsvCell(row[c.key])).join(',')
  );
  return [header, ...rows].join('\r\n');
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function tableToPrintHtml(
  title: string,
  data: Record<string, unknown>[],
  columns: ExportColumn[]
): string {
  const ths = columns.map((c) => `<th>${escapeHtml(c.header)}</th>`).join('');
  const rows = data.map(
    (row) =>
      `<tr>${columns
        .map((c) => `<td>${escapeHtml(String(row[c.key] ?? ''))}</td>`)
        .join('')}</tr>`
  ).join('');
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${escapeHtml(title)}</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 1rem; }
    h1 { font-size: 1.25rem; margin-bottom: 1rem; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 0.5rem 0.75rem; text-align: left; }
    th { background: #f5f5f5; font-weight: 600; }
  </style>
</head>
<body>
  <h1>${escapeHtml(title)}</h1>
  <table>
    <thead><tr>${ths}</tr></thead>
    <tbody>${rows}</tbody>
  </table>
</body>
</html>`;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function TableExportBar({
  title,
  data,
  columns,
  filenameBase,
  className = '',
}: TableExportBarProps) {
  const handleCsv = () => {
    const csv = toCsv(data, columns);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    downloadBlob(blob, `${filenameBase}.csv`);
  };

  const handleJson = () => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    downloadBlob(blob, `${filenameBase}.json`);
  };

  const handlePrint = () => {
    const html = tableToPrintHtml(title, data, columns);
    const w = window.open('', '_blank');
    if (!w) return;
    w.document.write(html);
    w.document.close();
    w.focus();
    w.print();
    w.close();
  };

  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      <span className="text-sm text-text-secondary mr-1">Export:</span>
      <Button variant="secondary" size="sm" onClick={handleCsv}>
        CSV
      </Button>
      <Button variant="secondary" size="sm" onClick={handleJson}>
        JSON
      </Button>
      <Button variant="secondary" size="sm" onClick={handlePrint}>
        Print
      </Button>
    </div>
  );
}
