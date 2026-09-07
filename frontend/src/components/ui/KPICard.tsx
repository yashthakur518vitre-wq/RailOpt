import React from 'react';
import { LucideIcon } from 'lucide-react';
import clsx from 'clsx';

interface KPICardProps {
  title: string;
  value: string | number;
  trend?: string;
  icon: LucideIcon;
  status?: 'success' | 'warning' | 'danger' | 'neutral';
}

export default function KPICard({ title, value, trend, icon: Icon, status = 'neutral' }: KPICardProps) {
  const statusColors = {
    success: 'text-signal-green',
    warning: 'text-signal-amber',
    danger: 'text-signal-red',
    neutral: 'text-slate-500'
  };

  return (
    <div className="bg-white p-6 rounded-panel shadow-sm border border-slate-200 flex items-center justify-between">
      <div>
        <h3 className="text-sm font-medium text-slate-500">{title}</h3>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold text-slate-900 font-data">{value}</span>
          {trend && (
            <span className={clsx('text-sm font-medium font-data', trend.startsWith('+') ? 'text-signal-green' : 'text-signal-red')}>
              {trend}
            </span>
          )}
        </div>
      </div>
      <div className={clsx('p-3 rounded-full bg-slate-50', statusColors[status])}>
        <Icon size={24} />
      </div>
    </div>
  );
}
