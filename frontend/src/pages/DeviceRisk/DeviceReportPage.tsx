import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { devicesApi, GeneratedDocumentOut } from '../../services/devicesApi';

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function printReport(title: string, markdown: string) {
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${title.replace(/</g, '&lt;')}</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 1.5rem; max-width: 900px; }
    h1 { font-size: 1.25rem; margin-bottom: 1rem; }
    pre { white-space: pre-wrap; font-size: 0.875rem; line-height: 1.5; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th, td { border: 1px solid #ccc; padding: 0.5rem 0.75rem; text-align: left; }
    th { background: #f5f5f5; }
  </style>
</head>
<body>
  <h1>${title.replace(/</g, '&lt;')}</h1>
  <pre>${markdown.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
</body>
</html>`;
  const w = window.open('', '_blank');
  if (!w) return;
  w.document.write(html);
  w.document.close();
  w.focus();
  w.print();
  w.close();
}

export default function DeviceReportPage() {
  const { id: deviceId } = useParams<{ id: string }>();
  const [doc, setDoc] = useState<GeneratedDocumentOut | null>(null);
  const [generating, setGenerating] = useState(false);
  const [loadingDoc, setLoadingDoc] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = () => {
    if (!deviceId) return;
    setGenerating(true);
    setError(null);
    devicesApi
      .generateReport(deviceId)
      .then((res) => {
        setLoadingDoc(true);
        return devicesApi.getGeneratedDocument(res.id);
      })
      .then(setDoc)
      .catch((e) => {
        console.error(e);
        setError('Failed to generate report.');
      })
      .finally(() => {
        setGenerating(false);
        setLoadingDoc(false);
      });
  };

  const exportMarkdown = () => {
    if (!doc?.content_markdown) return;
    const blob = new Blob([doc.content_markdown], {
      type: 'text/markdown;charset=utf-8',
    });
    downloadBlob(blob, `${doc.title.replace(/\s+/g, '-')}.md`);
  };

  const exportJson = () => {
    if (!doc?.content_json) return;
    try {
      const parsed = JSON.parse(doc.content_json);
      const blob = new Blob([JSON.stringify(parsed, null, 2)], {
        type: 'application/json',
      });
      downloadBlob(blob, `${doc.title.replace(/\s+/g, '-')}.json`);
    } catch {
      const blob = new Blob([doc.content_json], {
        type: 'application/json',
      });
      downloadBlob(blob, `${doc.title.replace(/\s+/g, '-')}.json`);
    }
  };

  const handlePrint = () => {
    if (!doc) return;
    printReport(doc.title, doc.content_markdown || '');
  };

  if (!deviceId) return null;

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
        <h2 className="text-lg font-semibold">Report</h2>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="primary"
            onClick={generateReport}
            disabled={generating || loadingDoc}
          >
            {generating || loadingDoc ? 'Generating…' : 'Generate report'}
          </Button>
          {doc && (
            <>
              <span className="text-sm text-text-secondary">Export:</span>
              <Button variant="secondary" size="sm" onClick={exportMarkdown}>
                Markdown
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={exportJson}
                disabled={!doc.content_json}
              >
                JSON
              </Button>
              <Button variant="secondary" size="sm" onClick={handlePrint}>
                Print
              </Button>
            </>
          )}
        </div>
      </div>
      {error && (
        <Card className="p-4 mb-4 bg-red-50 border-red-200 text-red-800">
          {error}
        </Card>
      )}
      {!doc ? (
        <Card className="p-8 text-center text-text-secondary">
          Generate a report to view and export device risk data (FMEA, hazard
          analysis, traceability, residual risk) as Markdown, JSON, or
          printable HTML.
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <div className="p-4 border-b border-border font-semibold">
            {doc.title}
          </div>
          <div className="p-4 overflow-x-auto">
            <pre className="whitespace-pre-wrap font-sans text-sm text-text-primary">
              {doc.content_markdown || '—'}
            </pre>
          </div>
        </Card>
      )}
    </>
  );
}
