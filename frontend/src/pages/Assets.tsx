import { useState, useEffect } from 'react';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Asset } from '../types';
import api from '../api/client';
import { Database, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

export default function Assets() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get('/assets').then((res: any) => {
      setAssets(res.data.data || []);
      setLoading(false);
    }).catch((err: any) => {
      setError(err.message || 'Failed to load assets');
      setLoading(false);
    });
  }, []);

  const columns = [
    { key: 'asset_id', header: 'Asset ID', render: (row: Asset) => <span className="font-mono text-blue-600 font-medium">{row.asset_id}</span> },
    { key: 'asset_type', header: 'Type', render: (row: Asset) => <span className="text-slate-700 dark:text-slate-300 font-medium">{row.asset_type}</span> },
    { key: 'location', header: 'Location' },
    { key: 'criticality', header: 'Criticality', render: (row: Asset) => <StatusBadge status={row.criticality} /> },
    { key: 'condition_score', header: 'Condition (Health)', render: (row: Asset) => (
      <div className="flex items-center gap-3">
        <div className="w-24 h-1.5 bg-slate-200 rounded-full overflow-hidden">
          <div 
            className={`h-full ${(row.condition_score || 0) > 70 ? 'bg-emerald-500' : (row.condition_score || 0) > 40 ? 'bg-amber-500' : 'bg-red-500'}`} 
            style={{ width: `${row.condition_score || 0}%` }} 
          />
        </div>
        <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{(row.condition_score || 0).toFixed(1)}</span>
      </div>
    )},
    { key: 'availability_status', header: 'Availability', render: (row: Asset) => <StatusBadge status={row.availability_status || 'Available'} /> }
  ];

  if (loading) return <div className="h-96 flex items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="p-6 text-red-600 bg-red-50 rounded-lg border border-red-100 flex items-center gap-3"><AlertTriangle className="w-5 h-5"/> {error}</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <Database className="text-blue-600" /> Infrastructure Asset Inventory
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Real-time status of all managed railway assets.</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex flex-col items-end">
            <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{assets.length}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium uppercase tracking-wider">Total Assets</div>
          </div>
          <div className="h-10 w-px bg-slate-200"></div>
          <div className="flex flex-col items-end">
            <div className="text-2xl font-bold text-emerald-600">
              {assets.filter(a => a.availability_status === 'Available').length}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium uppercase tracking-wider">Available</div>
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <DataTable data={assets} columns={columns} keyExtractor={(item) => item.asset_id} />
      </div>
    </div>
  );
}
