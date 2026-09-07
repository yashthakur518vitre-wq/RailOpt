import { useState, useEffect } from 'react';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import api from '../api/client';
import { Database, Brain, Activity, CheckCircle2, XCircle, AlertTriangle, Monitor } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export default function Settings() {
  const [status, setStatus] = useState<any>(null);
  const [aiStatus, setAiStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    Promise.all([
      api.get('/dashboard/summary').then(r => r.data).catch(() => null),
      api.get('/ai/model-status').then(r => r.data).catch(() => null),
    ]).then(([dashData, aiData]) => {
      setStatus(dashData);
      setAiStatus(aiData);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="h-96 flex items-center justify-center"><LoadingSpinner /></div>;

  const kpis = status?.data?.kpis || {};

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">System Settings & Status</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Diagnostic overview of the AI and Optimization engine.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Core System Status */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
          <h3 className="flex items-center gap-2 text-lg font-bold mb-6 text-slate-800 dark:text-slate-100 border-b border-slate-100 dark:border-slate-800 pb-4">
            <Activity className="text-blue-600" /> Infrastructure & API
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-600 dark:text-slate-400 font-medium">FastAPI Backend</span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-md border border-emerald-100 dark:border-emerald-800/50">
                <CheckCircle2 className="w-3.5 h-3.5" /> ONLINE
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600 dark:text-slate-400 font-medium">Google OR-Tools CP-SAT</span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-md border border-emerald-100 dark:border-emerald-800/50">
                <CheckCircle2 className="w-3.5 h-3.5" /> READY
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600 dark:text-slate-400 font-medium">SQLite Database</span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-md border border-emerald-100 dark:border-emerald-800/50">
                <CheckCircle2 className="w-3.5 h-3.5" /> CONNECTED
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600 dark:text-slate-400 font-medium">System Version</span>
              <span className="text-slate-800 dark:text-slate-200 font-mono text-sm font-semibold bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                1.0.0-SIH
              </span>
            </div>
          </div>
        </div>

        {/* System Preferences */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
          <h3 className="flex items-center gap-2 text-lg font-bold mb-6 text-slate-800 dark:text-slate-100 border-b border-slate-100 dark:border-slate-800 pb-4">
            <Monitor className="text-slate-600 dark:text-slate-400" /> Preferences
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-600 dark:text-slate-400 font-medium">Interface Theme</span>
              <select 
                value={theme}
                onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'system')}
                className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2"
              >
                <option value="light">Light Mode</option>
                <option value="dark">Dark Mode</option>
                <option value="system">System Preference</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI Model Status */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
          <h3 className="flex items-center gap-2 text-lg font-bold mb-6 text-slate-800 dark:text-slate-100 border-b border-slate-100 dark:border-slate-800 pb-4">
            <Brain className="text-purple-600" /> AI ML Models
          </h3>
          <div className="space-y-4">
            {aiStatus?.data ? (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400 font-medium">Priority Model (.joblib)</span>
                  {aiStatus.data.priority_model?.loaded ? (
                    <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-md border border-emerald-100 dark:border-emerald-800/50">
                      <CheckCircle2 className="w-3.5 h-3.5" /> LOADED
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 px-2.5 py-1 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-bold rounded-md border border-red-100 dark:border-red-800/50">
                      <XCircle className="w-3.5 h-3.5" /> MISSING
                    </span>
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400 font-medium">Risk Model (.joblib)</span>
                  {aiStatus.data.risk_model?.loaded ? (
                    <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-md border border-emerald-100 dark:border-emerald-800/50">
                      <CheckCircle2 className="w-3.5 h-3.5" /> LOADED
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 px-2.5 py-1 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-bold rounded-md border border-red-100 dark:border-red-800/50">
                      <XCircle className="w-3.5 h-3.5" /> MISSING
                    </span>
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400 font-medium">Impact Model (.joblib)</span>
                  {aiStatus.data.impact_model?.loaded ? (
                    <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-md border border-emerald-100 dark:border-emerald-800/50">
                      <CheckCircle2 className="w-3.5 h-3.5" /> LOADED
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 px-2.5 py-1 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-bold rounded-md border border-red-100 dark:border-red-800/50">
                      <XCircle className="w-3.5 h-3.5" /> MISSING
                    </span>
                  )}
                </div>
              </>
            ) : (
              <div className="text-slate-500 dark:text-slate-400 font-medium flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" /> AI model status unavailable
              </div>
            )}
          </div>
        </div>

        {/* Diagnostic Data Summary */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 md:col-span-2">
          <h3 className="flex items-center gap-2 text-lg font-bold mb-6 text-slate-800 dark:text-slate-100 border-b border-slate-100 dark:border-slate-800 pb-4">
            <Database className="text-blue-600" /> Diagnostic Cache
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg text-center border border-slate-100 dark:border-slate-700">
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">Cached Asset %</div>
              <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{(kpis['Asset Availability %'] || 0).toFixed(1)}%</div>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg text-center border border-slate-100 dark:border-slate-700">
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">Active Blocks</div>
              <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{kpis['Active Blocks'] || kpis['Number of Blocks'] || 0}</div>
            </div>
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg text-center border border-red-100 dark:border-red-800/30">
              <div className="text-red-700 dark:text-red-400 text-xs font-bold uppercase tracking-wider mb-2">Critical Pending</div>
              <div className="text-2xl font-bold text-red-700 dark:text-red-400">{kpis['Critical Tasks Pending'] || 0}</div>
            </div>
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-center border border-amber-100 dark:border-amber-800/30">
              <div className="text-amber-700 dark:text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">Overdue Tasks</div>
              <div className="text-2xl font-bold text-amber-700 dark:text-amber-400">{kpis['Overdue Tasks'] || 0}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
