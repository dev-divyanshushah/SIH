import { NavLink } from 'react-router-dom';
import {
  Radio, Map, Cpu, Brain, Route, Grid3X3,
  GitMerge, Clock, BarChart2, Settings,
  Zap,
} from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import clsx from 'clsx';

const NAV_ITEMS = [
  { to: '/', icon: Radio, label: 'Mission Control' },
  { to: '/map', icon: Map, label: 'Live Map' },
  { to: '/fleet', icon: Cpu, label: 'Fleet' },
  { to: '/ai', icon: Brain, label: 'AI Intelligence' },
  { to: '/planner', icon: Route, label: 'Mission Planner' },
  { to: '/coverage', icon: Grid3X3, label: 'Persistent Coverage' },
  { to: '/twin', icon: GitMerge, label: 'Digital Twin' },
  { to: '/timeline', icon: Clock, label: 'Event Timeline' },
  { to: '/analytics', icon: BarChart2, label: 'Analytics' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const { operationalMode, drones, anomalies, coveragePercentage } = useAppStore();
  const active = drones.filter(d => d.status === 'active').length;
  const critical = anomalies.filter(a => a.risk_level === 'critical' && a.status === 'detected').length;

  const modeColors: Record<string, string> = {
    security: 'text-cyan-400',
    humanitarian: 'text-green-400',
    environmental: 'text-emerald-400',
  };

  return (
    <aside className="flex flex-col w-[220px] flex-shrink-0 bg-[#0d1421] border-r border-slate-800/60">
      {/* Logo */}
      <div className="flex flex-col gap-1 px-4 py-4 border-b border-slate-800/60">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-cyan-500/20 border border-cyan-500/40 rounded flex items-center justify-center">
            <Zap size={14} className="text-cyan-400" />
          </div>
          <div>
            <div className="text-white font-bold text-sm tracking-widest">PERSIST-AIR</div>
            <div className="text-slate-500 text-[9px] tracking-widest uppercase">Aerial Intelligence</div>
          </div>
        </div>
        <div className={clsx('text-[9px] font-bold tracking-widest uppercase mt-1', modeColors[operationalMode])}>
          ◉ {operationalMode} mode
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-2 gap-px p-2 border-b border-slate-800/60">
        <div className="bg-slate-900/60 px-3 py-2 rounded">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider">Active</div>
          <div className="text-cyan-400 font-bold text-lg mono">{active}</div>
        </div>
        <div className={clsx('px-3 py-2 rounded', critical > 0 ? 'bg-red-950/40' : 'bg-slate-900/60')}>
          <div className="text-[9px] text-slate-500 uppercase tracking-wider">Critical</div>
          <div className={clsx('font-bold text-lg mono', critical > 0 ? 'text-red-400 animate-pulse-red' : 'text-slate-400')}>{critical}</div>
        </div>
        <div className="bg-slate-900/60 px-3 py-2 rounded">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider">Coverage</div>
          <div className="text-green-400 font-bold text-lg mono">{coveragePercentage.toFixed(1)}%</div>
        </div>
        <div className="bg-slate-900/60 px-3 py-2 rounded">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider">Drones</div>
          <div className="text-slate-300 font-bold text-lg mono">{drones.length}</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-2">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-4 py-2.5 text-[12px] font-medium transition-all',
                isActive
                  ? 'text-cyan-400 bg-cyan-500/10 border-r-2 border-cyan-400'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              )
            }
          >
            <Icon size={14} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom version */}
      <div className="px-4 py-3 border-t border-slate-800/60">
        <div className="text-[9px] text-slate-600 uppercase tracking-widest">v1.0.0 — SIH 2026</div>
      </div>
    </aside>
  );
}
