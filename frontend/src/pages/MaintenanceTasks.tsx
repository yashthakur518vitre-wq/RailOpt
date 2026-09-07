import React, { useState, useEffect } from 'react';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { MaintenanceTask } from '../types';
import api from '../api/client';
import { Wrench, AlertTriangle, Filter, Plus, X } from 'lucide-react';

export default function MaintenanceTasks() {
  const [tasks, setTasks] = useState<MaintenanceTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterDept, setFilterDept] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Form State
  const [formData, setFormData] = useState({
    asset_id: 'AST-001',
    department: 'Engineering',
    task_type: 'Preventive',
    description: 'New maintenance task',
    due_date: new Date().toISOString().split('T')[0],
    estimated_duration: 2.0,
    criticality: 'Medium',
    corridor_id: 'COR-001'
  });
  const [submitting, setSubmitting] = useState(false);

  const loadTasks = () => {
    setLoading(true);
    api.get('/maintenance').then((res: any) => {
      setTasks(res.data.data || []);
      setLoading(false);
    }).catch((err: any) => {
      setError(err.message || 'Failed to load tasks');
      setLoading(false);
    });
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const newTask = {
      task_id: `TSK-N${Math.floor(Math.random() * 10000)}`,
      asset_id: formData.asset_id,
      department: formData.department,
      task_type: formData.task_type,
      description: formData.description,
      created_date: new Date().toISOString().split('T')[0],
      due_date: formData.due_date,
      estimated_duration: Number(formData.estimated_duration),
      required_block_duration: Number(formData.estimated_duration) * 1.2,
      criticality: formData.criticality,
      urgency: 'Medium',
      safety_impact: formData.criticality === 'Critical' ? 'High' : 'Medium',
      asset_impact: 'High',
      status: 'PENDING',
      required_resources: 'Track_Gang',
      preferred_time_window: 'Any',
      corridor_id: formData.corridor_id,
    };

    try {
      await api.post('/maintenance', newTask);
      setIsModalOpen(false);
      loadTasks(); // refresh data
    } catch (err: any) {
      alert("Failed to create task: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredTasks = filterDept ? tasks.filter(t => t.department === filterDept) : tasks;

  const columns = [
    { key: 'task_id', header: 'Task ID', render: (row: MaintenanceTask) => <span className="font-mono text-blue-600 font-medium">{row.task_id}</span> },
    { key: 'asset_id', header: 'Asset' },
    { key: 'department', header: 'Department', render: (row: MaintenanceTask) => <span className="px-2.5 py-1 bg-slate-100 text-slate-700 dark:text-slate-300 rounded-md text-xs font-medium">{row.department}</span> },
    { key: 'criticality', header: 'Criticality', render: (row: MaintenanceTask) => <StatusBadge status={row.criticality} /> },
    { key: 'due_date', header: 'Due Date', render: (row: MaintenanceTask) => <span className="text-slate-600 dark:text-slate-400 font-medium">{row.due_date}</span> },
    { key: 'ai_priority_level', header: 'AI Priority', render: (row: MaintenanceTask) => row.ai_priority_level ? <StatusBadge status={row.ai_priority_level} /> : <span className="text-slate-400">-</span> },
    { key: 'ai_risk_percentage', header: 'AI Failure Risk', render: (row: MaintenanceTask) => (
      row.ai_risk_percentage != null ? (
        <span className={`font-semibold ${Number(row.ai_risk_percentage) > 50 ? 'text-rose-600' : Number(row.ai_risk_percentage) > 20 ? 'text-amber-600' : 'text-emerald-600'}`}>
          {Number(row.ai_risk_percentage).toFixed(1)}%
        </span>
      ) : <span className="text-slate-400">-</span>
    )},
    { key: 'estimated_duration', header: 'Duration', render: (row: MaintenanceTask) => <span className="text-slate-600 dark:text-slate-400 font-medium">{typeof row.estimated_duration === 'number' ? `${row.estimated_duration.toFixed(2)} hrs` : '-'}</span> },
    { key: 'status', header: 'Status', render: (row: MaintenanceTask) => <StatusBadge status={row.status} /> }
  ];

  if (loading && tasks.length === 0) return <div className="h-96 flex items-center justify-center"><LoadingSpinner /></div>;
  if (error && tasks.length === 0) return <div className="p-8 text-center text-signal-red bg-signal-red/10 rounded-panel">{error}</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 relative">
      <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <Wrench className="text-blue-600" /> Maintenance Work Management
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Review and manage AI-prioritized tasks.</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-4 bg-slate-50 dark:bg-slate-800 p-2 rounded-lg border border-slate-100">
            <div className="flex items-center gap-2 px-2 text-slate-500 dark:text-slate-400">
              <Filter className="w-4 h-4" />
              <span className="text-sm font-medium">Filter:</span>
            </div>
            <select 
              className="border-none focus:ring-2 focus:ring-blue-500 rounded-md px-3 py-1.5 bg-white dark:bg-slate-900 text-sm font-medium text-slate-700 dark:text-slate-300 shadow-sm cursor-pointer outline-none"
              value={filterDept}
              onChange={(e) => setFilterDept(e.target.value)}
            >
              <option value="">All Depts ({tasks.length})</option>
              <option value="Engineering">Engineering</option>
              <option value="S&T">S&T</option>
              <option value="Traction">Traction</option>
              <option value="Operations">Operations</option>
            </select>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-sm transition-colors"
          >
            <Plus className="w-4 h-4" /> New Task
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <DataTable data={filteredTasks} columns={columns} keyExtractor={(item) => item.task_id} />
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-2xl w-full p-6 animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Create Maintenance Task</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600 dark:text-slate-400">
                <X className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleCreateTask} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Asset ID</label>
                  <input type="text" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.asset_id} onChange={e => setFormData({...formData, asset_id: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Corridor ID</label>
                  <input type="text" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.corridor_id} onChange={e => setFormData({...formData, corridor_id: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Department</label>
                  <select className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.department} onChange={e => setFormData({...formData, department: e.target.value})}>
                    <option>Engineering</option>
                    <option>S&T</option>
                    <option>Traction</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Task Type</label>
                  <select className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.task_type} onChange={e => setFormData({...formData, task_type: e.target.value})}>
                    <option>Preventive</option>
                    <option>Corrective</option>
                    <option>Emergency</option>
                    <option>Inspection</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
                  <input type="text" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Due Date</label>
                  <input type="date" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.due_date} onChange={e => setFormData({...formData, due_date: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Criticality</label>
                  <select className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.criticality} onChange={e => setFormData({...formData, criticality: e.target.value})}>
                    <option>Critical</option>
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Duration (Hours)</label>
                  <input type="number" step="0.5" required className="w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" value={formData.estimated_duration} onChange={e => setFormData({...formData, estimated_duration: Number(e.target.value)})} />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-300 rounded-md hover:bg-slate-50 dark:bg-slate-800 font-medium">Cancel</button>
                <button type="submit" disabled={submitting} className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 font-medium disabled:opacity-50 flex items-center gap-2">
                  {submitting && <LoadingSpinner />}
                  Create Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
