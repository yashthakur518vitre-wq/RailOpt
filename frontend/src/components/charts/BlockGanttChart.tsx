import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid, Cell } from 'recharts';
import api from '../../api/client';
import LoadingSpinner from '../ui/LoadingSpinner';

export default function BlockGanttChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/blocks').then((res: any) => {
      const blocks = res.data.data || [];
      const formatted = blocks.map((b: any) => ({
        corridor: b.corridor_id,
        duration: typeof b.duration === 'number' ? Number(b.duration.toFixed(2)) : 0,
        department: b.department,
        status: b.status,
        start_time: new Date(b.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
        id: b.block_id
      })).sort((a: any, b: any) => b.duration - a.duration);
      setData(formatted);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-96 w-full flex items-center justify-center bg-white border border-slate-200 rounded-xl shadow-sm"><LoadingSpinner /></div>;
  if (data.length === 0) return <div className="h-96 w-full bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center justify-center text-slate-400 font-medium">No active blocks scheduled</div>;

  return (
    <div className="h-[500px] w-full bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h3 className="text-lg font-bold text-slate-900 tracking-tight">System Block Availability</h3>
          <p className="text-sm text-slate-500 font-medium">Approved durations for maintenance across corridors</p>
        </div>
        <div className="flex gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-blue-600"></div> Engineering</div>
          <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-indigo-500"></div> S&T</div>
          <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-emerald-500"></div> Traction</div>
          <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-slate-400"></div> Other</div>
        </div>
      </div>
      
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart layout="vertical" data={data} margin={{ top: 0, right: 30, left: 30, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={true} stroke="#f1f5f9" />
            <XAxis type="number" unit=" hrs" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <YAxis dataKey="corridor" type="category" tick={{ fontSize: 11, fill: '#475569', fontWeight: 600 }} axisLine={false} tickLine={false} />
            <Tooltip 
              cursor={{ fill: '#f8fafc' }}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              formatter={(val: number) => [`${val} hours`, 'Duration']}
              labelFormatter={(label) => `Corridor: ${label}`}
              labelStyle={{ fontWeight: 600, color: '#1e293b', marginBottom: '4px' }}
            />
            <Bar dataKey="duration" radius={[0, 4, 4, 0]} maxBarSize={30}>
              {data.map((entry, index) => {
                let color = '#94a3b8';
                if (entry.department === 'Engineering') color = '#2563eb';
                if (entry.department === 'S&T') color = '#6366f1';
                if (entry.department === 'Traction') color = '#10b981';
                return <Cell key={`cell-${index}`} fill={color} />;
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
