import { useState, useEffect } from 'react';
import { Wifi, WifiOff, Bell, Shield, User, Play, Square, RotateCcw, Zap } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import { toast } from 'sonner';
import clsx from 'clsx';

const MODE_CONFIG = {
  security: { label: 'SECURITY', color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/30' },
  humanitarian: { label: 'HUMANITARIAN', color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/30' },
  environmental: { label: 'ENVIRONMENTAL', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
};

export function TopBar() {
  const [time, setTime] = useState(new Date());
  const {
    wsConnected, operationalMode, simulationRunning,
    setSimulationRunning, anomalies, events,
  } = useAppStore();
  const modeConf = MODE_CONFIG[operationalMode];
  const criticalCount = anomalies.filter(a => a.risk_level === 'critical' && a.status === 'detected').length;

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const handleStart = async () => {
    await api.system.start();
    setSimulationRunning(true);
    toast.success('Simulation started');
  };
  const handlePause = async () => {
    await api.system.pause();
    setSimulationRunning(false);
    toast.info('Simulation paused');
  };
  const handleReset = async () => {
    await api.system.reset();
    toast.info('Simulation reset');
  };
  const handleDemo = async () => {
    await api.system.startDemo();
    toast.success('LIVE DEMO scenario initiated', { description: '17-step scripted mission scenario running...' });
  };

  return (
    <header className="flex items-center justify-between px-4 h-12 flex-shrink-0 bg-[#0d1421] border-b border-slate-800/60">
      {/* Left: Mode badge */}
      <div className="flex items-center gap-3">
        <div className={clsx('flex items-center gap-2 px-3 py-1 rounded border text-[10px] font-bold tracking-widest', modeConf.bg, modeConf.color)}>
          <Shield size={10} />
          {modeConf.label} MODE
        </div>
        {/* System health */}
        <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          ALL SYSTEMS NOMINAL
        </div>
        
        {/* Simulation label */}
        <div className="ml-4 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400/80 text-[9px] tracking-widest font-bold">
          DEMO / SIMULATION
        </div>
      </div>

      {/* Center: Simulation controls */}
      <div className="flex items-center gap-2">
        {!simulationRunning ? (
          <button onClick={handleStart} className="btn-tactical success text-green-400 border-green-500/40 hover:bg-green-500/10">
            <Play size={11} /> START
          </button>
        ) : (
          <button onClick={handlePause} className="btn-tactical text-amber-400 border-amber-500/40 hover:bg-amber-500/10">
            <Square size={11} /> PAUSE
          </button>
        )}
        <button onClick={handleReset} className="btn-tactical">
          <RotateCcw size={11} /> RESET
        </button>
        <button
          onClick={handleDemo}
          className="btn-tactical text-cyan-400 border-cyan-500/40 bg-cyan-500/10 hover:bg-cyan-500/20 font-bold tracking-wider"
        >
          <Zap size={11} /> LIVE DEMO
        </button>
      </div>

      {/* Right: Status info */}
      <div className="flex items-center gap-4">
        {/* Time */}
        <div className="mono text-[11px] text-slate-300">
          {time.toUTCString().slice(17, 25)} UTC
        </div>

        {/* Connection */}
        <div className={clsx('flex items-center gap-1.5 text-[10px]', wsConnected ? 'text-green-400' : 'text-red-400')}>
          {wsConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
          {wsConnected ? 'LIVE' : 'OFFLINE'}
        </div>

        {/* Alerts */}
        <div className={clsx('flex items-center gap-1.5 text-[10px]', criticalCount > 0 ? 'text-red-400 animate-pulse-red' : 'text-slate-500')}>
          <Bell size={12} />
          {criticalCount > 0 ? `${criticalCount} CRITICAL` : 'NO ALERTS'}
        </div>

        {/* Operator */}
        <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
          <div className="w-6 h-6 rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
            <User size={11} className="text-cyan-400" />
          </div>
          <div>
            <div className="text-[10px] text-slate-300 font-medium">OPR-01</div>
            <div className="text-[8px] text-slate-600 uppercase">Operator</div>
          </div>
        </div>
      </div>
    </header>
  );
}
