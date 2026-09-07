import { useState, useEffect } from 'react';
import api from '../api/client';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Search, Clock, MapPin, ArrowRight, Filter } from 'lucide-react';

interface TrainSchedule {
  id: number;
  train_id: string;
  train_number: string;
  train_type: string;
  origin: string;
  destination: string;
  corridor_id: string;
  arrival_time: string;
  departure_time: string;
  frequency: string;
  priority: string;
  occupancy: number;
  forecasted: boolean;
}

const priorityColor = (p: string) => {
  switch (p?.toUpperCase()) {
    case 'CRITICAL': return 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800/50';
    case 'HIGH': return 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800/50';
    case 'MEDIUM': return 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800/50';
    case 'LOW': return 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700';
    default: return 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700';
  }
};

const typeColor = (t: string) => {
  switch (t) {
    case 'Rajdhani': return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400';
    case 'Shatabdi': return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400';
    case 'Express': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
    case 'Suburban': return 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400';
    case 'Passenger': return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400';
    case 'Goods': return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400';
    default: return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400';
  }
};

export default function Schedules() {
  const [trains, setTrains] = useState<TrainSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [corridorFilter, setCorridorFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');

  useEffect(() => {
    api.get('/trains')
      .then((res: any) => {
        setTrains(res.data.data || []);
        setLoading(false);
      })
      .catch((err: any) => {
        setError(err?.message || 'Failed to load schedule data');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="h-full flex items-center justify-center"><LoadingSpinner /></div>;
  if (error) return (
    <div className="p-6 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-800/50">
      Failed to load schedule data: {error}
    </div>
  );

  const types = Array.from(new Set(trains.map(t => t.train_type))).sort();
  const corridors = Array.from(new Set(trains.map(t => t.corridor_id))).sort();
  const priorities = Array.from(new Set(trains.map(t => t.priority))).sort();

  const filtered = trains.filter(t => {
    const q = search.toLowerCase();
    const matchesSearch = !q ||
      t.train_id.toLowerCase().includes(q) ||
      t.train_number.toLowerCase().includes(q) ||
      t.origin.toLowerCase().includes(q) ||
      t.destination.toLowerCase().includes(q) ||
      t.corridor_id.toLowerCase().includes(q);
    const matchesType = typeFilter === 'All' || t.train_type === typeFilter;
    const matchesCorridor = corridorFilter === 'All' || t.corridor_id === corridorFilter;
    const matchesPriority = priorityFilter === 'All' || t.priority === priorityFilter;
    return matchesSearch && matchesType && matchesCorridor && matchesPriority;
  });

  // Sort by departure time
  const sorted = [...filtered].sort((a, b) => a.departure_time.localeCompare(b.departure_time));

  // Summary stats
  const totalTrains = trains.length;
  const typeCounts: Record<string, number> = {};
  trains.forEach(t => { typeCounts[t.train_type] = (typeCounts[t.train_type] || 0) + 1; });

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Train Schedules</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Departure and arrival timetable derived from operational train data.</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-4 text-center">
          <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">{totalTrains}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">Total Trains</div>
        </div>
        {Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([type, count]) => (
          <div key={type} className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-4 text-center">
            <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">{count}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">{type}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-4">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search by train, route, or corridor..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
              className="border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="All">All Types</option>
              {types.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <select value={corridorFilter} onChange={(e) => setCorridorFilter(e.target.value)}
              className="border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="All">All Corridors</option>
              {corridors.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}
              className="border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="All">All Priorities</option>
              {priorities.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">
            {sorted.length} of {totalTrains} trains
          </div>
        </div>
      </div>

      {/* Schedule Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
        {sorted.length === 0 ? (
          <div className="p-12 text-center text-slate-400 dark:text-slate-500">
            <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-lg font-medium">No schedules match your filters</p>
            <p className="text-sm mt-1">Try adjusting your search or filter criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-medium">
                <tr>
                  <th className="text-left px-4 py-3">Train</th>
                  <th className="text-left px-4 py-3">Type</th>
                  <th className="text-left px-4 py-3">Route</th>
                  <th className="text-left px-4 py-3">Departure</th>
                  <th className="text-left px-4 py-3">Arrival</th>
                  <th className="text-left px-4 py-3">Corridor</th>
                  <th className="text-left px-4 py-3">Priority</th>
                  <th className="text-left px-4 py-3">Occupancy</th>
                  <th className="text-left px-4 py-3">Frequency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {sorted.map((t) => (
                  <tr key={t.train_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-semibold text-slate-900 dark:text-slate-100">{t.train_id}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">#{t.train_number}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-bold ${typeColor(t.train_type)}`}>
                        {t.train_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                        <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="font-medium">{t.origin}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="font-medium">{t.destination}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5 font-mono text-slate-800 dark:text-slate-200 font-semibold">
                        <Clock className="w-3.5 h-3.5 text-blue-500" />
                        {t.departure_time}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5 font-mono text-slate-800 dark:text-slate-200 font-semibold">
                        <Clock className="w-3.5 h-3.5 text-emerald-500" />
                        {t.arrival_time}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-bold text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                        {t.corridor_id}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-bold border ${priorityColor(t.priority)}`}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${t.occupancy > 85 ? 'bg-red-500' : t.occupancy > 60 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                            style={{ width: `${Math.min(100, t.occupancy)}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-slate-600 dark:text-slate-400">{t.occupancy.toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs font-medium">
                      {t.frequency}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
