import { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, ShieldAlert, Award } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import type { DroneCandidate } from '@/types';
import clsx from 'clsx';

export function DroneSelector() {
  const { setSelectedDrone } = useAppStore();
  const [candidates, setCandidates] = useState<DroneCandidate[]>([]);
  const [recommended, setRecommended] = useState<DroneCandidate | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.energy
      .selectDrone({
        target_lat: 28.6139 - 0.010,
        target_lon: 77.2090 + 0.008,
      })
      .then((res: any) => {
        setCandidates(res.candidates || []);
        setRecommended(res.recommended || null);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Drone selection error', err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-[#0d1421] border border-slate-800/60 rounded p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-green-500/10 border border-green-500/30 flex items-center justify-center">
            <Cpu size={14} className="text-green-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">INTELLIGENT FLEET SELECTION ENGINE</h3>
            <p className="text-[10px] text-slate-500">Multi-criteria decision matrix scoring available drones for assignment</p>
          </div>
        </div>
      </div>

      {/* Recommended banner */}
      {recommended && (
        <div className="bg-green-500/10 border border-green-500/30 rounded p-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Award size={20} className="text-green-400" />
            <div>
              <div className="text-xs font-bold text-green-400">RECOMMENDED SELECTION: {recommended.drone_id}</div>
              <div className="text-[10px] text-slate-400">
                Score: <span className="mono font-bold text-slate-200">{recommended.score}/100</span> — Sufficient energy reserve & lowest predicted mission completion time.
              </div>
            </div>
          </div>
          <button
            onClick={() => setSelectedDrone(recommended.drone_id)}
            className="btn-tactical success text-xs"
          >
            DISPATCH {recommended.drone_id}
          </button>
        </div>
      )}

      {/* Rankings Table */}
      <div className="bg-[#111827] border border-slate-800 rounded overflow-hidden">
        <div className="grid grid-cols-6 gap-2 px-3 py-2 bg-slate-900/60 border-b border-slate-800 text-[9px] font-bold text-slate-500 uppercase tracking-wider">
          <span>Drone ID</span>
          <span>Score</span>
          <span>Battery</span>
          <span>Distance</span>
          <span>Feasibility</span>
          <span className="text-right">Action</span>
        </div>

        <div className="divide-y divide-slate-800/60">
          {candidates.map((c) => (
            <div
              key={c.drone_id}
              className={clsx(
                'grid grid-cols-6 gap-2 px-3 py-2.5 items-center text-xs',
                c.drone_id === recommended?.drone_id ? 'bg-green-500/5' : 'hover:bg-slate-800/30'
              )}
            >
              <div className="font-bold text-slate-200 mono flex items-center gap-1.5">
                {c.drone_id}
                {c.drone_id === recommended?.drone_id && <span className="text-[9px] text-green-400">★</span>}
              </div>
              <div className="mono font-bold text-cyan-400">{c.score}</div>
              <div className="mono text-slate-300">{c.battery_percentage}%</div>
              <div className="mono text-slate-400">{c.distance_km} km</div>
              <div>
                <span
                  className={clsx(
                    'badge',
                    c.feasible ? 'badge-active' : 'badge-critical'
                  )}
                >
                  {c.feasible ? 'FEASIBLE' : 'INSUFFICIENT'}
                </span>
              </div>
              <div className="text-right">
                <button
                  onClick={() => setSelectedDrone(c.drone_id)}
                  className="btn-tactical text-[10px] py-1 px-2"
                >
                  SELECT
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
