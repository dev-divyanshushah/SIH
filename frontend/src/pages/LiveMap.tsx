import { MapView } from '@/components/map/MapView';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
import { useAppStore } from '@/store/appStore';
import { Layers, Shield, Radio } from 'lucide-react';

export function LiveMap() {
  const { selectedDroneId, drones, coveragePercentage } = useAppStore();

  return (
    <div className="flex h-full w-full overflow-hidden relative bg-[#080c14]">
      {/* Full screen Map */}
      <div className="flex-1 h-full w-full relative">
        <MapView />

        {/* Floating tactical overlay */}
        <div className="absolute top-4 left-4 z-[1000] bg-[#0d1421]/90 border border-slate-800 p-3 rounded backdrop-blur text-xs flex flex-col gap-2">
          <div className="flex items-center gap-2 font-bold text-slate-100 border-b border-slate-800 pb-1">
            <Layers size={14} className="text-cyan-400" /> FULL GEOSPATIAL COMMAND MAP
          </div>
          <div className="flex justify-between gap-4 text-[11px] text-slate-400">
            <span>Surveillance Coverage:</span>
            <span className="mono font-bold text-green-400">{coveragePercentage.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between gap-4 text-[11px] text-slate-400">
            <span>Units Deployed:</span>
            <span className="mono font-bold text-cyan-400">{drones.filter(d => d.status === 'active').length} / {drones.length}</span>
          </div>
        </div>
      </div>

      {/* Telemetry panel on side if drone selected */}
      {selectedDroneId && <TelemetryPanel />}
    </div>
  );
}
