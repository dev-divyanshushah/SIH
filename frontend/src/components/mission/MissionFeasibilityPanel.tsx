import { useState, useEffect } from 'react';
import { Target, CheckCircle2, AlertTriangle, XCircle, Shield, ArrowRight } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import type { MissionFeasibility } from '@/types';
import clsx from 'clsx';

export function MissionFeasibilityPanel() {
  const { drones, anomalies } = useAppStore();
  const selectedAnomaly = anomalies.find((a) => a.status === 'detected') || anomalies[0];
  const selectedDrone = drones.find((d) => d.id === 'PA-02') || drones[0];

  const [feasibility, setFeasibility] = useState<MissionFeasibility | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedDrone || !selectedAnomaly) return;
    setLoading(true);

    api.energy
      .feasibility({
        drone_id: selectedDrone.id,
        battery_percentage: selectedDrone.battery_percentage,
        distance_to_target_m: 4200,
        estimated_investigation_minutes: 12,
        return_distance_m: 4500,
        wind_factor: 1.1,
        mission_priority: selectedAnomaly.risk_level || 'high',
      })
      .then((res: any) => {
        setFeasibility(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Feasibility calculation error', err);
        setLoading(false);
      });
  }, [selectedDrone?.id, selectedDrone?.battery_percentage, selectedAnomaly?.id]);

  if (!selectedDrone || !selectedAnomaly) {
    return <div className="p-4 text-slate-500 text-xs">No active anomaly or drone available.</div>;
  }

  const resultColor =
    feasibility?.result === 'FEASIBLE'
      ? 'text-green-400 bg-green-500/10 border-green-500/40'
      : feasibility?.result === 'MARGINAL'
      ? 'text-amber-400 bg-amber-500/10 border-amber-500/40'
      : 'text-red-400 bg-red-500/10 border-red-500/40';

  const ResultIcon =
    feasibility?.result === 'FEASIBLE'
      ? CheckCircle2
      : feasibility?.result === 'MARGINAL'
      ? AlertTriangle
      : XCircle;

  return (
    <div className="bg-[#0d1421] border border-slate-800/60 rounded p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
            <Target size={14} className="text-amber-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">MISSION FEASIBILITY EVALUATION</h3>
            <p className="text-[10px] text-slate-500">Autonomous safety & endurance check prior to target dispatch</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Context details */}
        <div className="bg-[#111827] border border-slate-800 p-3 rounded flex flex-col justify-between">
          <div className="flex flex-col gap-2">
            <div className="flex justify-between items-center text-xs border-b border-slate-800 pb-1">
              <span className="text-slate-400">Target Anomaly:</span>
              <span className="mono font-bold text-amber-400">{selectedAnomaly.id}</span>
            </div>
            <div className="flex justify-between items-center text-xs border-b border-slate-800 pb-1">
              <span className="text-slate-400">Assigned Drone:</span>
              <span className="mono font-bold text-cyan-400">{selectedDrone.id}</span>
            </div>
            <div className="flex justify-between items-center text-xs border-b border-slate-800 pb-1">
              <span className="text-slate-400">Distance to Target:</span>
              <span className="mono text-slate-200">4.2 km</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Current Battery:</span>
              <span className="mono font-bold text-slate-200">{selectedDrone.battery_percentage.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Result summary */}
        <div className={clsx('border rounded p-4 flex flex-col items-center justify-center gap-2 text-center', resultColor)}>
          <ResultIcon size={28} />
          <div className="text-lg font-bold tracking-widest uppercase">{feasibility ? feasibility.result : 'EVALUATING'}</div>
          <div className="text-[10px] text-slate-400 max-w-[200px]">
            {feasibility?.recommendation}
          </div>
        </div>
      </div>

      {/* Energy Math */}
      {feasibility && (
        <div className="grid grid-cols-3 gap-3 bg-[#111827] border border-slate-800 p-3 rounded">
          <div>
            <div className="text-[9px] text-slate-500 uppercase">Required Energy</div>
            <div className="mono text-sm font-bold text-slate-200">{feasibility.estimated_mission_energy}%</div>
          </div>
          <div>
            <div className="text-[9px] text-slate-500 uppercase">Usable Energy</div>
            <div className="mono text-sm font-bold text-cyan-400">{feasibility.available_usable_energy}%</div>
          </div>
          <div>
            <div className="text-[9px] text-slate-500 uppercase">Required Reserve</div>
            <div className="mono text-sm font-bold text-amber-400">{feasibility.required_return_reserve}%</div>
          </div>
        </div>
      )}
    </div>
  );
}
