import { useEffect, useMemo, useState } from 'react';
import api from '../api/client';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Activity, AlertTriangle, Bell, CheckCircle2, Clock3, ShieldAlert, Wrench, RefreshCw } from 'lucide-react';

type AlertItem = {
  id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'INFO';
  title: string;
  message: string;
  source: string;
  meta: string;
};

const severityOrder: Record<AlertItem['severity'], number> = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, INFO: 3 };

function severityClasses(severity: AlertItem['severity']) {
  if (severity === 'CRITICAL') return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-300';
  if (severity === 'HIGH') return 'border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-900/60 dark:bg-orange-950/30 dark:text-orange-300';
  if (severity === 'MEDIUM') return 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-300';
  return 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900/60 dark:bg-blue-950/30 dark:text-blue-300';
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAlerts = async () => {
    setLoading(true); setError('');
    try {
      const [tasksRes, defectsRes, blocksRes, assetsRes] = await Promise.all([
        api.get('/maintenance'), api.get('/defects'), api.get('/blocks'), api.get('/assets')
      ]);
      const tasks = tasksRes.data?.data || [];
      const defects = defectsRes.data?.data || [];
      const blocks = blocksRes.data?.data || [];
      const assets = assetsRes.data?.data || [];
      const next: AlertItem[] = [];

      tasks.filter((t: any) => String(t.status || '').toUpperCase() === 'OVERDUE').slice(0, 8).forEach((t: any) => {
        next.push({ id: `task-overdue-${t.task_id}`, severity: 'CRITICAL', title: 'Overdue maintenance task', message: `${t.task_id || 'Task'} requires immediate attention.`, source: t.department || 'Maintenance', meta: t.due_date || 'Due date passed' });
      });
      tasks.filter((t: any) => String(t.criticality || '').toUpperCase() === 'CRITICAL' && String(t.status || '').toUpperCase() !== 'COMPLETED').slice(0, 8).forEach((t: any) => {
        next.push({ id: `task-critical-${t.task_id}`, severity: 'HIGH', title: 'Critical maintenance pending', message: `${t.task_id || 'Task'} is marked critical and is not completed.`, source: t.department || 'Maintenance', meta: String(t.status || 'PENDING') });
      });
      defects.filter((d: any) => ['CRITICAL', 'HIGH'].includes(String(d.severity || d.priority || '').toUpperCase())).slice(0, 8).forEach((d: any) => {
        const sev = String(d.severity || d.priority || '').toUpperCase() === 'CRITICAL' ? 'CRITICAL' : 'HIGH';
        next.push({ id: `defect-${d.defect_id}`, severity: sev, title: 'High-priority asset defect', message: `${d.defect_id || 'Defect'} needs engineering review.`, source: d.asset_id || 'Asset inventory', meta: d.status || 'OPEN' });
      });
      blocks.filter((b: any) => String(b.status || '').toUpperCase() !== 'APPROVED').slice(0, 6).forEach((b: any) => {
        next.push({ id: `block-${b.block_id}`, severity: 'MEDIUM', title: 'Block requires review', message: `${b.block_id || 'Block'} is not currently approved.`, source: b.corridor_id || 'Block planning', meta: b.status || 'UNKNOWN' });
      });
      const unavailable = assets.filter((a: any) => String(a.availability_status || '').toUpperCase() !== 'AVAILABLE').length;
      if (unavailable > 0) next.push({ id: 'assets-unavailable', severity: unavailable > assets.length * 0.25 ? 'HIGH' : 'MEDIUM', title: 'Assets unavailable', message: `${unavailable} of ${assets.length} assets are not currently available.`, source: 'Asset inventory', meta: 'Availability watch' });
      if (next.length === 0) next.push({ id: 'healthy', severity: 'INFO', title: 'No active operational alerts', message: 'Current maintenance, defect and block data contains no generated alerts.', source: 'System monitor', meta: 'Healthy' });
      setAlerts(next.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]));
    } catch (e: any) {
      setError(e?.message || 'Unable to load alert data. Check that the backend is running.');
    } finally { setLoading(false); }
  };

  useEffect(() => { loadAlerts(); }, []);

  const counts = useMemo(() => ({
    critical: alerts.filter(a => a.severity === 'CRITICAL').length,
    high: alerts.filter(a => a.severity === 'HIGH').length,
    medium: alerts.filter(a => a.severity === 'MEDIUM').length,
    info: alerts.filter(a => a.severity === 'INFO').length,
  }), [alerts]);

  return <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div><h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2"><Bell className="text-blue-600" /> Alert Center</h1><p className="text-slate-500 dark:text-slate-400 mt-1">Operational warnings generated from live maintenance, defect, asset and block data.</p></div>
      <button onClick={loadAlerts} disabled={loading} className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 disabled:opacity-50"><RefreshCw className={loading ? 'w-4 h-4 animate-spin' : 'w-4 h-4'} /> Refresh</button>
    </div>
    {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-300">{error}</div>}
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {[[counts.critical, 'Critical', 'text-red-600', ShieldAlert], [counts.high, 'High', 'text-orange-600', AlertTriangle], [counts.medium, 'Medium', 'text-amber-600', Clock3], [counts.info, 'Info', 'text-blue-600', Activity]].map(([value, label, color, Icon]: any) => <div key={label} className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800"><div className="flex items-center justify-between"><span className="text-sm font-semibold text-slate-500 dark:text-slate-400">{label}</span><Icon className={`w-5 h-5 ${color}`} /></div><div className="text-3xl font-bold mt-2 text-slate-900 dark:text-slate-100">{value}</div></div>)}
    </div>
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
      {loading ? <div className="h-80 flex items-center justify-center"><LoadingSpinner /></div> : <div className="divide-y divide-slate-100 dark:divide-slate-800">{alerts.map(alert => <div key={alert.id} className="p-5 flex gap-4 items-start"><div className={`mt-0.5 p-2 rounded-lg border ${severityClasses(alert.severity)}`}>{alert.severity === 'CRITICAL' ? <ShieldAlert className="w-5 h-5" /> : alert.severity === 'HIGH' ? <AlertTriangle className="w-5 h-5" /> : alert.severity === 'MEDIUM' ? <Wrench className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><h3 className="font-bold text-slate-900 dark:text-slate-100">{alert.title}</h3><span className={`text-[10px] font-bold px-2 py-1 rounded-full border ${severityClasses(alert.severity)}`}>{alert.severity}</span></div><p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{alert.message}</p><div className="flex flex-wrap gap-x-5 gap-y-1 mt-3 text-xs text-slate-500 dark:text-slate-500"><span>Source: {alert.source}</span><span>{alert.meta}</span></div></div></div>)}</div>}
    </div>
  </div>;
}
