import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Brain, AlertCircle, ArrowUpCircle } from 'lucide-react';
import api from '../api/client';
import EmptyState from '../components/ui/EmptyState';

export default function AIPriority() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get('/ai/priorities/top').then((res: any) => {
      const payload = res?.data?.data;
      setAnalyses(Array.isArray(payload) ? payload : []);
      setLoading(false);
    }).catch((err) => {
      setError(err.message || 'Failed to load AI Priorities');
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="p-8 text-center text-signal-red bg-signal-red/10 rounded-panel">{error}</div>;
  if (analyses.length === 0) return <EmptyState message="No AI Analysis data available" />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">AI Priority Analysis</h1>
      <p className="text-sm text-slate-500">Top pending tasks ranked by ML priority model</p>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {(analyses || []).map(a => (
          <div key={a.task_id} className="bg-white p-6 rounded-panel border border-ink-track">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2 font-data">
                  <Brain className="text-steel-dark" size={20} /> {a.task_id}
                </h3>
                <span className="text-sm text-slate-500">{a.department} • {a.task_type}</span>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-signal-red font-data">{(a.priority_score || 0).toFixed(2)}</div>
                <div className="text-sm font-medium text-slate-500">Priority Score</div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm p-3 bg-slate-50 rounded border border-slate-100">
                <span className="font-medium text-slate-700 flex items-center gap-2">
                  <AlertCircle size={16} className={a.criticality === 'Critical' ? 'text-signal-red' : 'text-signal-amber'} /> 
                  Criticality Prediction
                </span>
                <span className="font-bold text-slate-900">{a.criticality}</span>
              </div>
              <div className="flex justify-between items-center text-sm p-3 bg-slate-50 rounded border border-slate-100">
                <span className="font-medium text-slate-700 flex items-center gap-2">
                  <ArrowUpCircle size={16} className={a.urgency === 'High' ? 'text-signal-red' : 'text-signal-amber'} /> 
                  Urgency Prediction
                </span>
                <span className="font-bold text-slate-900">{a.urgency}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
