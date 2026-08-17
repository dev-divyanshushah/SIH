import { useState } from 'react';
import { Settings as SettingsIcon, Shield, Globe, Cpu, Link, Server } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/services/api';
import type { OperationalMode } from '@/types';
import { toast } from 'sonner';
import clsx from 'clsx';

export function Settings() {
  const { operationalMode, setOperationalMode } = useAppStore();

  const handleModeChange = async (mode: OperationalMode) => {
    try {
      await api.system.setMode(mode);
      setOperationalMode(mode);
      toast.success(`Operational Mode switched to ${mode.toUpperCase()}`);
    } catch (e) {
      toast.error('Failed to change operational mode');
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-[#080c14] p-6 gap-6 overflow-y-auto">
      <div className="border-b border-slate-800 pb-3">
        <h1 className="text-xl font-bold text-slate-100 tracking-wider">SYSTEM SETTINGS & INTEGRATIONS</h1>
        <p className="text-xs text-slate-500">Operational mode selection, backend API, & ML model endpoint adapters</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Operational Mode Selection */}
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded flex flex-col gap-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
            <Shield size={16} className="text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">OPERATIONAL MISSION MODE</h3>
          </div>

          <p className="text-xs text-slate-400">
            Selecting an operational mode adjusts AI object detection models, anomaly risk weightings, map overlays, and scenario prioritizations.
          </p>

          <div className="flex flex-col gap-3">
            {[
              { id: 'security', label: 'SECURITY MODE', desc: 'Perimeter defense, vehicle tracking, unauthorized intrusion, abandoned objects.' },
              { id: 'humanitarian', label: 'HUMANITARIAN MODE', desc: 'Disaster response, stranded person identification, active fire/flood mapping.' },
              { id: 'environmental', label: 'ENVIRONMENTAL MODE', desc: 'Deforestation monitoring, water body analysis, illegal logging/dumping.' },
            ].map((m) => (
              <div
                key={m.id}
                onClick={() => handleModeChange(m.id as OperationalMode)}
                className={clsx(
                  'border rounded p-3 cursor-pointer flex flex-col gap-1 transition-all',
                  operationalMode === m.id
                    ? 'border-cyan-500 bg-cyan-500/10'
                    : 'border-slate-800 hover:border-slate-700'
                )}
              >
                <div className="flex justify-between items-center text-xs font-bold text-slate-200">
                  <span>{m.label}</span>
                  {operationalMode === m.id && <span className="badge badge-active">ACTIVE</span>}
                </div>
                <span className="text-[11px] text-slate-400">{m.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* External ML Service Integration Architecture */}
        <div className="bg-[#0d1421] border border-slate-800 p-4 rounded flex flex-col gap-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
            <Server size={16} className="text-green-400" />
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">ML MODEL SERVICE ARCHITECTURE</h3>
          </div>

          <p className="text-xs text-slate-400">
            PERSIST-AIR isolates model inference behind a clean backend API adapter. Connect trained models by pointing to your deployed ML service endpoints.
          </p>

          <div className="flex flex-col gap-3 text-xs">
            <div className="bg-[#111827] border border-slate-800 p-3 rounded flex justify-between items-center">
              <div>
                <div className="font-bold text-slate-200">ML_SERVICE_URL</div>
                <div className="text-[10px] text-slate-500">Target inference backend host</div>
              </div>
              <span className="mono text-cyan-400">http://localhost:8001</span>
            </div>

            <div className="bg-[#111827] border border-slate-800 p-3 rounded flex flex-col gap-1">
              <span className="font-bold text-slate-200">Adapter Status</span>
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>Object Detector:</span>
                <span className="text-green-400 font-mono">Mock (YOLOv8 Adapter Ready)</span>
              </div>
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>Behaviour Analyser:</span>
                <span className="text-green-400 font-mono">Mock (LSTM Adapter Ready)</span>
              </div>
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>Endurance Predictor:</span>
                <span className="text-green-400 font-mono">Mock (Physics Physics-ML Adapter Ready)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
