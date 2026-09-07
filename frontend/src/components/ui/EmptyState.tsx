import React from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  message?: string;
}

export default function EmptyState({ message = "No data available" }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-slate-500 bg-white rounded-lg border border-slate-200">
      <Inbox size={48} className="mb-4 text-slate-300" />
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
}
