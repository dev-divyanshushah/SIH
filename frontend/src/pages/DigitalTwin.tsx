import { useState } from 'react';
import { GitMerge, Play, Square, RotateCcw, FastForward, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import { MapView } from '@/components/map/MapView';
import { toast } from 'sonner';
import clsx from 'clsx';

export function DigitalTwin() {
  const { simulationRunning, speedMultiplier, setSimulationRunning, setSpeedMultiplier, tick, coveragePercentage } = useAppStore();

  const handleStart = async () => {
    await api.system.start();
    setSimulationRunning(true);
  };
  const handlePause = async () => {
    await api.system.pause();
    setSimulationRunning(false);
  };
  const handleReset = async () => {
    await api.system.reset();
    toast.info('Digital twin simulation reset');
  };
  const handleSpeed = async (mult: number) => {
    await api.system.setSpeed(mult);
    setSpeedMultiplier(mult);
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-[#080c14]">
      {/* Simulation Header Controls */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-[#0d1421]">
        <div className="flex items-center gap-3">
          <GitMerge size={18} className="text-cyan-400" />
          <div>
            <h1 className="text-sm font-bold text-slate-100 tracking-wider">DIGITAL TWIN & MULTI-DRONE SIMULATION</h1>
            <p className="text-[10px] text-slate-500">10–15 Hour Mission Scenario Playback & Rotation Validation</p>
          </div>
        </div>

        {/* Speed & Control buttons */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-[#111827] border border-slate-800 rounded p-1">
            {[1, 5, 10].map((s) => (
              <button
                key={s}
                onClick={() => handleSpeed(s)}
                className={clsx(
                  'px-2 py-0.5 text-xs font-mono rounded',
                  speedMultiplier === s ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200'
                )}
              >
                {s}x
              </button>
            ))}
          </div>

          {!simulationRunning ? (
            <button onClick={handleStart} className="btn-tactical success text-xs">
              <Play size={12} /> START SIMULATION
            </button>
          ) : (
            <button onClick={handlePause} className="btn-tactical text-xs text-amber-400">
              <Square size={12} /> PAUSE
            </button>
          )}

          <button onClick={handleReset} className="btn-tactical text-xs">
            <RotateCcw size={12} /> RESET
          </button>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-2 gap-4 p-4 bg-[#0d1421]/50 border-b border-slate-800">
        {/* WITHOUT PERSIST-AIR */}
        <div className="bg-[#111827] border border-red-500/30 p-3 rounded flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-red-400 flex items-center gap-1">
              <AlertTriangle size={14} /> WITHOUT PERSIST-AIR
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Coverage gaps occur when batteries deplete (~35 min interval blackouts).
            </div>
          </div>
          <div className="mono font-bold text-red-400 text-sm">GAP RISK: HIGH</div>
        </div>

        {/* WITH PERSIST-AIR */}
        <div className="bg-[#111827] border border-green-500/30 p-3 rounded flex items-center justify-between bg-green-500/5">
          <div>
            <div className="text-xs font-bold text-green-400 flex items-center gap-1">
              <ShieldCheck size={14} /> WITH PERSIST-AIR (INTELLIGENT ROTATION)
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Continuous 98%+ coverage maintained seamlessly over 10+ hours.
            </div>
          </div>
          <div className="mono font-bold text-green-400 text-sm">{coveragePercentage.toFixed(1)}% COVERAGE</div>
        </div>
      </div>

      {/* Main Twin Visualization Map */}
      <div className="flex-1 relative">
        <MapView />
      </div>
    </div>
  );
}
