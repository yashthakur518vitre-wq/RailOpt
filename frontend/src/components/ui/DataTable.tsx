import React, { useState } from 'react';
import EmptyState from './EmptyState';

interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string | number;
}

export default function DataTable<T>({ data, columns, keyExtractor }: DataTableProps<T>) {
  if (data.length === 0) return <EmptyState message="No data available" />;

  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow-sm border border-slate-200">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-slate-50 border-b border-slate-200">
            {columns.map(col => (
              <th key={col.key} className="py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {data.map((row) => (
            <tr key={keyExtractor(row)} className="hover:bg-slate-50 transition-colors">
              {columns.map(col => (
                <td key={col.key} className="py-3 px-4 text-sm text-slate-700 whitespace-nowrap">
                  {col.render ? col.render(row) : (row as any)[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
