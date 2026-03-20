/**
 * Scoped CSS for backend-rendered HTML tables inside `.report-preview`.
 * Screen: sticky thead inside scroll container; Print: static thead, preserved banding/RPN tints.
 */
export function buildReportPreviewTableCss(isFmea: boolean): string {
  const fmeaRpnRules = isFmea
    ? `
        .report-preview tbody td:nth-child(10),
        .report-preview tbody td:nth-child(15) {
          text-align: center;
          font-variant-numeric: tabular-nums;
          font-weight: 600;
          min-width: 4.25rem;
        }
        .report-preview tbody td.rpn-high {
          background: #fef2f2 !important;
          color: #7f1d1d;
          box-shadow: inset 3px 0 0 0 #dc2626;
        }
        .report-preview tbody td.rpn-medium {
          background: #fffbeb !important;
          color: #78350f;
          box-shadow: inset 3px 0 0 0 #f59e0b;
        }
        .report-preview tbody td.rpn-low {
          background: #f0fdf4 !important;
          color: #14532d;
          box-shadow: inset 3px 0 0 0 #22c55e;
        }
        .report-preview tbody td.rpn-neutral {
          background: #fafafa !important;
          color: #525252;
        }
        .report-preview tbody tr.report-row-filtered-out {
          display: none !important;
        }
        .report-preview tbody tr.report-compliance-issue td:first-child {
          box-shadow: inset 3px 0 0 0 #d97706;
        }
        .report-preview tbody tr.report-compliance-critical td:first-child {
          box-shadow: inset 3px 0 0 0 #dc2626;
        }
        .report-preview tbody td.compliance-mit-empty {
          background: #fff7ed !important;
          box-shadow: inset 0 0 0 1px #fed7aa;
        }
        .report-preview tbody td.compliance-res-empty {
          background: #f8fafc !important;
          box-shadow: inset 0 0 0 1px #cbd5e1;
        }
      `
    : '';

  return `
    .report-preview-inner { position: relative; min-width: 0; }
    .report-preview table {
      width: 100%;
      min-width: min(100%, 720px);
      border-collapse: separate;
      border-spacing: 0;
      table-layout: auto;
    }
    .report-preview thead {
      position: relative;
      z-index: 2;
    }
    .report-preview th,
    .report-preview td {
      border: 1px solid #d4d4d4;
      padding: 0.5rem 0.625rem;
      vertical-align: top;
      white-space: normal;
      word-break: break-word;
      overflow-wrap: anywhere;
      font-size: 0.8125rem;
      line-height: 1.5;
      color: #171717;
    }
    .report-preview thead th {
      position: sticky;
      top: 0;
      background: #f5f5f5;
      z-index: 3;
      font-size: 0.6875rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #525252;
      font-weight: 700;
      border-bottom: 1px solid #a3a3a3;
      box-shadow: 0 1px 0 0 #a3a3a3;
    }
    .report-preview tbody tr:nth-child(even) td {
      background: #fafafa;
    }
    .report-preview tbody tr:nth-child(even) td.rpn-high,
    .report-preview tbody tr:nth-child(even) td.rpn-medium,
    .report-preview tbody tr:nth-child(even) td.rpn-low,
    .report-preview tbody tr:nth-child(even) td.rpn-neutral {
      background-image: none;
    }
    @media (hover: hover) and (pointer: fine) {
      .report-preview tbody tr:hover td {
        background: #f5f5f5 !important;
      }
      .report-preview tbody tr:nth-child(even):hover td {
        background: #eeeeee !important;
      }
    }
    ${fmeaRpnRules}

    @media print {
      .report-preview thead th {
        position: static;
        box-shadow: none;
        background: #f5f5f5 !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      .report-preview th,
      .report-preview td {
        border-color: #a3a3a3 !important;
      }
      .report-preview tbody tr:hover td,
      .report-preview tbody tr:nth-child(even):hover td {
        background: inherit !important;
      }
      .report-preview tbody tr:nth-child(even) td {
        background: #fafafa !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      .report-preview tbody tr:nth-child(even) td.rpn-high,
      .report-preview tbody tr:nth-child(even) td.rpn-medium,
      .report-preview tbody tr:nth-child(even) td.rpn-low {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
    }
  `;
}
