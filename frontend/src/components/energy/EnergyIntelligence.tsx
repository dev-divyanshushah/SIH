import { useState, useEffect } from 'react';
import { Battery, Zap, ShieldAlert, Clock, Activity, ArrowRight } from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Line, ComposedChart
} from 'recharts';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import type { EnergyPrediction } from '@/types';
import clsx from 'clsx';

export function EnergyIntelligence() {
  const { drones, selectedDroneId } = useAppStore();
  const activeDrones = drones.filter((d) => d.status === 'active' || d.status === 'returning');
  const selectedDrone = drones.find((d) => d.id === selectedDroneId) || activeDrones[0] || drones[0];

  const [prediction, setPrediction] = useState<EnergyPrediction | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedDrone) return;
    setLoading(true);
    api.energy
      .predict({
        drone_id: selectedDrone.id,
        battery_percentage: selectedDrone.battery_percentage,
        battery_voltage: selectedDrone.battery_voltage,
        current_consumption: selectedDrone.current_consumption,
        temperature: selectedDrone.battery_temperature,
        airspeed: selectedDrone.airspeed,
        altitude: selectedDrone.altitude,
        distance_from_base: selectedDrone.distance_from_base,
      })
      .then((res: any) => {
        setPrediction(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Energy prediction error', err);
        setLoading(false);
      });
  }, [selectedDrone?.id, selectedDrone?.battery_percentage]);

  if (!selectedDrone) {
    return <div className="p-4 text-slate-500 text-xs">No drone available for telemetry.</div>;
  }

  const riskColor =
    prediction?.energy_risk === 'critical'
      ? 'text-red-400 bg-red-500/10 border-red-500/30'
      : prediction?.energy_risk === 'high'
      ? 'text-orange-400 bg-orange-500/10 border-orange-500/30'
      : prediction?.energy_risk === 'medium'
      ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
      : 'text-green-400 bg-green-500/10 border-green-500/30';

  return (
    <div className="bg-[#0d1421] border border-slate-800/60 rounded p-4 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <Zap size={14} className="text-cyan-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">ENERGY INTELLIGENCE & ENDURANCE PREDICTION</h3>
            <p className="text-[10px] text-slate-500">Real-time battery degradation & mission window forecasting</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-slate-400">Target:</span>
          <span className="mono text-xs font-bold text-cyan-400">{selectedDrone.id}</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-5 gap-3">
        <div className="bg-[#111827] border border-slate-800 p-3 rounded">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Battery size={10} /> Current Battery
          </div>
          <div className="mono text-xl font-bold text-slate-100">
            {selectedDrone.battery_percentage.toFixed(1)}
            <span className="text-xs text-slate-500">%</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 p-3 rounded">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Clock size={10} /> Remaining Endurance
          </div>
          <div className="mono text-xl font-bold text-cyan-400">
            {prediction ? prediction.remaining_endurance_minutes.toFixed(0) : '--'}
            <span className="text-xs text-slate-500"> min</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 p-3 rounded">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
            <ShieldAlert size={10} /> Safe Mission Time
          </div>
          <div className="mono text-xl font-bold text-green-400">
            {prediction ? prediction.safe_mission_time.toFixed(0) : '--'}
            <span className="text-xs text-slate-500"> min</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 p-3 rounded">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
            <ArrowRight size={10} /> Return Reserve
          </div>
          <div className="mono text-xl font-bold text-amber-400">
            {prediction ? prediction.return_reserve_minutes.toFixed(0) : '--'}
            <span className="text-xs text-slate-500"> min</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 p-3 rounded flex flex-col justify-between">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Activity size={10} /> Energy Risk
          </div>
          <div className={clsx('text-xs font-bold px-2 py-1 rounded border text-center uppercase tracking-wider', riskColor)}>
            {prediction ? prediction.energy_risk : 'COMPUTING'}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-[#111827] border border-slate-800 p-3 rounded flex flex-col gap-2">
        <div className="flex items-center justify-between text-[11px]">
          <span className="text-slate-400 font-medium">Predicted Battery Depletion Curve (Next 40 Minutes)</span>
          <span className="text-slate-500 text-[10px]">
            Model Confidence: <span className="text-cyan-400 mono">{(prediction?.confidence ?? 0.95) * 100}%</span>
          </span>
        </div>

        <div className="h-48 w-full mt-2">
          {prediction && (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={prediction.predicted_battery_curve} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <defs>
                  <linearGradient id="batteryGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="t" tick={{ fill: '#64748b', fontSize: 10 }} unit="m" />
                <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} unit="%" />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    return (
                      <div className="bg-[#0d1421] border border-slate-700 p-2 rounded text-xs">
                        <div className="text-slate-400">Time: +{payload[0].payload.t} min</div>
                        <div className="text-cyan-400 font-bold">Predicted Battery: {payload[0].value}%</div>
                      </div>
                    );
                  }}
                />
                <ReferenceLine y={20} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Return Reserve Threshold (20%)', fill: '#f59e0b', fontSize: 10 }} />
                <ReferenceLine y={8} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Critical Cutoff (8%)', fill: '#ef4444', fontSize: 10 }} />
                <Area type="monotone" dataKey="pct" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#batteryGrad)" name="Battery %" />
              </ComposedChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
