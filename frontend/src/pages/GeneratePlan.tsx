import { useState, useEffect } from 'react';
import { generatePlan } from '../api/planning';
import api from '../api/client';
import PlanComparisonCard from '../components/ui/PlanComparisonCard';
import PlanTimeline from '../components/ui/PlanTimeline';
import { CheckCircle2, XCircle, AlertTriangle, Play, CalendarDays, BrainCircuit } from 'lucide-react';

const LOADING_STEPS = [
  "Analyzing maintenance tasks...",
  "Applying railway constraints...",
  "Running AI prioritization models...",
  "Executing Google CP-SAT optimization...",
  "Validating constraint satisfaction..."
];

export default function GeneratePlan() {
  const [horizon, setHorizon] = useState('weekly');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [preContext, setPreContext] = useState<any>(null);

  useEffect(() => {
    Promise.all([
      api.get('/maintenance'), // Fetching all so we can accurately count overdue/critical without assuming API filters are exact
      api.get('/corridors')
    ]).then(([tasksRes, corridorsRes]) => {
      const allTasks = tasksRes.data.data || [];
      const pendingTasks = allTasks.filter((t: any) => t.status === 'PENDING' || t.status === 'OVERDUE');
      const criticalCount = pendingTasks.filter((t: any) => t.priority === 'CRITICAL').length;
      const overdueCount = pendingTasks.filter((t: any) => t.status === 'OVERDUE').length;
      const corridors = corridorsRes.data.data || [];
      const depts = new Set(pendingTasks.map((t: any) => t.department));
      setPreContext({
        taskCount: pendingTasks.length,
        criticalCount: criticalCount,
        overdueCount: overdueCount,
        depts: Array.from(depts).join(' / ') || 'None',
        corridorCount: corridors.length
      });
    }).catch(console.error);
  }, []);

  useEffect(() => {
    let interval: any;
    if (loading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep(prev => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
      }, 3000); // cycle messages
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await generatePlan(horizon);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Error generating plan from backend API.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in duration-500">
      
      {/* Header Card */}
      <div className="bg-white dark:bg-slate-900 p-8 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
              <BrainCircuit className="text-steel" /> Generate Optimized Schedule
            </h1>
            <p className="text-slate-500 dark:text-slate-400">
              Run the AI prioritization and Constraint Programming (CP-SAT) engine to schedule blocks automatically.
            </p>
          </div>
        </div>

        <div className="mt-8 flex flex-col md:flex-row items-center gap-6 bg-slate-50 dark:bg-slate-800 p-4 rounded-lg border border-slate-100">
          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 cursor-pointer p-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-blue-300 transition-colors">
              <input type="radio" value="weekly" checked={horizon === 'weekly'} onChange={() => setHorizon('weekly')} className="accent-blue-600 w-4 h-4" />
              <div className="flex flex-col">
                <span className="font-semibold text-slate-800 dark:text-slate-100 text-sm">Weekly Plan</span>
                <span className="text-xs text-slate-500 dark:text-slate-400">7-day optimization horizon</span>
              </div>
            </label>
            <label className="flex items-center gap-2 cursor-pointer p-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-blue-300 transition-colors">
              <input type="radio" value="monthly" checked={horizon === 'monthly'} onChange={() => setHorizon('monthly')} className="accent-blue-600 w-4 h-4" />
              <div className="flex flex-col">
                <span className="font-semibold text-slate-800 dark:text-slate-100 text-sm">Monthly Plan</span>
                <span className="text-xs text-slate-500 dark:text-slate-400">30-day capacity planning</span>
              </div>
            </label>
          </div>
          
          <div className="md:ml-auto">
            <button 
              onClick={handleGenerate} 
              disabled={loading}
              className="flex items-center gap-2 bg-steel hover:bg-steel-dark text-white px-8 py-3 rounded-lg font-semibold transition-all disabled:opacity-70 disabled:cursor-not-allowed shadow-sm"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Optimizing...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current" />
                  Run Optimizer
                </>
              )}
            </button>
          </div>
        </div>
        
        {error && (
          <div className="mt-6 flex items-center gap-3 text-signal-red bg-signal-red/10 p-4 rounded-lg border border-red-200">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <p className="font-medium">{error}</p>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 text-center animate-in zoom-in-95 duration-300">
          <div className="w-16 h-16 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin mx-auto mb-6"></div>
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2">Engine Running</h3>
          <p className="text-slate-500 dark:text-slate-400 font-medium animate-pulse">{LOADING_STEPS[loadingStep]}</p>
        </div>
      )}

      {/* Results State */}
      {result && !loading && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
          
          {/* Status banner */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm gap-4">
            <div className="flex items-center gap-3">
              {result.solver_status === 'OPTIMAL' || result.solver_status === 'FEASIBLE' ? (
                <div className="flex items-center gap-2 px-3 py-1 bg-signal-green/10 text-signal-green rounded-full border border-emerald-200 font-medium">
                  <CheckCircle2 className="w-4 h-4" /> Solver Status: {result.solver_status}
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-700 rounded-full border border-amber-200 font-medium">
                  <AlertTriangle className="w-4 h-4" /> Solver Status: {result.solver_status || 'UNKNOWN'}
                </div>
              )}
              {result.validation?.valid && (
                <div className="flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200 font-medium text-sm">
                  <CheckCircle2 className="w-4 h-4" /> Constraints Validated
                </div>
              )}
            </div>
            <div className="flex gap-3 text-sm text-slate-500 dark:text-slate-400 font-medium">
              <span className="flex items-center gap-1"><CalendarDays className="w-4 h-4" /> Plan ID: {result.plan?.plan_id || 'Auto-generated'}</span>
            </div>
          </div>

          {/* Metrics Comparison */}
          {result.comparison && <PlanComparisonCard comparison={result.comparison} />}

          {/* Timeline View */}
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="p-5 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
              <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">Corridor Coordination Timeline</h3>
            </div>
            <div className="p-4">
              <PlanTimeline blocks={result.blocks || []} horizon_days={horizon === 'weekly' ? 7 : 30} reference_start={result.plan?.generated_at} />
            </div>
          </div>

          {/* Two-column layout for Tasks */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Scheduled Tasks */}
            <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col h-[500px]">
              <div className="p-5 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 flex justify-between items-center shrink-0">
                <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">Scheduled Blocks</h3>
                <span className="bg-signal-green/20 text-emerald-800 text-xs font-bold px-2.5 py-1 rounded-full">
                  {result.scheduled_tasks?.length || 0} Tasks Assigned
                </span>
              </div>
              <div className="overflow-auto p-0">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-white dark:bg-slate-900 sticky top-0 shadow-sm">
                    <tr>
                      <th className="py-3 px-4 font-semibold text-slate-600 dark:text-slate-400">Task ID</th>
                      <th className="py-3 px-4 font-semibold text-slate-600 dark:text-slate-400">Corridor</th>
                      <th className="py-3 px-4 font-semibold text-slate-600 dark:text-slate-400">Time Window</th>
                      <th className="py-3 px-4 font-semibold text-slate-600 dark:text-slate-400">Duration</th>
                      <th className="py-3 px-4 font-semibold text-slate-600 dark:text-slate-400">Dept</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {result.scheduled_tasks?.map((t: any) => (
                      <tr id={`task-${t.task_id}`} key={t.task_id} className="hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                        <td className="py-3 px-4 font-mono text-xs text-steel font-medium">{t.task_id}</td>
                        <td className="py-3 px-4 font-medium text-slate-700 dark:text-slate-300">{t.corridor_id}</td>
                        <td className="py-3 px-4">
                          <div className="flex flex-col text-xs">
                            <span className="text-slate-800 dark:text-slate-100">{new Date(t.start_time).toLocaleString([], {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'})}</span>
                            <span className="text-slate-400">to {new Date(t.end_time).toLocaleString([], {hour:'2-digit', minute:'2-digit'})}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-slate-600 dark:text-slate-400 font-medium font-data">{typeof t.duration_hours === 'number' ? t.duration_hours.toFixed(1) + 'h' : '-'}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-1 bg-slate-100 text-slate-700 dark:text-slate-300 rounded text-xs font-medium">{t.department}</span>
                        </td>
                      </tr>
                    ))}
                    {!result.scheduled_tasks?.length && (
                      <tr><td colSpan={5} className="p-8 text-center text-slate-500 dark:text-slate-400">No tasks could be scheduled</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Unscheduled Tasks & Validation */}
            <div className="space-y-6 flex flex-col">
              
              {/* Unscheduled Tasks */}
              <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-orange-200 overflow-hidden flex-1 max-h-[250px] flex flex-col">
                <div className="p-4 border-b border-orange-100 bg-orange-50 flex justify-between items-center shrink-0">
                  <h3 className="font-bold text-orange-800">Unscheduled</h3>
                  <span className="bg-orange-200 text-orange-800 text-xs font-bold px-2 py-0.5 rounded-full">
                    {result.unscheduled_tasks?.length || 0}
                  </span>
                </div>
                <div className="p-4 overflow-auto">
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">Constraints or priority prevented scheduling.</p>
                  <div className="flex flex-wrap gap-1.5">
                    {result.unscheduled_tasks?.slice(0, 20).map((t: any) => (
                      <div key={t.task_id} className="flex items-center gap-2 w-full text-[10px] bg-orange-50 border border-orange-100 text-orange-700 px-2 py-1 rounded" title={t.reason}>
                        <span className="font-mono font-bold shrink-0">{t.task_id}</span>
                        <span className="truncate text-orange-600">{t.reason}</span>
                      </div>
                    ))}
                    {result.unscheduled_tasks?.length > 20 && (
                      <span className="text-xs text-slate-400 font-medium mt-1">+{result.unscheduled_tasks.length - 20} more</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Validation Result */}
              <div className={`bg-white dark:bg-slate-900 rounded-xl shadow-sm border overflow-hidden flex-1 max-h-[225px] flex flex-col ${result.validation?.valid ? 'border-emerald-200' : 'border-red-200'}`}>
                <div className={`p-4 border-b shrink-0 ${result.validation?.valid ? 'bg-signal-green/10 border-emerald-100' : 'bg-signal-red/10 border-red-100'}`}>
                  <h3 className={`font-bold ${result.validation?.valid ? 'text-emerald-800' : 'text-red-800'}`}>
                    Validation Checks
                  </h3>
                </div>
                <div className="p-4 overflow-auto">
                  {result.validation?.valid ? (
                    <div className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <CheckCircle2 className="w-5 h-5 text-signal-green shrink-0 mt-0.5" />
                      <p>All scheduled blocks successfully satisfy temporal and spatial railway constraints.</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-start gap-2 text-sm text-signal-red font-medium mb-2">
                        <XCircle className="w-5 h-5 shrink-0" />
                        <p>Violations Detected:</p>
                      </div>
                      <div className="bg-signal-red/10 text-red-800 text-xs font-mono p-2 rounded max-h-24 overflow-auto whitespace-pre-wrap">
                        {JSON.stringify(result.validation?.violations, null, 2)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
