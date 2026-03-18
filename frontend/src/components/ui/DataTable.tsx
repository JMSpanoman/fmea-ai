import React from 'react';
import { Card } from './Card';

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  className?: string;
  cardStyle?: React.CSSProperties;
  /** When true, use light backgrounds and dark text for use on light pages */
  light?: boolean;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  onRowClick,
  emptyMessage = 'No data available',
  className = '',
  cardStyle,
  light = false,
}: DataTableProps<T>) {
  const theadClass = light
    ? 'bg-gray-100 border-b border-gray-200'
    : 'bg-surface-secondary border-b border-border';
  const thClass = light
    ? 'px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider'
    : 'px-6 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider';
  const tdClass = light
    ? 'px-6 py-4 text-sm text-gray-900'
    : 'px-6 py-4 text-sm text-text-primary';
  const emptyClass = light
    ? 'px-6 py-12 text-center text-gray-600'
    : 'px-6 py-12 text-center text-text-secondary';
  const rowHoverClass = light
    ? 'hover:bg-gray-50 transition-smooth'
    : 'hover:bg-surface-secondary/50 transition-smooth';

  return (
    <Card className={`overflow-hidden ${className}`} style={cardStyle ?? (light ? { backgroundColor: '#fff' } : undefined)}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className={`border-b ${theadClass}`}>
            <tr>
              {columns.map((column) => (
                <th key={column.key} className={thClass}>
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className={emptyClass}>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((item, index) => (
                <tr
                  key={index}
                  onClick={() => onRowClick?.(item)}
                  className={`${rowHoverClass} ${onRowClick ? 'cursor-pointer' : ''}`}
                >
                  {columns.map((column) => (
                    <td key={column.key} className={tdClass}>
                      {column.render
                        ? column.render(item)
                        : item[column.key]?.toString() || '-'}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

