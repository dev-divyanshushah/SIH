import { useState, useEffect } from 'react';
import { ArrowRight, RefreshCw, Zap, Shield, CheckCircle2 } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import clsx from 'clsx';

export function HandoverPanel() {
  const { activeHandover, drones } = useAppStore();
  const [prediction, setPrediction] = useState<any>(null);

  useEffect(() => {
    api.energy
      .predictHandover({ drone_id: 'PA-02' })
      .then((res) => setPrediction(res))
      .catch((err) => console.error('Handover predict error', err));
  }, []);

  const activeDroneId = activeHandover?.active_drone || 'PA-02';
  const replacementDroneId = activeHandover?.replacement_drone || 'PA-04';

  const activeDrone = drones.find((d) => d.id === activeDroneId);
  const replacementDrone = drones.find((d) => d.id === replacementDroneId);

  return (
    <div className="bg-[#0d1421] border border-slate-800/60 rounded p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <RefreshCw size={14} className="text-cyan-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">PREDICTIVE DRONE HANDOVER ENGINE</h3>
            <p className="text-[10px] text-slate-500">Zero-gap persistent coverage via proactive mid-mission replacement</p>
          </div>
        </div>
        <div className="badge badge-active flex items-center gap-1">
          <Zap size={10} /> CONTINUOUS MISSION
        </div>
      </div>

      {/* Visual Sequence */}
      <div className="bg-[#111827] border border-slate-800 p-4 rounded flex items-center justify-between">
        {/* Active Drone */}
        <div className="flex flex-col gap-1 items-center">
          <span className="text-[9px] text-slate-500 uppercase tracking-wider">ACTIVE DRONE</span>
          <span className="mono text-lg font-bold text-amber-400">{activeDroneId}</span>
          <span className="text-xs text-slate-400">Battery: {activeDrone?.battery_percentage.toFixed(0) ?? 29}%</span>
        </div>

        {/* Transition Arrow */}
        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-2 text-cyan-400">
            <div className="h-0.5 w-12 bg-gradient-to-r from-amber-500 to-cyan-400 animate-pulse" />
            <ArrowRight size={18} />
          </div>
          <span className="text-[9px] mono text-cyan-400 font-medium">Predicted in 06:42</span>
        </div>

        {/* Replacement Drone */}
        <div className="flex flex-col gap-1 items-center">
          <span className="text-[9px] text-slate-500 uppercase tracking-wider">REPLACEMENT DRONE</span>
          <span className="mono text-lg font-bold text-green-400">{replacementDroneId}</span>
          <span className="text-xs text-slate-400">Battery: {replacementDrone?.battery_percentage.toFixed(0) ?? 87}%</span>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-[#111827] border border-slate-800 p-3 rounded text-center">
          <div className="text-[9px] text-slate-500 uppercase">Coverage Continuity</div>
          <div className="mono text-lg font-bold text-green-400">
            {prediction?.coverage_continuity ?? 98.7}%
          </div>
        </div>
        <div className="bg-[#111827] border border-slate-800 p-3 rounded text-center">
          <div className="text-[9px] text-slate-500 uppercase">Handover Confidence</div>
          <div className="mono text-lg font-bold text-cyan-400">
            {prediction?.handover_confidence ?? 94}%
          </div>
        </div>
        <div className="bg-[#111827] border border-slate-800 p-3 rounded text-center">
          <div className="text-[9px] text-slate-500 uppercase">Handover State</div>
          <div className="text-xs font-bold text-amber-400 mt-1 uppercase">
            {activeHandover?.status || 'MONITORING'}
          </div>
        </div>
      </div>
    </div>
  );
}
