import { Grid3X3, Shield, Zap, RefreshCw, Clock } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { MapView } from '@/components/map/MapView';

export function PersistentCoverage() {
  const { coveragePercentage, drones } = useAppStore();

  return (
    <div className="flex h-full w-full overflow-hidden bg-[#080c14]">
      {/* Left analytics & core message */}
      <div className="w-[420px] border-r border-slate-800 p-6 flex flex-col gap-6 overflow-y-auto bg-[#0d1421]">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-wider">PERSISTENT COVERAGE INTELLIGENCE</h1>
          <p className="text-xs text-slate-500">Overcoming drone endurance limits at the mission level</p>
        </div>

        {/* CORE STORYTELLING BANNER */}
        <div className="bg-cyan-500/10 border border-cyan-500/40 p-4 rounded flex flex-col gap-2">
          <div className="text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-1.5">
            <Zap size={14} /> PERSIST-AIR CORE CONCEPT
          </div>
          <p className="text-sm font-bold text-slate-100 italic">
            "INDIVIDUAL DRONE ENDURANCE ≠ MISSION ENDURANCE"
          </p>
          <p className="text-xs text-slate-300">
            While individual drones are constrained to 35-minute battery lifespans, PERSIST-AIR coordinates predictive rotative handovers to deliver <span className="text-green-400 font-bold">10+ hours of continuous uninterrupted aerial coverage</span>.
          </p>
        </div>

        {/* Coverage KPIs */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-[#111827] border border-slate-800 p-3 rounded text-center">
            <div className="text-[9px] text-slate-500 uppercase">Coverage Percentage</div>
            <div className="mono text-2xl font-bold text-green-400">{coveragePercentage.toFixed(1)}%</div>
          </div>
          <div className="bg-[#111827] border border-slate-800 p-3 rounded text-center">
            <div className="text-[9px] text-slate-500 uppercase">Uncovered Area</div>
            <div className="mono text-2xl font-bold text-slate-400">{(100 - coveragePercentage).toFixed(1)}%</div>
          </div>
          <div className="bg-[#111827] border border-slate-800 p-3 rounded text-center">
            <div className="text-[9px] text-slate-500 uppercase">Mission Continuity</div>
            <div className="mono text-2xl font-bold text-cyan-400">99.1%</div>
          </div>
          <div className="bg-[#111827] border border-slate-800 p-3 rounded text-center">
            <div className="text-[9px] text-slate-500 uppercase">Mission Duration</div>
            <div className="mono text-2xl font-bold text-amber-400">10h 00m</div>
          </div>
        </div>

        {/* Sector Assignment */}
        <div className="flex flex-col gap-2">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Sector Coverage Assignment</h3>
          <div className="flex flex-col gap-2 text-xs">
            <div className="bg-[#111827] border border-slate-800 p-2.5 rounded flex justify-between items-center">
              <span>Sector A (North Perimeter)</span>
              <span className="mono text-green-400 font-bold">PA-01 (98.2%)</span>
            </div>
            <div className="bg-[#111827] border border-slate-800 p-2.5 rounded flex justify-between items-center">
              <span>Sector B (South Boundary)</span>
              <span className="mono text-amber-400 font-bold">PA-02 → PA-04 (Handover)</span>
            </div>
            <div className="bg-[#111827] border border-slate-800 p-2.5 rounded flex justify-between items-center">
              <span>Sector C (West Quadrant)</span>
              <span className="mono text-cyan-400 font-bold">PA-05 (95.4%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Map */}
      <div className="flex-1 h-full relative">
        <MapView />
      </div>
    </div>
  );
}
