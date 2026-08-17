import { X, Battery, Wifi, Navigation, Wind, Thermometer, Zap, Activity, Target } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { useAppStore } from '@/store/appStore';
import clsx from 'clsx';

const STATUS_COLORS: Record<string, string> = {
  active: '#10b981', available: '#64748b', returning: '#f59e0b',
  charging: '#3b82f6', critical: '#ef4444', offline: '#475569',
};

function getBatteryColor(pct: number): string {
  if (pct > 50) return '#10b981';
  if (pct > 25) return '#f59e0b';
  if (pct > 12) return '#f97316';
  return '#ef4444';
}

function DataRow({ label, value, unit, accent }: {
  label: string; value: string | number; unit?: string; accent?: boolean;
}) {
  return (
    <div className="data-row">
      <span className="data-label">{label}</span>
      <span className={clsx('data-value', accent && 'text-cyan-400')}>
        {value}{unit && <span className="text-slate-500 ml-0.5 text-[10px]">{unit}</span>}
      </span>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#111827] border border-slate-700 rounded p-2 text-[10px]">
      <div className="text-slate-400 mb-1">t-{60 - Number(label)}s</div>
      {payload.map((p: any) => (
        <div key={p.name} style={{ color: p.color }}>{p.name}: {p.value?.toFixed(1)}{p.name === 'Battery' ? '%' : p.name === 'Speed' ? ' m/s' : 'm'}</div>
      ))}
    </div>
  );
};

export function TelemetryPanel() {
  const { getSelectedDrone, setSelectedDrone } = useAppStore();
  const drone = getSelectedDrone();

  if (!drone) return null;

  const color = STATUS_COLORS[drone.status];
  const battColor = getBatteryColor(drone.battery_percentage);

  // Build chart data from history arrays
  const chartData = drone.battery_history.slice(-60).map((b, i) => ({
    i,
    Battery: b,
    Speed: drone.speed_history[i] ?? 0,
    Altitude: drone.altitude_history[i] ?? 0,
  }));

  const flightTimeColor = drone.estimated_flight_time > 20 ? '#10b981'
    : drone.estimated_flight_time > 10 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col w-[300px] flex-shrink-0 bg-[#0d1421] border-l border-slate-800/60 animate-slide-in overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/60">
        <div className="flex items-center gap-2">
          <div className="status-dot" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
          <div>
            <div className="text-white font-bold text-sm">{drone.id}</div>
            <div className="text-slate-500 text-[9px] uppercase tracking-widest">{drone.name}</div>
          </div>
        </div>
        <button
          onClick={() => setSelectedDrone(null)}
          className="text-slate-500 hover:text-slate-300 transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      {/* Status badge */}
      <div className="px-4 py-2 border-b border-slate-800/60 flex items-center justify-between">
        <span className={`badge badge-${drone.status}`}>{drone.status}</span>
        {drone.mission_id && (
          <span className="flex items-center gap-1 text-[10px] text-cyan-400">
            <Target size={10} />
            {drone.mission_id}
          </span>
        )}
      </div>

      {/* Battery */}
      <div className="px-4 py-3 border-b border-slate-800/60">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 uppercase tracking-wider">
            <Battery size={11} /> Battery
          </div>
          <span className="mono text-lg font-bold" style={{ color: battColor }}>
            {drone.battery_percentage.toFixed(1)}%
          </span>
        </div>
        <div className="battery-bar">
          <div
            className="battery-fill"
            style={{ width: `${drone.battery_percentage}%`, background: battColor }}
          />
        </div>
        <div className="flex justify-between mt-1.5 text-[10px] text-slate-500">
          <span>{drone.battery_voltage.toFixed(2)}V</span>
          <span>{drone.current_consumption.toFixed(1)}A</span>
          <span>{drone.battery_temperature.toFixed(1)}°C</span>
        </div>
      </div>

      {/* Flight time */}
      <div className="px-4 py-3 border-b border-slate-800/60">
        <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-2">Endurance Estimate</div>
        <div className="grid grid-cols-3 gap-2">
          <div className="bg-slate-900/60 rounded p-2 text-center">
            <div className="text-[8px] text-slate-500 mb-1">Remaining</div>
            <div className="mono text-sm font-bold" style={{ color: flightTimeColor }}>
              {drone.estimated_flight_time.toFixed(0)}<span className="text-[9px] text-slate-500">m</span>
            </div>
          </div>
          <div className="bg-slate-900/60 rounded p-2 text-center">
            <div className="text-[8px] text-slate-500 mb-1">Safe Time</div>
            <div className="mono text-sm font-bold text-amber-400">
              {Math.max(0, drone.estimated_flight_time - 8).toFixed(0)}<span className="text-[9px] text-slate-500">m</span>
            </div>
          </div>
          <div className="bg-slate-900/60 rounded p-2 text-center">
            <div className="text-[8px] text-slate-500 mb-1">Reserve</div>
            <div className="mono text-sm font-bold text-blue-400">
              8<span className="text-[9px] text-slate-500">m</span>
            </div>
          </div>
        </div>
      </div>

      {/* Telemetry data */}
      <div className="px-4 py-2 border-b border-slate-800/60">
        <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-2">Telemetry</div>
        <DataRow label="Latitude" value={drone.latitude.toFixed(5)} />
        <DataRow label="Longitude" value={drone.longitude.toFixed(5)} />
        <DataRow label="Altitude" value={drone.altitude.toFixed(0)} unit="m" />
        <DataRow label="Airspeed" value={drone.airspeed.toFixed(1)} unit="m/s" />
        <DataRow label="Heading" value={drone.heading.toFixed(0)} unit="°" />
        <DataRow label="Distance from Base" value={(drone.distance_from_base / 1000).toFixed(2)} unit="km" />
      </div>

      {/* Comms & health */}
      <div className="px-4 py-2 border-b border-slate-800/60">
        <div className="flex gap-3">
          <div className="flex-1 bg-slate-900/60 rounded p-2">
            <div className="flex items-center gap-1 text-[8px] text-slate-500 mb-1"><Wifi size={9} /> Signal</div>
            <div className="mono text-sm font-bold" style={{ color: drone.communication_quality > 80 ? '#10b981' : '#f59e0b' }}>
              {drone.communication_quality}%
            </div>
          </div>
          <div className="flex-1 bg-slate-900/60 rounded p-2">
            <div className="flex items-center gap-1 text-[8px] text-slate-500 mb-1"><Activity size={9} /> Health</div>
            <div className="mono text-sm font-bold" style={{ color: drone.health_score > 80 ? '#10b981' : '#f59e0b' }}>
              {drone.health_score}%
            </div>
          </div>
        </div>
      </div>

      {/* Battery chart */}
      <div className="px-4 py-3">
        <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-2">Battery History</div>
        <ResponsiveContainer width="100%" height={80}>
          <LineChart data={chartData} margin={{ top: 2, right: 2, left: -20, bottom: 0 }}>
            <XAxis dataKey="i" hide />
            <YAxis domain={[0, 100]} tick={{ fontSize: 9, fill: '#475569' }} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={20} stroke="#ef4444" strokeDasharray="3 3" strokeOpacity={0.5} />
            <ReferenceLine y={8} stroke="#7f1d1d" strokeDasharray="3 3" strokeOpacity={0.5} />
            <Line type="monotone" dataKey="Battery" stroke={battColor} dot={false} strokeWidth={1.5} name="Battery" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
