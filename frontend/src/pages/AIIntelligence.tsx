import { useState } from 'react';
import { Brain, Eye, ShieldAlert, CheckCircle2, XCircle, AlertTriangle, UserCheck } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { HumanVerificationModal } from '@/components/verification/HumanVerificationModal';
import type { Anomaly } from '@/types';
import clsx from 'clsx';

export function AIIntelligence() {
  const { anomalies } = useAppStore();
  const [selectedAnomalyId, setSelectedAnomalyId] = useState<string | null>(null);

  const activeAnomalies = anomalies.filter(a => a.status === 'detected');
  const verifiedAnomalies = anomalies.filter(a => a.status === 'verified');
  const dismissedAnomalies = anomalies.filter(a => a.status === 'dismissed');

  const selectedAnomaly = anomalies.find(a => a.id === selectedAnomalyId) || null;

  return (
    <div className="flex h-full w-full overflow-hidden bg-[#080c14] p-6 gap-6">
      {/* Left Column: Detections & Anomalies List */}
      <div className="flex-1 flex flex-col gap-4 overflow-y-auto">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h1 className="text-xl font-bold text-slate-100 tracking-wider">AI OBJECT & BEHAVIOURAL INTELLIGENCE</h1>
            <p className="text-xs text-slate-500">Real-time computer vision inference & temporal pattern anomaly detection</p>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-critical">{activeAnomalies.length} UNVERIFIED</span>
            <span className="badge badge-active">{verifiedAnomalies.length} CONFIRMED</span>
          </div>
        </div>

        {/* Anomaly list */}
        <div className="flex flex-col gap-3">
          {anomalies.length === 0 ? (
            <div className="p-8 text-center text-slate-600 text-sm">No AI detections logged yet.</div>
          ) : (
            [...anomalies].sort((a, b) => b.risk_score - a.risk_score).map((item) => {
              const riskColor =
                item.risk_level === 'critical' ? 'border-red-500/50 bg-red-500/5'
                : item.risk_level === 'high' ? 'border-orange-500/50 bg-orange-500/5'
                : 'border-amber-500/50 bg-amber-500/5';

              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedAnomalyId(item.id)}
                  className={clsx(
                    'bg-[#0d1421] border rounded p-4 flex justify-between items-start cursor-pointer hover:border-cyan-500/50 transition-all',
                    riskColor,
                    selectedAnomaly?.id === item.id && 'ring-1 ring-cyan-500'
                  )}
                >
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <span className="mono text-xs font-bold text-slate-400">{item.id}</span>
                      <span className="text-sm font-bold text-slate-100 uppercase">{item.object_class.replace('_', ' ')}</span>
                      <span className={`badge badge-${item.risk_level}`}>{item.risk_level}</span>
                      <span className="text-[10px] text-cyan-400 font-medium">({(item.confidence * 100).toFixed(1)}% confidence)</span>
                    </div>

                    <p className="text-xs text-slate-300 mt-1">{item.description}</p>
                    {item.behaviour_description && (
                      <p className="text-[11px] text-amber-400/90 font-mono mt-0.5">
                        Observed: {item.behaviour_description}
                      </p>
                    )}

                    <div className="text-[10px] text-slate-500 flex gap-4 mt-2">
                      <span>Unit: <strong className="text-slate-300">{item.detected_by_drone_id}</strong></span>
                      <span>Sector: <strong className="text-slate-300">Sector {item.sector}</strong></span>
                      <span>Time: <strong className="text-slate-300">{new Date(item.detected_at).toLocaleTimeString()}</strong></span>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    <div className="text-right">
                      <div className="mono text-2xl font-bold text-red-400">{item.risk_score}</div>
                      <div className="text-[9px] text-slate-500">RISK SCORE</div>
                    </div>
                    <span className={clsx(
                      'text-[10px] font-bold px-2 py-0.5 rounded border uppercase',
                      item.status === 'detected' ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' :
                      item.status === 'verified' ? 'text-green-400 border-green-500/30 bg-green-500/10' :
                      'text-slate-500 border-slate-700 bg-slate-800'
                    )}>
                      {item.status}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Right Column: Selected Anomaly Detail & Human Verification Modal */}
      <div className="w-[380px] flex flex-col gap-4 overflow-y-auto">
        <HumanVerificationModal anomaly={selectedAnomaly} onClose={() => setSelectedAnomalyId(null)} />

        {/* Explainable Risk Breakdown */}
        {selectedAnomaly && (
          <div className="bg-[#0d1421] border border-slate-800 p-4 rounded flex flex-col gap-3">
            <h3 className="text-xs font-bold text-slate-200 border-b border-slate-800 pb-2 uppercase tracking-wider">
              TRANSPARENT RISK BREAKDOWN MODEL
            </h3>

            <div className="flex flex-col gap-2 text-xs">
              {Object.entries(selectedAnomaly.risk_breakdown || {}).map(([key, val]) => (
                <div key={key} className="flex justify-between items-center bg-[#111827] px-3 py-1.5 rounded">
                  <span className="text-slate-400 capitalize">{key.replace('_', ' ')}</span>
                  <span className="mono font-bold text-cyan-400">+{val}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
