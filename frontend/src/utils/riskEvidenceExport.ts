/**
 * Export Risk Item Evidence Pack (HTML/PDF)
 * Includes version history, approvals, AI events, trace links, audit logs
 */

export interface RiskEvidenceData {
  riskItem: any;
  versions: any[];
  approvals: any[];
  aiEvents: any[];
  traceLinks: { from: any[]; to: any[] };
  handoffAuditLogs?: any[];
}

export function exportRiskEvidenceHTML(data: RiskEvidenceData, filename: string): void {
  const html = generateEvidenceHTML(data);
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}-evidence-${Date.now()}.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function generateEvidenceHTML(data: RiskEvidenceData): string {
  const { riskItem, versions, approvals, aiEvents, traceLinks } = data;
  const riskKey = riskItem?.title || riskItem?.id?.slice(0, 8) || 'Unknown';

  return `
<!DOCTYPE html>
<html>
<head>
  <title>Risk Evidence Pack: ${riskKey}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
    h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
    h2 { color: #1e40af; margin-top: 30px; }
    h3 { color: #374151; margin-top: 20px; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f3f4f6; font-weight: bold; }
    .section { margin: 20px 0; padding: 15px; background: #f9fafb; border-radius: 5px; }
    .meta { color: #6b7280; font-size: 0.9em; }
    .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; }
    .badge-success { background: #d1fae5; color: #065f46; }
    .badge-warning { background: #fef3c7; color: #92400e; }
    .badge-info { background: #dbeafe; color: #1e40af; }
  </style>
</head>
<body>
  <h1>Risk Evidence Pack: ${riskKey}</h1>
  <div class="meta">Generated: ${new Date().toLocaleString()}</div>
  
  <div class="section">
    <h2>Risk Item Summary</h2>
    <table>
      <tr><th>ID</th><td>${riskItem?.id || 'N/A'}</td></tr>
      <tr><th>Title</th><td>${riskItem?.title || 'N/A'}</td></tr>
      <tr><th>Hazard</th><td>${riskItem?.current_version?.hazard || riskItem?.hazard || 'N/A'}</td></tr>
      <tr><th>Harm</th><td>${riskItem?.current_version?.harm || riskItem?.harm || 'N/A'}</td></tr>
      <tr><th>Risk Score</th><td>${riskItem?.risk_score || 'N/A'}</td></tr>
      <tr><th>Risk Level</th><td>${riskItem?.risk_level || 'N/A'}</td></tr>
      <tr><th>Risk Acceptability</th><td>${riskItem?.current_version?.risk_acceptability || riskItem?.risk_acceptability || 'N/A'}</td></tr>
      <tr><th>Created</th><td>${riskItem?.created_at ? new Date(riskItem.created_at).toLocaleString() : 'N/A'}</td></tr>
    </table>
  </div>

  <div class="section">
    <h2>Version History (${versions.length})</h2>
    ${versions.length > 0 ? `
    <table>
      <thead>
        <tr>
          <th>Version</th>
          <th>Created</th>
          <th>Changed By</th>
          <th>Change Summary</th>
          <th>Risk Score</th>
        </tr>
      </thead>
      <tbody>
        ${versions.map(v => `
          <tr>
            <td>v${v.version_number}</td>
            <td>${new Date(v.created_at).toLocaleString()}</td>
            <td>${v.changed_by || 'N/A'}</td>
            <td>${v.change_summary || '-'}</td>
            <td>${v.risk_score || 'N/A'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p>No version history</p>'}
  </div>

  <div class="section">
    <h2>Approvals (${approvals.length})</h2>
    ${approvals.length > 0 ? `
    <table>
      <thead>
        <tr>
          <th>Version</th>
          <th>Decision</th>
          <th>Approver</th>
          <th>Date</th>
          <th>Rationale</th>
        </tr>
      </thead>
      <tbody>
        ${approvals.map(a => `
          <tr>
            <td>${a.object_id || 'N/A'}</td>
            <td><span class="badge badge-${a.decision === 'approved' ? 'success' : 'warning'}">${a.decision}</span></td>
            <td>${a.approver_id || 'N/A'}</td>
            <td>${new Date(a.created_at).toLocaleString()}</td>
            <td>${a.rationale || '-'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p>No approvals</p>'}
  </div>

  <div class="section">
    <h2>AI Events (${aiEvents.length})</h2>
    ${aiEvents.length > 0 ? `
    <table>
      <thead>
        <tr>
          <th>Prompt</th>
          <th>Disposition</th>
          <th>Created</th>
          <th>Input Summary</th>
        </tr>
      </thead>
      <tbody>
        ${aiEvents.map(e => `
          <tr>
            <td>${e.prompt_name || 'N/A'}</td>
            <td><span class="badge badge-${e.disposition === 'accepted' ? 'success' : 'info'}">${e.disposition || 'pending'}</span></td>
            <td>${new Date(e.created_at).toLocaleString()}</td>
            <td>${e.input_summary ? e.input_summary.substring(0, 100) + '...' : '-'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p>No AI events</p>'}
  </div>

  <div class="section">
    <h2>Traceability Links</h2>
    <h3>Outgoing Links (${traceLinks.from.length})</h3>
    ${traceLinks.from.length > 0 ? `
    <table>
      <thead>
        <tr>
          <th>To Type</th>
          <th>To ID</th>
          <th>Link Type</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        ${traceLinks.from.map(l => `
          <tr>
            <td>${l.to_type}</td>
            <td>${l.to_id}</td>
            <td>${l.link_type || 'traces_to'}</td>
            <td>${new Date(l.created_at).toLocaleString()}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p>No outgoing links</p>'}
    
    <h3>Incoming Links (${traceLinks.to.length})</h3>
    ${traceLinks.to.length > 0 ? `
    <table>
      <thead>
        <tr>
          <th>From Type</th>
          <th>From ID</th>
          <th>Link Type</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        ${traceLinks.to.map(l => `
          <tr>
            <td>${l.from_type}</td>
            <td>${l.from_id}</td>
            <td>${l.link_type || 'traces_to'}</td>
            <td>${new Date(l.created_at).toLocaleString()}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p>No incoming links</p>'}
  </div>
</body>
</html>
  `;
}

export async function exportRiskEvidencePDF(data: RiskEvidenceData, filename: string): Promise<void> {
  // For now, convert HTML to PDF using browser print
  // In production, you might want server-side PDF generation
  const html = generateEvidenceHTML(data);
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.print();
  }
}

