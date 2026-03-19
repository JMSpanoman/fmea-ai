import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { TableExportBar, ExportColumn } from '../../components/TableExportBar';
import { devicesApi, HazardAnalysisRow } from '../../services/devicesApi';

const COLUMNS: ExportColumn[] = [
  { key: 'row_number', header: '#' },
  { key: 'hazard', header: 'Hazard' },
  { key: 'sequence_of_events', header: 'Sequence of Events' },
  { key: 'hazardous_situation', header: 'Hazardous Situation' },
  { key: 'harm', header: 'Harm' },
  { key: 'severity', header: 'Severity' },
  { key: 'probability', header: 'Probability/Occurrence' },
  { key: 'risk_acceptability_decision', header: 'Acceptability Decision' },
];

export default function DeviceHazardAnalysisPage() {
  const { id: deviceId } = useParams<{ id: string }>();
  const [rows, setRows] = useState<HazardAnalysisRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!deviceId) return;
    setLoading(true);
    setError(null);
    devicesApi
      .getHazardAnalysis(deviceId)
      .then(setRows)
      .catch((e) => {
        console.error(e);
        setError('Failed to load hazard analysis.');
      })
      .finally(() => setLoading(false));
  }, [deviceId]);

  if (!deviceId) return null;

  return (
    <>
      <div className="flex items-center justify-between gap-4 mb-3">
        <h2 className="text-lg font-semibold">Hazard Analysis</h2>
        <TableExportBar
          title="Hazard Analysis"
          data={rows as Record<string, unknown>[]}
          columns={COLUMNS}
          filenameBase={`device-${deviceId.slice(0, 8)}-hazard-analysis`}
        />
      </div>
      {error && (
        <Card className="p-4 mb-4 bg-red-50 border-red-200 text-red-800">
          {error}
        </Card>
      )}
      {loading ? (
        <Card className="p-8 text-center text-text-secondary">Loading…</Card>
      ) : (
        <Card className="overflow-hidden">
          <DataTable
            data={rows}
            columns={COLUMNS.map((c) => ({ key: c.key, header: c.header }))}
            emptyMessage="No hazard analysis data for this device."
          />
        </Card>
      )}
    </>
  );
}
