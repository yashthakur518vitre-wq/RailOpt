import { useEffect, useState } from 'react';
import api from '../api/client';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { BarChart3, Download, RefreshCw, Database, Wrench, TrainFront, Boxes, ShieldCheck } from 'lucide-react';

function downloadCsv(filename: string, rows: Record<string, any>[]) {
  if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const csv = [headers.join(','), ...rows.map(row => headers.map(h => JSON.stringify(row[h] ?? '')).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
}

export default function Reports() {
  const [data, setData] = useState<any>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  const load = async () => { setLoading(true); setError(''); try { const [dash, avail, maint, impact, dept] = await Promise.all([api.get('/dashboard/summary'), api.get('/analytics/asset-availability'), api.get('/analytics/maintenance-completion'), api.get('/analytics/train-impact'), api.get('/analytics/department-performance')]); setData({ dash: dash.data?.data || {}, avail: avail.data?.data || {}, maint: maint.data?.data || {}, impact: impact.data?.data || {}, dept: dept.data?.data || {} }); } catch (e: any) { setError(e?.message || 'Unable to load analytics.'); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);
  if (loading && !data) return <div className="h-96 flex items-center justify-center"><LoadingSpinner /></div>;
  const d = data || { dash: {}, avail: {}, maint: {}, impact: {}, dept: {} }; const k = d.dash.kpis || {};
  const deptRows = Object.entries(d.dept).map(([name, value]: any) => ({ department: name, completion: value.completion ?? 0, efficiency: value.efficiency ?? 0 }));
  const corridorRows = Object.entries(d.impact.by_corridor || {}).map(([corridor, score]) => ({ corridor, impact_score: score }));
  const cards = [
    ['Asset Availability', `${Number(d.avail.overall_percentage || 0).toFixed(1)}%`, 'Current available assets', ShieldCheck, 'text-emerald-600'],
    ['Maintenance Completion', `${Number(d.maint.completion_percentage || 0).toFixed(1)}%`, `${d.maint.overdue_count || 0} overdue`, Wrench, 'text-blue-600'],
    ['Train Impact Score', `${Number(d.impact.overall_score || 0).toFixed(1)}`, 'Lower is better', TrainFront, 'text-orange-600'],
    ['Active Blocks', `${k['Number of Blocks'] ?? d.dash.active_blocks?.length ?? 0}`, 'From operational database', Boxes, 'text-purple-600'],
  ];
  return <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row md:items-center md:justify-between gap-4"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2"><BarChart3 className="text-blue-600" /> Reports & Analytics</h1><p className="text-slate-500 dark:text-slate-400 mt-1">Live operational metrics calculated from the RAILBlock database.</p></div><div className="flex gap-2"><button onClick={load} className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-sm font-semibold text-slate-700 dark:text-slate-200"><RefreshCw className="w-4 h-4" /> Refresh</button><button onClick={() => downloadCsv('railblock-department-report.csv', deptRows)} className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700"><Download className="w-4 h-4" /> Export CSV</button></div></div>
    {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">{cards.map(([title, value, sub, Icon, color]: any) => <div key={title} className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800"><div className="flex justify-between"><div><p className="text-sm font-semibold text-slate-500 dark:text-slate-400">{title}</p><p className="text-3xl font-bold text-slate-900 dark:text-slate-100 mt-2">{value}</p></div><Icon className={`w-6 h-6 ${color}`} /></div><p className="text-xs text-slate-500 mt-2">{sub}</p></div>)}</div>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6"><div className="flex items-center gap-2 mb-5"><Wrench className="w-5 h-5 text-blue-600" /><h2 className="font-bold text-lg text-slate-900 dark:text-slate-100">Department Performance</h2></div>{deptRows.length ? <div className="space-y-4">{deptRows.map(r => <div key={r.department}><div className="flex justify-between text-sm mb-1"><span className="font-semibold text-slate-700 dark:text-slate-300">{r.department}</span><span className="text-slate-500">{r.completion}% completion</span></div><div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-blue-600 rounded-full" style={{ width: `${Math.min(100, Math.max(0, r.completion))}%` }} /></div><div className="text-xs text-slate-500 mt-1">Efficiency: {r.efficiency}%</div></div>)}</div> : <p className="text-slate-400">No department data available.</p>}</section>
      <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6"><div className="flex items-center gap-2 mb-5"><TrainFront className="w-5 h-5 text-orange-600" /><h2 className="font-bold text-lg text-slate-900 dark:text-slate-100">Train Impact by Corridor</h2></div>{corridorRows.length ? <div className="space-y-3">{corridorRows.sort((a,b) => Number(b.impact_score)-Number(a.impact_score)).slice(0,10).map(r => <div key={r.corridor} className="grid grid-cols-[100px_1fr_55px] gap-3 items-center"><span className="font-mono text-xs text-slate-600 dark:text-slate-400 truncate">{r.corridor}</span><div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-orange-500 rounded-full" style={{ width: `${Math.min(100, Number(r.impact_score))}%` }} /></div><span className="text-xs font-semibold text-right text-slate-700 dark:text-slate-300">{Number(r.impact_score).toFixed(1)}</span></div>)}</div> : <p className="text-slate-400">No corridor impact data available.</p>}</section>
    </div>
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6"><div className="flex items-center gap-2 mb-4"><Database className="w-5 h-5 text-slate-600" /><h2 className="font-bold text-lg text-slate-900 dark:text-slate-100">Report Data Snapshot</h2></div><div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center">{[['Assets', d.dash.kpis?.['Total Assets'] ?? '—'], ['Tasks', d.dash.kpis?.['Total Maintenance Tasks'] ?? '—'], ['Blocks', d.dash.kpis?.['Number of Blocks'] ?? '—'], ['Trains', d.dash.kpis?.['Total Trains'] ?? '—'], ['Overdue', d.maint.overdue_count ?? '—']].map(([a,b]) => <div key={a} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg"><div className="text-2xl font-bold text-slate-900 dark:text-slate-100">{b}</div><div className="text-xs font-semibold text-slate-500 mt-1">{a}</div></div>)}</div></div>
  </div>;
}
