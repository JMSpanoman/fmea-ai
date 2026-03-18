import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { TableExportBar, ExportColumn } from '../../components/TableExportBar';
import { devicesApi, RiskControlTraceabilityRow } from '../../services/devicesApi';

const COLUMNS: ExportColumn[] = [
  { key: 'risk_item', header: 'Risk Item' },
  { key: 'hazard', header: 'Hazard' },
  { key: 'control', header: 'Control' },
  { key: 'implementation_reference', header: 'Implementation Reference' },
  { key: 'verification', header: 'Verification' },
  { key: 'evidence_reference', header: 'Evidence Reference' },
];

export default function DeviceRiskTraceabilityPage() {
  const { id: deviceId } = useParams<{ id: string }>();
  const [rows, setRows] = useState<RiskControlTraceabilityRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!deviceId) return;
    setLoading(true);
    setError(null);
    devicesApi
      .getRiskTraceability(deviceId)
      .then(setRows)
      .catch((e) => {
        console.error(e);
        setError('Failed to load risk traceability.');
      })
      .finally(() => setLoading(false));
  }, [deviceId]);

  if (!deviceId) return null;

  return (
    <>
      <div className="flex items-center justify-between gap-4 mb-3">
        <h2 className="text-lg font-semibold">Risk Traceability</h2>
        <TableExportBar
          title="Risk Traceability"
          data={rows as Record<string, unknown>[]}
          columns={COLUMNS}
          filenameBase={`device-${deviceId.slice(0, 8)}-risk-traceability`}
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
            emptyMessage="No risk traceability data for this device."
          />
        </Card>
      )}
    </>
  );
}
