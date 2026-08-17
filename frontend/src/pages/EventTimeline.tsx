import { useState } from 'react';
import { Clock, Shield, AlertTriangle, Radio, Filter } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import clsx from 'clsx';

export function EventTimeline() {
  const { events } = useAppStore();
  const [filter, setFilter] = useState<string>('all');

  const filteredEvents = events.filter((e) => {
    if (filter === 'all') return true;
    if (filter === 'critical') return e.risk_level === 'critical';
    if (filter === 'handover') return e.event_type.includes('handover');
    if (filter === 'detection') return e.event_type === 'detection' || e.event_type === 'anomaly';
    return true;
  });

  return (
    <div className="flex flex-col h-full w-full bg-[#080c14] p-6 gap-6 overflow-y-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-wider">INTELLIGENCE EVENT TIMELINE</h1>
          <p className="text-xs text-slate-500">Audit trail of autonomous detections, feasibility checks, handovers, & verifications</p>
        </div>

        {/* Filter buttons */}
        <div className="flex gap-2">
          {['all', 'critical', 'handover', 'detection'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={clsx(
                'btn-tactical text-xs uppercase',
                filter === f && 'active'
              )}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline List */}
      <div className="flex flex-col gap-3 max-w-4xl">
        {filteredEvents.map((evt) => (
          <div
            key={evt.id}
            className={clsx(
              'bg-[#0d1421] border border-slate-800 p-4 rounded flex items-start gap-4 hover:border-slate-700 transition-all',
              evt.risk_level === 'critical' && 'border-l-4 border-l-red-500',
              evt.risk_level === 'high' && 'border-l-4 border-l-orange-500'
            )}
          >
            <div className="mono text-xs text-cyan-400 font-bold w-20 flex-shrink-0">
              {new Date(evt.timestamp).toLocaleTimeString()}
            </div>

            <div className="flex-1 flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-200">{evt.title}</span>
                {evt.drone_id && <span className="mono text-xs text-slate-400">({evt.drone_id})</span>}
                {evt.risk_level && <span className={`badge badge-${evt.risk_level}`}>{evt.risk_level}</span>}
              </div>
              <p className="text-xs text-slate-400">{evt.description}</p>
              {evt.sector && <div className="text-[10px] text-slate-500">Sector {evt.sector}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
