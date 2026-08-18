import { create } from 'zustand';
import type {
  Drone, Anomaly, IntelEvent, Mission, ActiveHandover,
  OperationalMode, SimulationState,
} from '@/types';

interface AppState {
  // Live telemetry
  drones: Drone[];
  anomalies: Anomaly[];
  events: IntelEvent[];
  missions: Mission[];
  coveragePercentage: number;
  coverageMetrics: { overall: number; redundant: number; single: number; gaps: number; status: string };
  activeHandover: ActiveHandover | null;
  tick: number;

  // UI state
  selectedDroneId: string | null;
  selectedAnomalyId: string | null;
  operationalMode: OperationalMode;
  wsConnected: boolean;
  lastUpdate: string | null;

  // Simulation state
  simulationRunning: boolean;
  speedMultiplier: number;
  demoMode: boolean;

  // Setters
  setDrones: (drones: Drone[]) => void;
  setAnomalies: (anomalies: Anomaly[]) => void;
  setEvents: (events: IntelEvent[]) => void;
  setMissions: (missions: Mission[]) => void;
  setCoverage: (pct: number) => void;
  setCoverageMetrics: (m: { overall: number; redundant: number; single: number; gaps: number; status: string }) => void;
  setActiveHandover: (h: ActiveHandover | null) => void;
  setTick: (t: number) => void;
  setSelectedDrone: (id: string | null) => void;
  setSelectedAnomaly: (id: string | null) => void;
  setOperationalMode: (mode: OperationalMode) => void;
  setWsConnected: (v: boolean) => void;
  setLastUpdate: (ts: string) => void;
  setSimulationRunning: (v: boolean) => void;
  setSpeedMultiplier: (v: number) => void;
  setDemoMode: (v: boolean) => void;

  // Computed helpers
  getSelectedDrone: () => Drone | undefined;
  getActiveDrones: () => Drone[];
  getCriticalAnomalies: () => Anomaly[];
}

export const useAppStore = create<AppState>((set, get) => ({
  drones: [],
  anomalies: [],
  events: [],
  missions: [],
  coveragePercentage: 97.8,
  coverageMetrics: { overall: 97.8, redundant: 70.0, single: 27.8, gaps: 0, status: "STABLE" },
  activeHandover: null,
  tick: 0,

  selectedDroneId: null,
  selectedAnomalyId: null,
  operationalMode: 'security',
  wsConnected: false,
  lastUpdate: null,

  simulationRunning: false,
  speedMultiplier: 1,
  demoMode: false,

  setDrones: (drones) => set({ drones }),
  setAnomalies: (anomalies) => set({ anomalies }),
  setEvents: (events) => set({ events }),
  setMissions: (missions) => set({ missions }),
  setCoverage: (coveragePercentage) => set({ coveragePercentage }),
  setCoverageMetrics: (coverageMetrics) => set({ coverageMetrics }),
  setActiveHandover: (activeHandover) => set({ activeHandover }),
  setTick: (tick) => set({ tick }),
  setSelectedDrone: (selectedDroneId) => set({ selectedDroneId }),
  setSelectedAnomaly: (selectedAnomalyId) => set({ selectedAnomalyId }),
  setOperationalMode: (operationalMode) => set({ operationalMode }),
  setWsConnected: (wsConnected) => set({ wsConnected }),
  setLastUpdate: (lastUpdate) => set({ lastUpdate }),
  setSimulationRunning: (simulationRunning) => set({ simulationRunning }),
  setSpeedMultiplier: (speedMultiplier) => set({ speedMultiplier }),
  setDemoMode: (demoMode) => set({ demoMode }),

  getSelectedDrone: () => {
    const { drones, selectedDroneId } = get();
    return drones.find((d) => d.id === selectedDroneId);
  },
  getActiveDrones: () => get().drones.filter((d) => d.status === 'active'),
  getCriticalAnomalies: () =>
    get().anomalies.filter((a) => a.risk_level === 'critical' && a.status === 'detected'),
}));
