import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, Calendar, Server, Settings, Wrench, BarChart3, Activity, Route, Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

const navItems = [
  { to: '/', label: 'Dashboard', icon: Home },
  { to: '/corridors', label: 'Corridor Network', icon: Route },
  { to: '/trains', label: 'Train Operations', icon: Activity },
  { to: '/schedules', label: 'Schedules', icon: Calendar },
  { to: '/resources', label: 'Resources', icon: Server },
  { to: '/plans', label: 'Generate Plan', icon: Calendar },
  { to: '/assets', label: 'Asset Inventory', icon: Server },
  { to: '/maintenance', label: 'Maintenance Tasks', icon: Wrench },
  { to: '/ai-priority', label: 'AI Priority', icon: Activity },
  { to: '/blocks', label: 'Block Schedule', icon: BarChart3 },
  { to: '/reports', label: 'Reports', icon: BarChart3 },
  { to: '/alerts', label: 'Alerts', icon: Activity },
  { to: '/settings', label: 'System Settings', icon: Settings },
  { to: '/admin', label: 'Admin', icon: Settings },
];

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();
  
  return (
    <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
      <button 
        onClick={() => setTheme('light')}
        className={`p-1.5 rounded-md ${theme === 'light' ? 'bg-white dark:bg-slate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'}`}
        title="Light Mode"
      >
        <Sun size={16} />
      </button>
      <button 
        onClick={() => setTheme('dark')}
        className={`p-1.5 rounded-md ${theme === 'dark' ? 'bg-white dark:bg-slate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'}`}
        title="Dark Mode"
      >
        <Moon size={16} />
      </button>
      <button 
        onClick={() => setTheme('system')}
        className={`p-1.5 rounded-md ${theme === 'system' ? 'bg-white dark:bg-slate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'}`}
        title="System Preference"
      >
        <Monitor size={16} />
      </button>
    </div>
  );
};

const Layout: React.FC = () => {
  const location = useLocation();

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900 overflow-hidden font-sans text-slate-900 dark:text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 dark:bg-slate-950 text-white flex flex-col shadow-xl z-10 border-r border-slate-800 dark:border-slate-800">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2 mb-1">
            <Activity className="text-blue-400 w-6 h-6" />
            <h1 className="text-xl font-bold tracking-tight text-white">RAILBlock AI</h1>
          </div>
          <p className="text-xs text-slate-400 font-medium">SIH26027 — Block Planning</p>
        </div>
        <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map(item => {
            const active = location.pathname === item.to || (item.to !== '/' && location.pathname.startsWith(item.to));
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  active 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white dark:hover:bg-slate-800'
                }`}
              >
                <item.icon size={18} className={active ? 'text-white' : 'text-slate-400'} />
                <span className="font-medium text-sm">{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-slate-800 bg-slate-900 dark:bg-slate-950">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-xs text-slate-400 font-medium">CP-SAT Optimizer Online</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-50 dark:bg-[#0f172a]">
        <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center px-8 justify-between shrink-0 shadow-sm z-0">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 tracking-tight">Indian Railways Maintenance Optimization</h2>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <span className="text-sm font-medium text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-700">
              Operations Control Center
            </span>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
