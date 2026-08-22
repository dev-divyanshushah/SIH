import { MapView } from '@/components/map/MapView';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
import { useAppStore } from '@/store/appStore';
import { Layers, Shield, Radio } from 'lucide-react';

export function LiveMap() {
  const { selectedDroneId, drones, coveragePercentage } = useAppStore();

  return (
    <div className="flex h-full w-full overflow-hidden relative bg-[#080c14]">
      <div className="flex-1 h-full w-full relative">
        <MapView cleanMode={true} />
      </div>

      {/* Telemetry panel on side if drone selected */}
      {selectedDroneId && <TelemetryPanel />}
    </div>
  );
}
