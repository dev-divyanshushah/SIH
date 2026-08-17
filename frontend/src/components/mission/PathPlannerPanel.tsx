import { useState, useEffect } from 'react';
import { Navigation, Route, Zap, ArrowRight, ShieldCheck } from 'lucide-react';
import { api } from '@/services/api';
import clsx from 'clsx';

export function PathPlannerPanel() {
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.energy
      .planPath({
        drone_id: 'PA-04',
        target_lat: 28.6139 - 0.010,
        target_lon: 77.2090 + 0.008,
      })
      .then((res: any) => {
        setPlan(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Path planning error', err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-[#0d1421] border border-slate-800/60 rounded p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
            <Route size={14} className="text-blue-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">ENERGY-AWARE MISSION ROUTE PLANNER</h3>
            <p className="text-[10px] text-slate-500">Shortest geometric trajectory vs. wind/altitude energy-optimized route</p>
          </div>
        </div>
      </div>

      {plan && (
        <div className="grid grid-cols-2 gap-4">
          {/* Direct Shortest Path */}
          <div className="bg-[#111827] border border-slate-800 p-3 rounded flex flex-col gap-3">
            <div className="flex justify-between items-center text-xs font-bold border-b border-slate-800 pb-2 text-slate-400">
              <span>DIRECT SHORTEST PATH</span>
              <span className="text-[10px] text-slate-500">Standard Navigation</span>
            </div>
            <div className="flex flex-col gap-1 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Distance:</span>
                <span className="mono text-slate-200">{plan.shortest_distance_m} m</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Est. Battery Cost:</span>
                <span className="mono text-red-400">{plan.shortest_energy_pct}%</span>
              </div>
            </div>
          </div>

          {/* Energy Optimized Path */}
          <div className="bg-[#111827] border border-cyan-500/40 p-3 rounded flex flex-col gap-3 bg-cyan-500/5">
            <div className="flex justify-between items-center text-xs font-bold border-b border-slate-800 pb-2 text-cyan-400">
              <span className="flex items-center gap-1"><Zap size={12} /> ENERGY-AWARE PATH</span>
              <span className="badge badge-active">RECOMMENDED</span>
            </div>
            <div className="flex flex-col gap-1 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Distance:</span>
                <span className="mono text-slate-200">{plan.energy_path_distance_m} m</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Est. Battery Cost:</span>
                <span className="mono text-green-400 font-bold">{plan.energy_path_energy_pct}%</span>
              </div>
              <div className="flex justify-between text-slate-400 border-t border-slate-800/80 pt-1 mt-1">
                <span className="text-cyan-400 font-medium">Net Energy Saved:</span>
                <span className="mono text-green-400 font-bold">-{plan.energy_saving_pct}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {plan?.explanation && (
        <div className="bg-slate-900/60 border border-slate-800 p-2.5 rounded text-[10px] text-slate-400 flex items-start gap-2">
          <ShieldCheck size={14} className="text-cyan-400 flex-shrink-0 mt-0.5" />
          <span>{plan.explanation}</span>
        </div>
      )}
    </div>
  );
}
