import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { TableExportBar, ExportColumn } from '../../components/TableExportBar';
import { devicesApi, ResidualRiskRow } from '../../services/devicesApi';

const COLUMNS: ExportColumn[] = [
  { key: 'row_number', header: '#' },
  { key: 'risk_item', header: 'Risk Item' },
  { key: 'initial_risk', header: 'Initial Risk' },
  { key: 'controls_applied', header: 'Controls Applied' },
  { key: 'residual_severity', header: 'Residual Severity' },
  { key: 'residual_probability', header: 'Residual Probability' },
  { key: 'residual_risk_score', header: 'Residual Risk Score' },
  { key: 'acceptable', header: 'Acceptable?' },
];

export default function DeviceResidualRiskPage() {
  const { id: deviceId } = useParams<{ id: string }>();
  const [rows, setRows] = useState<ResidualRiskRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!deviceId) return;
    setLoading(true);
    setError(null);
    devicesApi
      .getResidualRisk(deviceId)
      .then(setRows)
      .catch((e) => {
        console.error(e);
        setError('Failed to load residual risk.');
      })
      .finally(() => setLoading(false));
  }, [deviceId]);

  if (!deviceId) return null;

  return (
    <>
      <div className="flex items-center justify-between gap-4 mb-3">
        <h2 className="text-lg font-semibold">Residual Risk</h2>
        <TableExportBar
          title="Residual Risk Evaluation"
          data={rows as Record<string, unknown>[]}
          columns={COLUMNS}
          filenameBase={`device-${deviceId.slice(0, 8)}-residual-risk`}
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
            emptyMessage="No residual risk data for this device."
          />
        </Card>
      )}
    </>
  );
}
