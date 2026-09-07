import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../api/client';

const COLORS = ['#2563eb', '#16a34a', '#d97706', '#9333ea', '#dc2626', '#0891b2', '#4f46e5'];

export default function DepartmentPieChart() {
  const [data, setData] = useState<{name: string, value: number}[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/maintenance').then((res: any) => {
      const tasks = res.data.data || [];
      const dist: Record<string, number> = {};
      tasks.forEach((t: any) => {
        const dept = t.department || 'Unknown';
        dist[dept] = (dist[dept] || 0) + 1;
      });
      // Sort by value descending
      const formatted = Object.keys(dist)
        .map(k => ({ name: k, value: dist[k] }))
        .sort((a, b) => b.value - a.value);
      setData(formatted);
      setLoading(false);
    }).catch(() => {
      setData([]);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="h-80 w-full bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-center"><div className="animate-pulse flex flex-col items-center"><div className="w-12 h-12 rounded-full border-4 border-slate-200 dark:border-slate-700 border-t-blue-500 animate-spin mb-3"></div><div className="text-slate-400 text-sm font-medium">Loading department data...</div></div></div>;
  
  if (data.length === 0) return <div className="h-80 w-full bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-center text-slate-400 font-medium">No department data available</div>;
  
  return (
    <div className="h-96 w-full bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-tight">Tasks by Department</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Distribution of pending maintenance tasks</p>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={2} dataKey="value" stroke="none">
              {data.map((_entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
            </Pie>
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              itemStyle={{ color: '#1e293b', fontWeight: 600 }}
            />
            <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', fontWeight: 500, color: '#64748b' }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
