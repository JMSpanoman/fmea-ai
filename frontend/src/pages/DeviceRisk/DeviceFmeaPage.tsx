import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { TableExportBar, ExportColumn } from '../../components/TableExportBar';
import { devicesApi, FmeaRow } from '../../services/devicesApi';

const COLUMNS: ExportColumn[] = [
  { key: 'row_number', header: '#' },
  { key: 'component', header: 'Component' },
  { key: 'failure_mode', header: 'Failure Mode' },
  { key: 'effect', header: 'Effect' },
  { key: 'cause', header: 'Cause' },
  { key: 'severity', header: 'Severity' },
  { key: 'probability', header: 'Probability' },
  { key: 'detectability', header: 'Detectability' },
  { key: 'risk_score', header: 'Risk Score' },
  { key: 'risk_control', header: 'Risk Control' },
  { key: 'verification', header: 'Verification' },
  { key: 'residual_risk', header: 'Residual Risk' },
];

export default function DeviceFmeaPage() {
  const { id: deviceId } = useParams<{ id: string }>();
  const [rows, setRows] = useState<FmeaRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!deviceId) return;
    setLoading(true);
    setError(null);
    devicesApi
      .getFmea(deviceId)
      .then(setRows)
      .catch((e) => {
        console.error(e);
        setError('Failed to load FMEA data.');
      })
      .finally(() => setLoading(false));
  }, [deviceId]);

  if (!deviceId) return null;

  return (
    <>
      <div className="flex items-center justify-between gap-4 mb-3">
        <h2 className="text-lg font-semibold">FMEA</h2>
        <TableExportBar
          title="FMEA"
          data={rows as Record<string, unknown>[]}
          columns={COLUMNS}
          filenameBase={`device-${deviceId.slice(0, 8)}-fmea`}
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
          <div className="overflow-x-auto">
            <DataTable
              data={rows}
              columns={COLUMNS.map((c) => ({ key: c.key, header: c.header }))}
              emptyMessage="No FMEA data for this device."
            />
          </div>
        </Card>
      )}
    </>
  );
}
