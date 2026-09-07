import { useApi } from '../hooks/useApi';
import { getDashboardSummary } from '../api/analytics';
import DepartmentPieChart from '../components/charts/DepartmentPieChart';
import CorridorUtilizationChart from '../components/charts/CorridorUtilizationChart';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Activity, Wrench, AlertTriangle, PlayCircle, BarChart2, Clock } from 'lucide-react';

export default function Dashboard() {
  const { data: summary, loading, error } = useApi(getDashboardSummary);

  if (loading) return <div className="h-full flex items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="p-8 text-center text-signal-red bg-signal-red/10 rounded-panel">Failed to load dashboard data: {error as string}</div>;
  if (!summary) return <div className="p-6 text-slate-500">No dashboard data available</div>;

  const primaryStats = [
    { label: 'Asset Availability', value: `${(summary.assetAvailability * 100).toFixed(1)}%`, icon: Activity, color: 'text-signal-green', bg: 'bg-signal-green/10', border: 'border-signal-green/20', subtitle: 'System-wide health' },
    { label: 'Train Impact Score', value: summary.trainImpact.toFixed(1), icon: BarChart2, color: 'text-signal-red', bg: 'bg-signal-red/10', border: 'border-signal-red/20', subtitle: 'Lower is better' },
  ];
  const secondaryStats = [
    { label: 'Maintenance Completion', value: `${(summary.maintenanceCompletion * 100).toFixed(1)}%`, icon: Wrench, color: 'text-steel', bg: 'bg-steel/10', border: 'border-ink-track', subtitle: 'Tasks resolved this cycle' },
    { label: 'Critical Task Completion', value: `${Number(summary.criticalTasks).toFixed(1)}%`, icon: AlertTriangle, color: 'text-signal-amber', bg: 'bg-signal-amber/10', border: 'border-ink-track', subtitle: 'High safety impact' },
    { label: 'Active Blocks', value: summary.activeBlocks, icon: PlayCircle, color: 'text-steel', bg: 'bg-steel/10', border: 'border-ink-track', subtitle: 'Current windows' },
    { label: 'Overdue Tasks', value: summary.overdueTasks, icon: Clock, color: 'text-signal-amber', bg: 'bg-signal-amber/10', border: 'border-ink-track', subtitle: 'Requires immediate action' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto">
      {/* Control Room Summary Strip */}
      <div className="bg-ink rounded-panel p-6 border border-ink-track text-white shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="text-steel-light w-6 h-6" />
          <h1 className="text-xl font-bold tracking-tight">RailBlock AI Operations Center</h1>
        </div>
        
        {/* Primary Load-Bearing Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {primaryStats.map((stat, i) => (
            <div key={i} className={`bg-ink-panel p-5 rounded-lg border ${stat.border} flex items-center justify-between`}>
              <div>
                <div className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-1">{stat.label}</div>
                <div className={`text-4xl font-bold font-data ${stat.color}`}>{stat.value}</div>
                <div className="text-xs text-slate-500 mt-2">{stat.subtitle}</div>
              </div>
              <div className={`p-4 rounded-full ${stat.bg}`}>
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
              </div>
            </div>
          ))}
        </div>

        {/* Secondary Operational Counts */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {secondaryStats.map((stat, i) => (
            <div key={i} className={`bg-ink-panel p-4 rounded-lg border ${stat.border} flex flex-col justify-between`}>
              <div className="flex justify-between items-start mb-2">
                <div className={`p-1.5 rounded-md ${stat.bg}`}>
                  <stat.icon className={`w-4 h-4 ${stat.color}`} />
                </div>
              </div>
              <div>
                <div className="text-xl font-bold text-slate-200 font-data tracking-tight mb-1">{stat.value}</div>
                <div className="text-xs font-semibold text-slate-400">{stat.label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DepartmentPieChart />
        <CorridorUtilizationChart />
      </div>

      {/* Operations Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alerts / Recent Tasks */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
          <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-tight mb-4 flex items-center justify-between">
            <span>Recent Maintenance Alerts</span>
            <span className="text-xs bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 px-2 py-1 rounded-full font-bold">
              {summary.rawCriticalTasks?.length || 0} New
            </span>
          </h3>
          <div className="space-y-3">
            {summary.rawCriticalTasks?.length ? (
              summary.rawCriticalTasks.map((task: any, i: number) => (
                <div key={i} className="flex gap-3 items-start p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-700/50">
                  <AlertTriangle className={`w-5 h-5 mt-0.5 shrink-0 ${task.criticality === 'CRITICAL' || task.criticality === 'HIGH' ? 'text-red-500' : 'text-amber-500'}`} />
                  <div>
                    <div className="text-sm font-bold text-slate-800 dark:text-slate-200">{task.task_name || 'Maintenance Task'}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-1">{task.description || `Asset ID: ${task.asset_id}`}</div>
                    <div className="text-xs text-slate-400 mt-1">{new Date(task.created_date || Date.now()).toLocaleString()}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-slate-500 text-sm text-center py-4">No recent alerts.</div>
            )}
          </div>
        </div>

        {/* Active Blocks */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
          <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-tight mb-4 flex items-center justify-between">
            <span>Active Operational Blocks</span>
            <span className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 px-2 py-1 rounded-full font-bold">
              {summary.rawActiveBlocks?.length || 0} Active
            </span>
          </h3>
          <div className="space-y-3">
            {summary.rawActiveBlocks?.length ? (
              summary.rawActiveBlocks.map((block: any, i: number) => (
                <div key={i} className="flex gap-3 items-start p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-700/50">
                  <PlayCircle className="w-5 h-5 mt-0.5 shrink-0 text-blue-500" />
                  <div className="w-full">
                    <div className="flex justify-between items-center">
                      <div className="text-sm font-bold text-slate-800 dark:text-slate-200">Block {block.block_id || block.id}</div>
                      <div className="text-xs font-bold text-emerald-600 dark:text-emerald-400">{block.status}</div>
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">Corridor: {block.corridor_id} | Dept: {block.department}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-slate-500 text-sm text-center py-4">No active blocks.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
