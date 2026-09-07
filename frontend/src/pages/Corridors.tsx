import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';
import { Corridor } from '../types';
import api from '../api/client';
import { Route as RouteIcon, TrendingUp, Clock, Train as TrainIcon, Calendar } from 'lucide-react';

export default function Corridors() {
  const [corridors, setCorridors] = useState<Corridor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>({});

  useEffect(() => {
    Promise.all([
      api.get('/corridors'),
      api.get('/trains'),
      api.get('/blocks')
    ]).then(([corRes, trainRes, blockRes]: any[]) => {
      const c = corRes.data?.data || [];
      const t = trainRes.data?.data || [];
      const b = blockRes.data?.data || [];
      
      const s: any = {};
      c.forEach((cor: any) => {
        s[cor.corridor_id] = {
          trains: t.filter((tr: any) => tr.corridor_id === cor.corridor_id).length,
          blocks: b.filter((blk: any) => blk.corridor_id === cor.corridor_id).length
        };
      });
      
      setCorridors(c);
      setStats(s);
      setLoading(false);
    }).catch((err) => {
      setError(err.message || "Failed to load corridors");
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="h-96 flex items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="p-8 text-center text-signal-red bg-signal-red/10 rounded-panel">{error}</div>;
  if (corridors.length === 0) return <EmptyState message="No corridors found" />;

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
          <RouteIcon className="text-blue-600" /> Corridor Network
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Railway network segments linking Trains, Assets, and Maintenance Blocks.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {corridors.map(c => (
          <div key={c.corridor_id} className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
                    <RouteIcon size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 tracking-tight">{c.name}</h3>
                    <span className="text-xs font-mono text-slate-500 dark:text-slate-400 bg-slate-100 px-2 py-0.5 rounded">{c.corridor_id}</span>
                  </div>
                </div>
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 font-medium mb-4 pb-4 border-b border-slate-100">
                {c.start_station} <span className="text-slate-400 mx-1">→</span> {c.end_station}
              </div>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400 flex items-center gap-2"><TrendingUp size={14} /> Distance</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">{c.distance_km} km</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400 flex items-center gap-2"><RouteIcon size={14} /> Type</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">{c.route_type}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400 flex items-center gap-2"><Clock size={14} /> Capacity</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">{c.capacity} trains/day</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
              <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-lg flex flex-col items-center justify-center border border-slate-100">
                <TrainIcon className="text-indigo-500 mb-1" size={16} />
                <span className="text-xl font-bold text-slate-800 dark:text-slate-100">{stats[c.corridor_id]?.trains || 0}</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">Trains</span>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-lg flex flex-col items-center justify-center border border-slate-100">
                <Calendar className="text-rose-500 mb-1" size={16} />
                <span className="text-xl font-bold text-slate-800 dark:text-slate-100">{stats[c.corridor_id]?.blocks || 0}</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">Active Blocks</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
