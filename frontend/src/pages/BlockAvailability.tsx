import React from 'react';
import BlockGanttChart from '../components/charts/BlockGanttChart';
import { CalendarClock, ShieldCheck } from 'lucide-react';

export default function BlockAvailability() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      <div className="flex justify-between items-center bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <CalendarClock className="text-blue-600" /> Maintenance Block Schedule
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Authorized downtime windows and resource allocations.</p>
        </div>
        <div className="flex items-center gap-2 text-sm font-medium text-emerald-700 bg-emerald-50 px-4 py-2 rounded-lg border border-emerald-200">
          <ShieldCheck className="w-5 h-5" />
          CP-SAT Optimized
        </div>
      </div>
      
      <BlockGanttChart />
    </div>
  );
}
