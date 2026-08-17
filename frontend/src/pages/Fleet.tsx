import { useState } from 'react';
import { Cpu, Battery, Radio, Wifi, Zap, Activity, Navigation, Shield } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
import clsx from 'clsx';

export function Fleet() {
  const { drones, selectedDroneId, setSelectedDrone } = useAppStore();

  return (
    <div className="flex h-full w-full overflow-hidden bg-[#080c14]">
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-xl font-bold text-slate-100 tracking-wider">AERIAL FLEET COMMAND</h1>
            <p className="text-xs text-slate-500">Autonomous UAV status, endurance monitoring, and operational readiness</p>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-slate-400">Total Fleet: <span className="mono text-cyan-400 font-bold">{drones.length}</span></span>
            <span className="text-slate-400">Active: <span className="mono text-green-400 font-bold">{drones.filter(d => d.status === 'active').length}</span></span>
            <span className="text-slate-400">Charging: <span className="mono text-blue-400 font-bold">{drones.filter(d => d.status === 'charging').length}</span></span>
          </div>
        </div>

        {/* Grid of Drone Cards */}
        <div className="grid grid-cols-3 gap-4">
          {drones.map((drone) => {
            const isSelected = drone.id === selectedDroneId;
            const battColor =
              drone.battery_percentage > 50 ? 'text-green-400'
              : drone.battery_percentage > 20 ? 'text-amber-400' : 'text-red-400';

            return (
              <div
                key={drone.id}
                onClick={() => setSelectedDrone(drone.id)}
                className={clsx(
                  'bg-[#0d1421] border rounded p-4 flex flex-col gap-3 cursor-pointer transition-all hover:border-cyan-500/50',
                  isSelected ? 'border-cyan-500 bg-cyan-500/5 shadow-lg' : 'border-slate-800'
                )}
              >
                {/* Top header */}
                <div className="flex items-center justify-between border-b border-slate-800/60 pb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center font-bold mono text-cyan-400 text-xs">
                      {drone.id}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-200">{drone.name}</div>
                      <div className="text-[9px] text-slate-500">{drone.model}</div>
                    </div>
                  </div>
                  <span className={`badge badge-${drone.status}`}>{drone.status}</span>
                </div>

                {/* Battery & Flight Time */}
                <div className="grid grid-cols-2 gap-2 bg-[#111827] border border-slate-800 p-2.5 rounded">
                  <div>
                    <div className="text-[9px] text-slate-500 uppercase flex items-center gap-1">
                      <Battery size={10} /> Battery
                    </div>
                    <div className={clsx('mono text-base font-bold', battColor)}>
                      {drone.battery_percentage.toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-[9px] text-slate-500 uppercase flex items-center gap-1">
                      <Zap size={10} /> Endurance
                    </div>
                    <div className="mono text-base font-bold text-slate-200">
                      {drone.estimated_flight_time.toFixed(0)} <span className="text-[10px] text-slate-500">min</span>
                    </div>
                  </div>
                </div>

                {/* Telemetry quick metrics */}
                <div className="grid grid-cols-3 gap-1 text-[10px] text-slate-400">
                  <div className="bg-slate-900/60 p-1.5 rounded">
                    <span className="block text-[8px] text-slate-500">ALTITUDE</span>
                    <span className="mono text-slate-200">{drone.altitude.toFixed(0)} m</span>
                  </div>
                  <div className="bg-slate-900/60 p-1.5 rounded">
                    <span className="block text-[8px] text-slate-500">SPEED</span>
                    <span className="mono text-slate-200">{drone.airspeed.toFixed(1)} m/s</span>
                  </div>
                  <div className="bg-slate-900/60 p-1.5 rounded">
                    <span className="block text-[8px] text-slate-500">SIGNAL</span>
                    <span className="mono text-green-400">{drone.communication_quality}%</span>
                  </div>
                </div>

                {/* Assigned Mission */}
                <div className="text-[10px] text-slate-400 border-t border-slate-800/60 pt-2 flex justify-between">
                  <span>Current Mission:</span>
                  <span className="mono text-cyan-400">{drone.mission_id || 'NONE (UNASSIGNED)'}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Drone Telemetry drawer */}
      {selectedDroneId && <TelemetryPanel />}
    </div>
  );
}
