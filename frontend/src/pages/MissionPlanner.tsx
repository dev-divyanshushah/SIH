import { MissionFeasibilityPanel } from '@/components/mission/MissionFeasibilityPanel';
import { DroneSelector } from '@/components/mission/DroneSelector';
import { PathPlannerPanel } from '@/components/mission/PathPlannerPanel';
import { HandoverPanel } from '@/components/handover/HandoverPanel';
import { EnergyIntelligence } from '@/components/energy/EnergyIntelligence';

export function MissionPlanner() {
  return (
    <div className="flex flex-col h-full w-full overflow-y-auto bg-[#080c14] p-6 gap-6">
      <div className="border-b border-slate-800 pb-3">
        <h1 className="text-xl font-bold text-slate-100 tracking-wider">AI MISSION & ENERGY PLANNER</h1>
        <p className="text-xs text-slate-500">
          Autonomous safety verification, energy path optimization, & predictive handover coordination
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <MissionFeasibilityPanel />
        <DroneSelector />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <PathPlannerPanel />
        <HandoverPanel />
      </div>

      <EnergyIntelligence />
    </div>
  );
}
