import React from 'react';
import clsx from 'clsx';

interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  let colorClass = 'bg-slate-100 text-slate-800';
  const s = status.toUpperCase();
  if (s === 'CRITICAL') colorClass = 'bg-red-100 text-red-800';
  else if (s === 'HIGH') colorClass = 'bg-orange-100 text-orange-800';
  else if (s === 'MEDIUM') colorClass = 'bg-yellow-100 text-yellow-800';
  else if (s === 'LOW' || s === 'SCHEDULED') colorClass = 'bg-green-100 text-green-800';

  return (
    <span className={clsx('px-2.5 py-0.5 rounded-full text-xs font-medium', colorClass)}>
      {status}
    </span>
  );
}
