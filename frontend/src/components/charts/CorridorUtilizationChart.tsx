import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import api from '../../api/client';

export default function CorridorUtilizationChart() {
  const [data, setData] = useState<{name: string, blocks: number}[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/blocks').then((res: any) => {
      const blocks = res.data.data || [];
      const corr: Record<string, number> = {};
      blocks.forEach((b: any) => {
        const cId = b.corridor_id || 'Unknown';
        corr[cId] = (corr[cId] || 0) + 1;
      });
      // Sort by block count descending
      const formatted = Object.keys(corr)
        .map(k => ({ name: k, blocks: corr[k] }))
        .sort((a, b) => b.blocks - a.blocks)
        .slice(0, 10); // Top 10 to avoid crowding
      setData(formatted);
      setLoading(false);
    }).catch(() => {
      setData([]);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="h-80 w-full bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-center"><div className="animate-pulse flex flex-col items-center"><div className="w-12 h-12 rounded-full border-4 border-slate-200 dark:border-slate-700 border-t-blue-500 animate-spin mb-3"></div><div className="text-slate-400 text-sm font-medium">Loading utilization data...</div></div></div>;
  
  if (data.length === 0) return <div className="h-80 w-full bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-center text-slate-400 font-medium">No corridor data available</div>;

  return (
    <div className="h-96 w-full bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-tight">Top Corridor Utilization</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Number of active blocks per sector</p>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
            <Tooltip 
              cursor={{ fill: '#f1f5f9' }}
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Bar dataKey="blocks" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index < 3 ? '#2563eb' : '#94a3b8'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
