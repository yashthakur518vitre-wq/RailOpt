import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';
import api from '../api/client';
import { Train } from '../types';
import { Train as TrainIcon, Clock, Users, ArrowRight, ShieldAlert, Route as RouteIcon, Plus, X } from 'lucide-react';

export default function Trains() {
  const [trains, setTrains] = useState<Train[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    train_number: '12345',
    train_type: 'Express',
    origin: 'Station A',
    destination: 'Station B',
    corridor_id: 'COR-001',
    arrival_time: '12:00',
    departure_time: '12:15',
    priority: 'High',
    occupancy: 75
  });

  const [error, setError] = useState<string | null>(null);
  
  const loadTrains = () => {
    setLoading(true);
    api.get('/trains').then((res: any) => {
      setTrains(res.data?.data || []);
      setLoading(false);
    }).catch((err) => {
      setError(err.message || "Failed to load trains");
      setLoading(false);
    });
  };

  useEffect(() => {
    loadTrains();
  }, []);

  const handleCreateTrain = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const newTrain = {
      train_id: `TRN-N${Math.floor(Math.random() * 10000)}`,
      train_number: formData.train_number,
      train_type: formData.train_type,
      origin: formData.origin,
      destination: formData.destination,
      corridor_id: formData.corridor_id,
      arrival_time: formData.arrival_time,
      departure_time: formData.departure_time,
      frequency: 'Daily',
      priority: formData.priority,
      occupancy: Number(formData.occupancy),
      forecasted: false
    };

    try {
      await api.post('/trains', newTrain);
      setIsModalOpen(false);
      loadTrains();
    } catch (err: any) {
      alert("Failed to create train: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toUpperCase()) {
      case 'CRITICAL': return 'bg-red-100 text-red-700 border-red-200';
      case 'HIGH': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'LOW': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-slate-100 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700';
    }
  };

  const filteredTrains = filterType === 'All' 
    ? trains 
    : trains.filter(t => t.train_type === filterType);

  if (loading && trains.length === 0) return <div className="h-96 flex items-center justify-center"><LoadingSpinner /></div>;
  if (trains.length === 0) return <EmptyState message="No train data available" />;

  return (
    <div className="space-y-6 relative">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Train Operations</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Representative SIH Demo Data (Synthetic COA Integration)</p>
        </div>
        <div className="flex items-center gap-4">
          <select 
            className="border-slate-300 rounded-md text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="All">All Types</option>
            <option value="Rajdhani">Rajdhani</option>
            <option value="Shatabdi">Shatabdi</option>
            <option value="Express">Express</option>
            <option value="Passenger">Passenger</option>
            <option value="Goods">Goods (Freight)</option>
            <option value="Suburban">Suburban</option>
          </select>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-sm transition-colors"
          >
            <Plus className="w-4 h-4" /> Add Train
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-medium">
              <tr>
                <th className="px-6 py-4">Train ID / No.</th>
                <th className="px-6 py-4">Type & Priority</th>
                <th className="px-6 py-4">Route</th>
                <th className="px-6 py-4">Schedule</th>
                <th className="px-6 py-4">Corridor ID</th>
                <th className="px-6 py-4">Occupancy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredTrains.map(t => (
                <tr key={t.train_id} className="hover:bg-slate-50 dark:bg-slate-800 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                        <TrainIcon size={16} />
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900 dark:text-slate-100">{t.train_id}</div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 font-mono">{t.train_number}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1.5 items-start">
                      <span className="font-medium text-slate-700 dark:text-slate-300">{t.train_type}</span>
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${getPriorityColor(t.priority)}`}>
                        {t.priority}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                      <span className="truncate max-w-[100px]" title={t.origin}>{t.origin}</span>
                      <ArrowRight size={14} className="text-slate-400 shrink-0" />
                      <span className="truncate max-w-[100px]" title={t.destination}>{t.destination}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1 text-slate-600 dark:text-slate-400">
                      <div className="flex items-center gap-1.5">
                        <Clock size={14} className="text-emerald-500" />
                        <span>Dep: {t.departure_time}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Clock size={14} className="text-blue-500" />
                        <span>Arr: {t.arrival_time}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                      <RouteIcon size={14} className="text-slate-400" />
                      <span className="font-mono text-xs">{t.corridor_id}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Users size={16} className={t.occupancy > 80 ? 'text-red-500' : 'text-slate-400'} />
                      <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${t.occupancy > 80 ? 'bg-red-500' : t.occupancy > 60 ? 'bg-yellow-500' : 'bg-emerald-500'}`}
                          style={{ width: `${Math.min(100, Math.max(0, t.occupancy))}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-slate-600 dark:text-slate-400 w-8">{Math.round(t.occupancy)}%</span>
                    </div>
                    {t.forecasted && (
                      <div className="flex items-center gap-1 mt-1.5 text-xs text-orange-600 font-medium">
                        <ShieldAlert size={12} />
                        <span>Forecasted Goods</span>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-2xl w-full p-6 animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Add Train</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600 dark:text-slate-400">
                <X className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleCreateTrain} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Train Number</label>
                  <input type="text" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.train_number} onChange={e => setFormData({...formData, train_number: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Train Type</label>
                  <select className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.train_type} onChange={e => setFormData({...formData, train_type: e.target.value})}>
                    <option>Rajdhani</option>
                    <option>Shatabdi</option>
                    <option>Express</option>
                    <option>Passenger</option>
                    <option>Goods</option>
                    <option>Suburban</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Origin</label>
                  <input type="text" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.origin} onChange={e => setFormData({...formData, origin: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Destination</label>
                  <input type="text" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.destination} onChange={e => setFormData({...formData, destination: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Corridor ID</label>
                  <input type="text" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.corridor_id} onChange={e => setFormData({...formData, corridor_id: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Priority</label>
                  <select className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.priority} onChange={e => setFormData({...formData, priority: e.target.value})}>
                    <option>Critical</option>
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Departure Time</label>
                  <input type="time" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.departure_time} onChange={e => setFormData({...formData, departure_time: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Arrival Time</label>
                  <input type="time" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.arrival_time} onChange={e => setFormData({...formData, arrival_time: e.target.value})} />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-300 rounded-md hover:bg-slate-50 dark:bg-slate-800 font-medium">Cancel</button>
                <button type="submit" disabled={submitting} className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 font-medium disabled:opacity-50 flex items-center gap-2">
                  {submitting && <LoadingSpinner />}
                  Add Train
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
