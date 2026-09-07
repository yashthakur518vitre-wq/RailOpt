import { PlanComparison } from '../../types';

export default function PlanComparisonCard({ comparison }: { comparison: PlanComparison }) {
  if (!comparison) return null;

  const metrics = Object.entries(comparison).map(([key, val]: [string, any]) => ({
    label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    optimized: val?.optimized ?? 0,
    baseline: val?.baseline ?? 0,
    improvement: val?.improvement ?? 0,
  }));

  return (
    <div className="bg-white dark:bg-ink-panel border border-slate-200 dark:border-ink-track rounded-panel overflow-hidden">
      <div className="p-5 border-b border-slate-200 dark:border-ink-track bg-slate-50 dark:bg-ink flex justify-between items-center">
        <div>
          <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">Plan Comparison</h3>
          <p className="text-xs text-slate-500">AI Optimized vs. Baseline Heuristic</p>
        </div>
      </div>
      <div className="p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map(m => {
            const isBetter = m.improvement > 0;
            const isNeutral = m.improvement === 0;
            
            return (
              <div key={m.label} className="p-4 bg-white dark:bg-ink rounded-lg border border-slate-100 dark:border-slate-800 shadow-sm transition-all">
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">{m.label}</div>
                {m.label === 'Estimated Availability Proxy' && (
                  <div className="text-[10px] text-slate-400 mb-2 leading-tight">Proxy metric based on task completion ratio — not a direct downtime measurement.</div>
                )}
                {! (m.label === 'Estimated Availability Proxy') && <div className="mb-3"></div>}
                
                <div className="flex justify-between items-end mb-3">
                  <div>
                    <div className="text-[10px] text-slate-400 font-semibold uppercase mb-0.5">Baseline</div>
                    <div className="text-xl font-medium text-slate-600 dark:text-slate-400 line-through opacity-70 font-data">
                      {typeof m.baseline === 'number' ? (m.baseline % 1 === 0 ? m.baseline : m.baseline.toFixed(1)) : m.baseline}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-steel font-bold uppercase mb-0.5">Optimized</div>
                    <div className="text-2xl font-bold text-steel font-data">
                      {typeof m.optimized === 'number' ? (m.optimized % 1 === 0 ? m.optimized : m.optimized.toFixed(1)) : m.optimized}
                    </div>
                  </div>
                </div>
                
                <div className={`mt-2 text-xs font-bold px-2 py-1.5 rounded-md inline-block w-full text-center border font-data
                  ${isBetter ? 'bg-signal-green/10 text-signal-green border-signal-green/20' : 
                    isNeutral ? 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700' : 
                    'bg-signal-red/10 text-signal-red border-signal-red/20'}`}
                >
                  {m.improvement > 0 ? '+' : ''}{typeof m.improvement === 'number' ? m.improvement.toFixed(1) : m.improvement}% 
                  <span className="opacity-75 font-sans font-medium ml-1">{isBetter ? 'better' : isNeutral ? 'change' : 'worse'}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
