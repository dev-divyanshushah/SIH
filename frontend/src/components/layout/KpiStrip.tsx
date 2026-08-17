import { Cpu, Battery, Shield, Activity, Clock, Zap, Target, Radio } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import clsx from 'clsx';

interface KpiCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  unit?: string;
  accent?: 'cyan' | 'green' | 'amber' | 'red' | 'blue';
  alert?: boolean;
}

function KpiCard({ icon: Icon, label, value, unit, accent = 'cyan', alert }: KpiCardProps) {
  const accentColor = {
    cyan: 'text-cyan-400',
    green: 'text-green-400',
    amber: 'text-amber-400',
    red: 'text-red-400',
    blue: 'text-blue-400',
  }[accent];

  return (
    <div className={clsx('kpi-card flex items-center gap-3', alert && 'border-red-500/30 bg-red-950/20')}>
      <div className={clsx('w-8 h-8 rounded flex items-center justify-center flex-shrink-0', `bg-${accent === 'cyan' ? 'cyan' : accent === 'green' ? 'green' : accent === 'amber' ? 'amber' : accent === 'red' ? 'red' : 'blue'}-500/10`)}>
        <Icon size={14} className={accentColor} />
      </div>
      <div>
        <div className="text-[9px] text-slate-500 uppercase tracking-wider">{label}</div>
        <div className={clsx('mono text-base font-bold', accentColor, alert && 'animate-pulse-red')}>
          {value}{unit && <span className="text-[10px] text-slate-500 ml-0.5">{unit}</span>}
        </div>
      </div>
    </div>
  );
}

export function KpiStrip() {
  const { drones, anomalies, coveragePercentage, missions } = useAppStore();

  const active = drones.filter(d => d.status === 'active').length;
  const available = drones.filter(d => d.status === 'available').length;
  const charging = drones.filter(d => d.status === 'charging').length;
  const criticalEvents = anomalies.filter(a => a.risk_level === 'critical' && a.status === 'detected').length;
  const avgBattery = drones.length > 0
    ? drones.reduce((s, d) => s + d.battery_percentage, 0) / drones.length
    : 0;
  const activeMissions = missions.filter(m => m.status === 'active').length;
  const avgEndurance = drones.filter(d => d.status === 'active').length > 0
    ? drones.filter(d => d.status === 'active').reduce((s, d) => s + d.estimated_flight_time, 0) /
      drones.filter(d => d.status === 'active').length
    : 0;

  return (
    <div className="grid grid-cols-8 gap-2 px-4 py-2 border-b border-slate-800/60 bg-[#080c14]">
      <KpiCard icon={Cpu} label="Active Drones" value={active} accent="cyan" />
      <KpiCard icon={Radio} label="Available" value={available} accent="green" />
      <KpiCard icon={Zap} label="Charging" value={charging} accent="blue" />
      <KpiCard icon={Shield} label="Coverage" value={coveragePercentage.toFixed(1)} unit="%" accent="green" />
      <KpiCard icon={Activity} label="Critical Events" value={criticalEvents} accent={criticalEvents > 0 ? 'red' : 'cyan'} alert={criticalEvents > 0} />
      <KpiCard icon={Battery} label="Avg Battery" value={avgBattery.toFixed(0)} unit="%" accent={avgBattery > 40 ? 'green' : avgBattery > 20 ? 'amber' : 'red'} />
      <KpiCard icon={Clock} label="Avg Endurance" value={avgEndurance.toFixed(0)} unit="min" accent="amber" />
      <KpiCard icon={Target} label="Active Missions" value={activeMissions} accent="cyan" />
    </div>
  );
}
