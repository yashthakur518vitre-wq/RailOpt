import { useState, useEffect } from 'react';
import api from '../api/client';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Search, Plus, X, Package, Users, Zap, Radio, Filter } from 'lucide-react';

interface Resource {
  id: number;
  resource_id: string;
  name: string;
  department: string;
  capability: string;
  availability: string;
  quantity: number;
}

const availabilityColor = (a: string) => {
  switch (a) {
    case 'Available': return 'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800/50';
    case 'Busy': return 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800/50';
    case 'Off_Duty': return 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700';
    default: return 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700';
  }
};

const deptIcon = (dept: string) => {
  switch (dept) {
    case 'Engineering': return <Package className="w-5 h-5 text-blue-500" />;
    case 'Traction': return <Zap className="w-5 h-5 text-amber-500" />;
    case 'S&T': return <Radio className="w-5 h-5 text-purple-500" />;
    default: return <Users className="w-5 h-5 text-slate-500" />;
  }
};

const deptCardColor = (dept: string) => {
  switch (dept) {
    case 'Engineering': return 'border-blue-200 dark:border-blue-800/50';
    case 'Traction': return 'border-amber-200 dark:border-amber-800/50';
    case 'S&T': return 'border-purple-200 dark:border-purple-800/50';
    default: return 'border-slate-200 dark:border-slate-700';
  }
};

export default function Resources() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('All');
  const [availFilter, setAvailFilter] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    resource_id: '',
    name: '',
    department: 'Engineering',
    capability: '',
    availability: 'Available',
    quantity: 1,
  });

  const fetchResources = () => {
    setLoading(true);
    api.get('/resources')
      .then((res: any) => {
        setResources(res.data.data || []);
        setLoading(false);
      })
      .catch((err: any) => {
        setError(err?.message || 'Failed to load resources');
        setLoading(false);
      });
  };

  useEffect(() => { fetchResources(); }, []);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    api.post('/resources', form)
      .then(() => {
        setIsModalOpen(false);
        setForm({ resource_id: '', name: '', department: 'Engineering', capability: '', availability: 'Available', quantity: 1 });
        fetchResources();
      })
      .catch((err: any) => alert('Failed to create resource: ' + (err?.response?.data?.error?.message || err?.message || 'Unknown error')))
      .finally(() => setCreating(false));
  };

  if (loading) return <div className="h-full flex items-center justify-center"><LoadingSpinner /></div>;
  if (error) return (
    <div className="p-6 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-800/50">
      Failed to load resources: {error}
    </div>
  );

  const departments = Array.from(new Set(resources.map(r => r.department))).sort();
  const availabilities = Array.from(new Set(resources.map(r => r.availability))).sort();

  const filtered = resources.filter(r => {
    const q = search.toLowerCase();
    const matchesSearch = !q ||
      r.resource_id.toLowerCase().includes(q) ||
      r.name.toLowerCase().includes(q) ||
      r.capability.toLowerCase().includes(q);
    const matchesDept = deptFilter === 'All' || r.department === deptFilter;
    const matchesAvail = availFilter === 'All' || r.availability === availFilter;
    return matchesSearch && matchesDept && matchesAvail;
  });

  // Department summary cards
  const deptSummary = departments.map(dept => {
    const deptResources = resources.filter(r => r.department === dept);
    const totalQty = deptResources.reduce((sum, r) => sum + r.quantity, 0);
    const availableQty = deptResources.filter(r => r.availability === 'Available').reduce((sum, r) => sum + r.quantity, 0);
    return { dept, count: deptResources.length, totalQty, availableQty };
  });

  const totalResources = resources.length;
  const totalUnits = resources.reduce((sum, r) => sum + r.quantity, 0);
  const availableUnits = resources.filter(r => r.availability === 'Available').reduce((sum, r) => sum + r.quantity, 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Resource Management</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Personnel, equipment, and maintenance crew allocation.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm shadow-sm"
        >
          <Plus size={16} /> Add Resource
        </button>
      </div>

      {/* Overall Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-5">
          <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">Total Resources</div>
          <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mt-1">{totalResources}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">{totalUnits} total units</div>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-5">
          <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">Available Units</div>
          <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{availableUnits}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">of {totalUnits} total</div>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-5">
          <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">Departments</div>
          <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mt-1">{departments.length}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">{departments.join(', ')}</div>
        </div>
      </div>

      {/* Department Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {deptSummary.map(({ dept, count, totalQty, availableQty }) => (
          <div key={dept} className={`bg-white dark:bg-slate-900 rounded-xl shadow-sm border-2 ${deptCardColor(dept)} p-5`}>
            <div className="flex items-center gap-3 mb-3">
              {deptIcon(dept)}
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{dept}</h3>
            </div>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-xl font-bold text-slate-900 dark:text-slate-100">{count}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400">Resources</div>
              </div>
              <div>
                <div className="text-xl font-bold text-slate-900 dark:text-slate-100">{totalQty}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400">Units</div>
              </div>
              <div>
                <div className="text-xl font-bold text-emerald-600 dark:text-emerald-400">{availableQty}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400">Available</div>
              </div>
            </div>
            {/* Availability bar */}
            <div className="mt-3">
              <div className="w-full h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full"
                  style={{ width: `${totalQty > 0 ? (availableQty / totalQty * 100) : 0}%` }}
                />
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 text-right">
                {totalQty > 0 ? `${(availableQty / totalQty * 100).toFixed(0)}% available` : 'No units'}
              </div>
            </div>
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
              placeholder="Search by name, ID, or capability..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select value={deptFilter} onChange={(e) => setDeptFilter(e.target.value)}
              className="border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="All">All Departments</option>
              {departments.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
            <select value={availFilter} onChange={(e) => setAvailFilter(e.target.value)}
              className="border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="All">All Status</option>
              {availabilities.map(a => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">
            {filtered.length} of {totalResources} resources
          </div>
        </div>
      </div>

      {/* Resource Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-400 dark:text-slate-500">
            <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-lg font-medium">No resources match your filters</p>
            <p className="text-sm mt-1">Try adjusting your search or filter criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-medium">
                <tr>
                  <th className="text-left px-4 py-3">Resource ID</th>
                  <th className="text-left px-4 py-3">Name</th>
                  <th className="text-left px-4 py-3">Department</th>
                  <th className="text-left px-4 py-3">Capability</th>
                  <th className="text-left px-4 py-3">Availability</th>
                  <th className="text-left px-4 py-3">Quantity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filtered.map((r) => (
                  <tr key={r.resource_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3 font-semibold text-slate-900 dark:text-slate-100">{r.resource_id}</td>
                    <td className="px-4 py-3 text-slate-700 dark:text-slate-300">{r.name}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {deptIcon(r.department)}
                        <span className="text-slate-700 dark:text-slate-300 font-medium">{r.department}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-bold text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                        {r.capability.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-bold border ${availabilityColor(r.availability)}`}>
                        {r.availability.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-bold text-slate-900 dark:text-slate-100">{r.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Resource Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-lg w-full p-6 animate-in zoom-in-95 duration-200 border border-slate-200 dark:border-slate-800">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Add Resource</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Resource ID</label>
                  <input required value={form.resource_id} onChange={e => setForm({ ...form, resource_id: e.target.value })}
                    placeholder="e.g. RES-031"
                    className="w-full border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Name</label>
                  <input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                    placeholder="e.g. Welding Unit Alpha"
                    className="w-full border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Department</label>
                  <select required value={form.department} onChange={e => setForm({ ...form, department: e.target.value })}
                    className="w-full border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                    <option value="Engineering">Engineering</option>
                    <option value="Traction">Traction</option>
                    <option value="S&T">S&T</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Capability</label>
                  <input required value={form.capability} onChange={e => setForm({ ...form, capability: e.target.value })}
                    placeholder="e.g. Track_Machine"
                    className="w-full border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Availability</label>
                  <select required value={form.availability} onChange={e => setForm({ ...form, availability: e.target.value })}
                    className="w-full border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                    <option value="Available">Available</option>
                    <option value="Busy">Busy</option>
                    <option value="Off_Duty">Off Duty</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Quantity</label>
                  <input required type="number" min={1} value={form.quantity} onChange={e => setForm({ ...form, quantity: parseInt(e.target.value) || 1 })}
                    className="w-full border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <button type="button" onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 font-medium text-sm">
                  Cancel
                </button>
                <button type="submit" disabled={creating}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed">
                  {creating ? 'Creating...' : 'Create Resource'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
