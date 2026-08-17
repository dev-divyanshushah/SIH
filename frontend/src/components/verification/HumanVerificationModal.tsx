import { CheckCircle2, XCircle, ShieldAlert, Eye, UserCheck } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import { toast } from 'sonner';
import clsx from 'clsx';
import type { Anomaly } from '@/types';

interface HumanVerificationProps {
  anomaly?: Anomaly | null;
  onClose?: () => void;
}

export function HumanVerificationModal({ anomaly, onClose }: HumanVerificationProps) {
  const { anomalies } = useAppStore();
  const target = anomaly || anomalies.find((a) => a.status === 'detected') || anomalies[0];

  if (!target) return null;

  const handleAction = async (action: 'confirm' | 'dismiss') => {
    try {
      await api.anomalies.verify(target.id, action);
      toast.success(action === 'confirm' ? 'Anomaly Confirmed by Operator' : 'Anomaly Dismissed');
      if (onClose) onClose();
    } catch (e) {
      toast.error('Failed to update verification state');
    }
  };

  return (
    <div className="bg-[#0d1421] border border-slate-800/80 rounded p-4 flex flex-col gap-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-red-500/10 border border-red-500/30 flex items-center justify-center">
            <UserCheck size={14} className="text-red-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">HUMAN-IN-THE-LOOP VERIFICATION</h3>
            <p className="text-[10px] text-slate-500">Operator authorization required for high risk detections</p>
          </div>
        </div>
        <span className={`badge badge-${target.risk_level}`}>{target.risk_level} RISK</span>
      </div>

      {/* Workflow Indicator */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#111827] border border-slate-800 rounded text-[10px] text-slate-400">
        <span className="text-cyan-400">AI DETECTED</span>
        <span>→</span>
        <span className="text-amber-400">RISK SCORING</span>
        <span>→</span>
        <span className="text-red-400 font-bold underline">HUMAN VERIFICATION</span>
        <span>→</span>
        <span className="text-slate-500">ACTION</span>
      </div>

      {/* Details */}
      <div className="bg-[#111827] border border-slate-800 p-3 rounded flex flex-col gap-2 text-xs">
        <div className="flex justify-between">
          <span className="text-slate-400">Object Classification:</span>
          <span className="mono font-bold text-slate-200 uppercase">{target.object_class.replace('_', ' ')}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Detection Confidence:</span>
          <span className="mono text-cyan-400 font-bold">{(target.confidence * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Computed Risk Score:</span>
          <span className="mono text-red-400 font-bold">{target.risk_score} / 100</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Detecting Unit:</span>
          <span className="mono text-slate-300">{target.detected_by_drone_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Sector:</span>
          <span className="mono text-slate-300">Sector {target.sector}</span>
        </div>
        <div className="pt-2 border-t border-slate-800 text-slate-300 text-[11px]">
          <span className="text-slate-500 block mb-0.5">Observed Behaviour:</span>
          {target.behaviour_description || target.description}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3 pt-2">
        <button
          onClick={() => handleAction('confirm')}
          className="btn-tactical success justify-center py-2 text-xs font-bold text-green-400 border-green-500/40 bg-green-500/10 hover:bg-green-500/20"
        >
          <CheckCircle2 size={14} /> CONFIRM ANOMALY
        </button>
        <button
          onClick={() => handleAction('dismiss')}
          className="btn-tactical danger justify-center py-2 text-xs font-bold text-red-400 border-red-500/40 bg-red-500/10 hover:bg-red-500/20"
        >
          <XCircle size={14} /> DISMISS (FALSE POSITIVE)
        </button>
      </div>
    </div>
  );
}
