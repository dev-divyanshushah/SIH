import { AlertTriangle, Radio, Shield, Battery, ChevronRight, Eye, Zap, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';
import clsx from 'clsx';
import type { IntelEvent, Anomaly } from '@/types';

const EVENT_ICONS: Record<string, React.ElementType> = {
  detection: Eye,
  anomaly: AlertTriangle,
  risk_assessment: Shield,
  feasibility_check: Battery,
  drone_selection: Radio,
  handover_initiated: Zap,
  handover_completed: CheckCircle,
  verification_requested: Clock,
  verification_confirmed: CheckCircle,
  verification_dismissed: XCircle,
  mission_started: Radio,
  mission_completed: CheckCircle,
  battery_warning: Battery,
  battery_critical: Battery,
  coverage_gap: AlertTriangle,
  system: Radio,
};

function EventItem({ event }: { event: IntelEvent }) {
  const Icon = EVENT_ICONS[event.event_type] || Radio;
  const ts = new Date(event.timestamp);
  const timeStr = ts.toTimeString().slice(0, 8);

  return (
    <div className={clsx('event-item animate-fade-in', event.risk_level)}>
      <div className="flex items-start gap-2">
        <Icon size={11} className={clsx(
          'mt-0.5 flex-shrink-0',
          event.risk_level === 'critical' ? 'text-red-400' :
          event.risk_level === 'high' ? 'text-orange-400' :
          event.risk_level === 'medium' ? 'text-amber-400' :
          'text-slate-400'
        )} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[11px] font-medium text-slate-200 truncate">{event.title}</span>
            {event.drone_id && (
              <span className="text-[9px] text-cyan-400 flex-shrink-0 mono">{event.drone_id}</span>
            )}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5 line-clamp-2">{event.description}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="mono text-[9px] text-slate-600">{timeStr}</span>
            {event.sector && <span className="text-[9px] text-slate-600">• Sector {event.sector}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

function AnomalyCard({ anomaly }: { anomaly: Anomaly }) {
  const handleVerify = async (action: 'confirm' | 'dismiss') => {
    await api.anomalies.verify(anomaly.id, action);
    toast.success(action === 'confirm' ? 'Anomaly confirmed — Mission action authorized' : 'Anomaly dismissed');
  };

  const riskColor = anomaly.risk_level === 'critical' ? '#ef4444'
    : anomaly.risk_level === 'high' ? '#f97316'
    : anomaly.risk_level === 'medium' ? '#f59e0b' : '#10b981';

  return (
    <div className="border border-slate-800 rounded-sm mb-2 overflow-hidden animate-fade-in">
      <div className="flex items-center justify-between px-3 py-2" style={{ borderLeft: `3px solid ${riskColor}` }}>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold text-slate-200">{anomaly.object_class.replace('_', ' ').toUpperCase()}</span>
            <span className={`badge badge-${anomaly.risk_level}`}>{anomaly.risk_level}</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            {anomaly.detected_by_drone_id} · Sector {anomaly.sector} · {(anomaly.confidence * 100).toFixed(1)}% conf.
          </div>
        </div>
        <div className="text-right">
          <div className="mono text-lg font-bold" style={{ color: riskColor }}>{anomaly.risk_score}</div>
          <div className="text-[8px] text-slate-600">/100</div>
        </div>
      </div>

      {anomaly.status === 'detected' && (
        <div className="flex gap-px border-t border-slate-800">
          <button
            onClick={() => handleVerify('confirm')}
            className="flex-1 py-1.5 text-[10px] font-medium text-green-400 hover:bg-green-500/10 transition-colors flex items-center justify-center gap-1"
          >
            <CheckCircle size={10} /> CONFIRM
          </button>
          <button
            onClick={() => handleVerify('dismiss')}
            className="flex-1 py-1.5 text-[10px] font-medium text-slate-500 hover:bg-slate-800 transition-colors flex items-center justify-center gap-1 border-l border-slate-800"
          >
            <XCircle size={10} /> DISMISS
          </button>
        </div>
      )}
      {anomaly.status !== 'detected' && (
        <div className={clsx(
          'px-3 py-1.5 text-[10px] text-center font-medium border-t border-slate-800',
          anomaly.status === 'verified' ? 'text-green-400' : 'text-slate-500'
        )}>
          {anomaly.status.toUpperCase().replace('_', ' ')}
        </div>
      )}
    </div>
  );
}

export function IntelligenceFeed() {
  const { events, anomalies } = useAppStore();
  const activeAnomalies = anomalies.filter(a => a.status === 'detected').slice(-5).reverse();
  const recentEvents = events.slice(0, 30);

  return (
    <div className="flex flex-col w-[280px] flex-shrink-0 border-l border-slate-800/60 bg-[#0d1421]">
      {/* Anomaly alerts */}
      <div className="panel-header">
        <AlertTriangle size={11} className="text-amber-400" />
        ACTIVE ANOMALIES
        {activeAnomalies.length > 0 && (
          <span className="ml-auto bg-red-500/20 text-red-400 border border-red-500/30 text-[9px] font-bold px-2 py-0.5 rounded">
            {activeAnomalies.length}
          </span>
        )}
      </div>
      <div className="px-2 py-2 border-b border-slate-800/60 min-h-[100px] max-h-[220px] overflow-y-auto">
        {activeAnomalies.length === 0 ? (
          <div className="flex items-center justify-center h-16 text-[11px] text-slate-600">
            No active anomalies
          </div>
        ) : (
          activeAnomalies.map(a => <AnomalyCard key={a.id} anomaly={a} />)
        )}
      </div>

      {/* Intelligence feed */}
      <div className="panel-header">
        <Radio size={11} className="text-cyan-400" />
        INTELLIGENCE FEED
      </div>
      <div className="flex-1 overflow-y-auto">
        {recentEvents.length === 0 ? (
          <div className="flex items-center justify-center h-20 text-[11px] text-slate-600">
            Awaiting events...
          </div>
        ) : (
          recentEvents.map(e => <EventItem key={e.id} event={e} />)
        )}
      </div>
    </div>
  );
}
