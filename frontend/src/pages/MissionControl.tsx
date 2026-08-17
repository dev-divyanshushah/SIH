import { KpiStrip } from '@/components/layout/KpiStrip';
import { MapView } from '@/components/map/MapView';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
import { IntelligenceFeed } from '@/components/ai/IntelligenceFeed';
import { useAppStore } from '@/store/appStore';

export function MissionControl() {
  const { selectedDroneId } = useAppStore();

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-[#080c14]">
      {/* Top KPI strip */}
      <KpiStrip />

      {/* Main Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Map Center */}
        <div className="flex-1 relative overflow-hidden">
          <MapView />
        </div>

        {/* Selected Drone Telemetry Panel */}
        {selectedDroneId && <TelemetryPanel />}

        {/* Right Intelligence Feed */}
        <IntelligenceFeed />
      </div>
    </div>
  );
}
