import { BarChart2, Shield, Battery, Zap, Clock, TrendingUp } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area
} from 'recharts';

const EFFICIENCY_DATA = [
  { time: '14:00', coverage: 98.2, energySaved: 6.5, handovers: 0 },
  { time: '14:15', coverage: 97.9, energySaved: 7.2, handovers: 1 },
  { time: '14:30', coverage: 98.5, energySaved: 7.0, handovers: 1 },
  { time: '14:45', coverage: 96.8, energySaved: 8.1, handovers: 2 },
  { time: '15:00', coverage: 98.7, energySaved: 7.8, handovers: 2 },
];

export function Analytics() {
  return (
    <div className="flex flex-col h-full w-full bg-[#080c14] p-6 gap-6 overflow-y-auto">
      <div className="border-b border-slate-800 pb-3">
        <h1 className="text-xl font-bold text-slate-100 tracking-wider">SYSTEM PERFORMANCE ANALYTICS</h1>
        <p className="text-xs text-slate-500">Fleet battery efficiency, mission continuity scores, & energy savings</p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded text-center">
          <div className="text-xs text-slate-500 uppercase">Mission Success Rate</div>
          <div className="mono text-2xl font-bold text-green-400 mt-1">99.4%</div>
        </div>
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded text-center">
          <div className="text-xs text-slate-500 uppercase">Energy Saved (Path Optimization)</div>
          <div className="mono text-2xl font-bold text-cyan-400 mt-1">7.4%</div>
        </div>
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded text-center">
          <div className="text-xs text-slate-500 uppercase">Successful Handovers</div>
          <div className="mono text-2xl font-bold text-amber-400 mt-1">14</div>
        </div>
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded text-center">
          <div className="text-xs text-slate-500 uppercase">Avg Response Time</div>
          <div className="mono text-2xl font-bold text-slate-100 mt-1">4.2s</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-2 gap-6">
        {/* Coverage Continuity */}
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded flex flex-col gap-3">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Coverage Continuity Over Time</h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={EFFICIENCY_DATA}>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis domain={[90, 100]} stroke="#64748b" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ background: '#0d1421', borderColor: '#334155' }} />
                <Area type="monotone" dataKey="coverage" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Energy Optimization Savings */}
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded flex flex-col gap-3">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Cumulative Energy Saved (%)</h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={EFFICIENCY_DATA}>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ background: '#0d1421', borderColor: '#334155' }} />
                <Bar dataKey="energySaved" fill="#06b6d4" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
