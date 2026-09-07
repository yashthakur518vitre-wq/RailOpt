import os
import json

base_dir = r"c:\Users\lenovo\Desktop\RAILBlock ai\frontend"

files = {
    "package.json": """{
  "name": "railblock-ai",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0",
    "axios": "^1.7.0",
    "recharts": "^2.12.0",
    "lucide-react": "^0.441.0",
    "clsx": "^2.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}""",
    "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}""",
    "tsconfig.node.json": """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}""",
    "vite.config.ts": """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});""",
    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a365d',
          light: '#2b6cb0',
          dark: '#0f172a'
        },
        accent: {
          DEFAULT: '#ed8936',
          light: '#f6ad55',
          dark: '#dd6b20'
        },
        danger: '#e53e3e',
        success: '#38a169',
        warning: '#ecc94b',
        slate: {
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155'
        }
      }
    },
  },
  plugins: [],
}""",
    "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}""",
    "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RailBlock AI</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>""",
    ".env.example": "VITE_API_BASE_URL=http://localhost:8000\n",
    "src/main.tsx": """import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);""",
    "src/App.tsx": """import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import MaintenanceTasks from './pages/MaintenanceTasks';
import Assets from './pages/Assets';
import Corridors from './pages/Corridors';
import Trains from './pages/Trains';
import BlockAvailability from './pages/BlockAvailability';
import AIPriority from './pages/AIPriority';
import GeneratePlan from './pages/GeneratePlan';
import WeeklyPlan from './pages/WeeklyPlan';
import MonthlyPlan from './pages/MonthlyPlan';
import Conflicts from './pages/Conflicts';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/tasks" element={<MaintenanceTasks />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/corridors" element={<Corridors />} />
        <Route path="/trains" element={<Trains />} />
        <Route path="/blocks" element={<BlockAvailability />} />
        <Route path="/ai-priority" element={<AIPriority />} />
        <Route path="/generate-plan" element={<GeneratePlan />} />
        <Route path="/weekly-plan" element={<WeeklyPlan />} />
        <Route path="/monthly-plan" element={<MonthlyPlan />} />
        <Route path="/conflicts" element={<Conflicts />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}""",
    "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-slate-50 text-slate-900;
  }
}

/* Custom Scrollbar for dense data display */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  @apply bg-slate-100 rounded;
}
::-webkit-scrollbar-thumb {
  @apply bg-slate-300 rounded hover:bg-slate-400;
}
""",
    "src/types/index.ts": """export interface Asset {
  id: number; asset_id: string; asset_type: string; department: string; location: string; corridor_id: string;
  criticality: string; installation_date: string; last_maintenance_date: string; next_due_date: string;
  condition_score: number; availability_status: string; failure_history: number;
}
export interface MaintenanceTask {
  id: number; task_id: string; asset_id: string; department: string; task_type: string; description: string;
  created_date: string; due_date: string; estimated_duration: number; required_block_duration: number;
  criticality: string; urgency: string; safety_impact: string; asset_impact: string; status: string;
  required_resources: string; preferred_time_window: string; corridor_id: string; dependency_task_id: string | null;
  ai_priority_score: number | null; ai_priority_level: string | null; ai_failure_risk: number | null;
  ai_risk_percentage: number | null; ai_train_impact_score: number | null; ai_reasons: string | null; ai_model_version: string | null;
}
export interface Defect {
  id: number; defect_id: string; asset_id: string; department: string; severity: string; detected_date: string;
  description: string; failure_probability: number; safety_impact: string; operational_impact: string; status: string;
}
export interface Corridor {
  id: number; corridor_id: string; name: string; start_station: string; end_station: string; distance_km: number;
  route_type: string; capacity: number; availability_windows: string;
}
export interface Train {
  id: number; train_id: string; train_number: string; train_type: string; origin: string; destination: string;
  corridor_id: string; arrival_time: string; departure_time: string; frequency: string; priority: string;
  occupancy: number; forecasted: boolean;
}
export interface Block {
  id: number; block_id: string; corridor_id: string; start_time: string; end_time: string; duration: number;
  status: string; source: string; department: string; reason: string; plan_id: string | null;
}
export interface Resource {
  id: number; resource_id: string; name: string; department: string; capability: string; availability: string; quantity: number;
}
export interface Plan {
  id: number; plan_id: string; horizon: string; generated_at: string; status: string; objective_score: number;
  total_tasks: number; scheduled_tasks: number; unscheduled_tasks: number; total_block_hours: number;
  estimated_asset_availability: number; train_impact_score: number; maintenance_completion: number;
  coordination_score: number; validation_status: string; model_versions: string;
}
export interface DashboardSummary {
  assetAvailability: number; maintenanceCompletion: number; criticalTasks: number; activeBlocks: number;
  trainImpact: number; overdueTasks: number;
}
export interface APIResponse<T> { data: T; message?: string; }
export interface PaginatedResponse<T> { items: T[]; total: number; page: number; size: number; }
export interface PlanComparison { baseline: Plan; optimized: Plan; }
export interface AIAnalysis { task_id: string; score: number; risk: number; reasons: string[]; recommendation: string; version: string; }
export interface GeneratePlanResponse { plan: Plan; comparison: PlanComparison; validation: string; }
""",
    "src/api/client.ts": """import axios from 'axios';
const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000' });
api.interceptors.response.use((response) => response.data, (error) => Promise.reject(error));
export default api;
""",
    "src/api/assets.ts": """import api from './client'; import { Asset } from '../types';
export const getAssets = () => api.get<any, Asset[]>('/api/assets');
""",
    "src/api/maintenance.ts": """import api from './client'; import { MaintenanceTask } from '../types';
export const getTasks = () => api.get<any, MaintenanceTask[]>('/api/tasks');
""",
    "src/api/planning.ts": """import api from './client'; import { Plan, GeneratePlanResponse } from '../types';
export const generatePlan = (horizon: string) => api.post<any, GeneratePlanResponse>('/api/planning/generate', null, { params: { horizon } });
export const getPlans = () => api.get<any, Plan[]>('/api/plans');
""",
    "src/api/analytics.ts": """import api from './client'; import { DashboardSummary } from '../types';
export const getDashboardSummary = () => api.get<any, DashboardSummary>('/api/analytics/dashboard');
""",
    "src/api/ai.ts": """import api from './client'; import { AIAnalysis } from '../types';
export const getAIAnalysis = (taskId: string) => api.get<any, AIAnalysis>(`/api/ai/analysis/${taskId}`);
""",
    "src/utils/formatters.ts": """export const formatDate = (d: string) => new Date(d).toLocaleDateString();
export const formatPercent = (n: number) => `${(n * 100).toFixed(1)}%`;
""",
    "src/utils/constants.ts": """export const COLORS = { primary: '#1a365d', accent: '#ed8936', danger: '#e53e3e', success: '#38a169', warning: '#ecc94b' };
""",
    "src/hooks/useApi.ts": """import { useState, useEffect, useCallback } from 'react';
export function useApi<T>(fetcher: () => Promise<T>, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const refetch = useCallback(async () => {
    setLoading(true); setError(null);
    try { const res = await fetcher(); setData(res); } catch (err: any) { setError(err.message || 'Error fetching data'); }
    finally { setLoading(false); }
  }, [fetcher]);
  useEffect(() => { refetch(); }, [...deps]);
  return { data, loading, error, refetch };
}
""",
    "src/components/layout/Sidebar.tsx": """import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Wrench, Box, Route, Train, Calendar, Brain, Sparkles, CalendarDays, CalendarRange, AlertTriangle, BarChart3, Settings } from 'lucide-react';
import clsx from 'clsx';
const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/tasks', label: 'Maintenance Tasks', icon: Wrench },
  { path: '/assets', label: 'Assets', icon: Box },
  { path: '/corridors', label: 'Corridors', icon: Route },
  { path: '/trains', label: 'Trains', icon: Train },
  { path: '/blocks', label: 'Block Availability', icon: Calendar },
  { path: '/ai-priority', label: 'AI Priority', icon: Brain },
  { path: '/generate-plan', label: 'Generate Plan', icon: Sparkles },
  { path: '/weekly-plan', label: 'Weekly Plan', icon: CalendarDays },
  { path: '/monthly-plan', label: 'Monthly Plan', icon: CalendarRange },
  { path: '/conflicts', label: 'Conflicts', icon: AlertTriangle },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/settings', label: 'Settings', icon: Settings },
];
export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-white min-h-screen flex flex-col">
      <div className="p-4 flex items-center gap-3 text-xl font-bold border-b border-slate-800">
        <Train className="text-accent" /> RailBlock AI
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        {navItems.map((item) => (
          <NavLink key={item.path} to={item.path} className={({ isActive }) => clsx('flex items-center gap-3 px-4 py-3 hover:bg-slate-800 transition-colors', isActive && 'bg-slate-800 border-l-4 border-accent text-accent')}> 
            <item.icon size={20} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
""",
    "src/components/layout/Topbar.tsx": """export default function Topbar() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <h1 className="text-xl font-semibold text-primary">System Dashboard</h1>
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-success"></div>
        <span className="text-sm font-medium">System Online</span>
      </div>
    </header>
  );
}
""",
    "src/components/layout/Layout.tsx": """import Sidebar from './Sidebar'; import Topbar from './Topbar';
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
""",
    "src/components/ui/LoadingSpinner.tsx": """export default function LoadingSpinner() {
  return <div className="flex justify-center items-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;
}
""",
    "src/components/ui/EmptyState.tsx": """export default function EmptyState({ message }: { message: string }) {
  return <div className="text-center p-8 text-slate-500">{message}</div>;
}
""",
    "src/pages/Dashboard.tsx": """import React from 'react'; export default function Dashboard() { return <div>Dashboard</div>; }""",
    "src/pages/MaintenanceTasks.tsx": """import React from 'react'; export default function MaintenanceTasks() { return <div>Maintenance Tasks</div>; }""",
    "src/pages/Assets.tsx": """import React from 'react'; export default function Assets() { return <div>Assets</div>; }""",
    "src/pages/Corridors.tsx": """import React from 'react'; export default function Corridors() { return <div>Corridors</div>; }""",
    "src/pages/Trains.tsx": """import React from 'react'; export default function Trains() { return <div>Trains</div>; }""",
    "src/pages/BlockAvailability.tsx": """import React from 'react'; export default function BlockAvailability() { return <div>Block Availability</div>; }""",
    "src/pages/AIPriority.tsx": """import React from 'react'; export default function AIPriority() { return <div>AI Priority</div>; }""",
    "src/pages/GeneratePlan.tsx": """import React from 'react'; export default function GeneratePlan() { return <div>Generate Plan</div>; }""",
    "src/pages/WeeklyPlan.tsx": """import React from 'react'; export default function WeeklyPlan() { return <div>Weekly Plan</div>; }""",
    "src/pages/MonthlyPlan.tsx": """import React from 'react'; export default function MonthlyPlan() { return <div>Monthly Plan</div>; }""",
    "src/pages/Conflicts.tsx": """import React from 'react'; export default function Conflicts() { return <div>Conflicts</div>; }""",
    "src/pages/Analytics.tsx": """import React from 'react'; export default function Analytics() { return <div>Analytics</div>; }""",
    "src/pages/Settings.tsx": """import React from 'react'; export default function Settings() { return <div>Settings</div>; }"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
print("Frontend basic structure generated successfully.")
