// ─── Drone Types ─────────────────────────────────────────────────────────────
export type DroneStatus = 'active' | 'available' | 'returning' | 'charging' | 'critical' | 'offline';
export type OperationalMode = 'security' | 'humanitarian' | 'environmental';

export interface Drone {
  id: string;
  name: string;
  model?: string;
  status: DroneStatus;
  latitude: number;
  longitude: number;
  altitude: number;
  airspeed: number;
  heading: number;
  battery_percentage: number;
  battery_voltage: number;
  current_consumption: number;
  battery_temperature: number;
  distance_from_base: number;
  estimated_flight_time: number;
  home_latitude: number;
  home_longitude: number;
  communication_quality: number;
  health_score: number;
  mission_id: string | null;
  mission_type: string | null;
  operational_mode: OperationalMode;
  battery_history: number[];
  speed_history: number[];
  altitude_history: number[];
}

// ─── Mission Types ────────────────────────────────────────────────────────────
export type MissionStatus = 'planned' | 'active' | 'completed' | 'aborted' | 'pending_handover';
export type MissionPriority = 'low' | 'medium' | 'high' | 'critical';

export interface Mission {
  id: string;
  name: string;
  status: MissionStatus;
  priority: MissionPriority;
  assigned_drone_id: string | null;
  target_latitude?: number;
  target_longitude?: number;
  mission_type: string;
  operational_mode: OperationalMode;
  estimated_duration: number;
  estimated_energy: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

// ─── Anomaly Types ────────────────────────────────────────────────────────────
export type AnomalyRisk = 'low' | 'medium' | 'high' | 'critical';
export type AnomalyStatus = 'detected' | 'under_investigation' | 'verified' | 'dismissed' | 'resolved';

export interface Anomaly {
  id: string;
  detected_by_drone_id: string;
  object_class: string;
  behaviour_type: string | null;
  latitude: number;
  longitude: number;
  confidence: number;
  risk_score: number;
  risk_level: AnomalyRisk;
  status: AnomalyStatus;
  sector: string;
  description: string;
  behaviour_description: string;
  risk_breakdown: Record<string, number>;
  detected_at: string;
  investigation_drone_id: string | null;
}

// ─── Event Types ──────────────────────────────────────────────────────────────
export type EventType =
  | 'detection' | 'anomaly' | 'risk_assessment' | 'feasibility_check'
  | 'drone_selection' | 'handover_initiated' | 'handover_completed'
  | 'verification_requested' | 'verification_confirmed' | 'verification_dismissed'
  | 'mission_started' | 'mission_completed'
  | 'battery_warning' | 'battery_critical' | 'coverage_gap' | 'system';

export interface IntelEvent {
  id: string;
  event_type: EventType;
  drone_id: string | null;
  mission_id: string | null;
  anomaly_id: string | null;
  title: string;
  description: string;
  risk_level: AnomalyRisk | null;
  latitude: number | null;
  longitude: number | null;
  sector: string | null;
  timestamp: string;
}

// ─── Energy Types ─────────────────────────────────────────────────────────────
export interface EnergyPrediction {
  remaining_endurance_minutes: number;
  safe_mission_time: number;
  return_reserve_minutes: number;
  energy_risk: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  predicted_battery_curve: { t: number; pct: number }[];
}

export interface MissionFeasibility {
  result: 'FEASIBLE' | 'MARGINAL' | 'NOT_FEASIBLE';
  estimated_mission_energy: number;
  available_usable_energy: number;
  required_return_reserve: number;
  predicted_completion_time: string;
  confidence: number;
  recommendation: string;
}

// ─── Handover Types ───────────────────────────────────────────────────────────
export interface ActiveHandover {
  active_drone: string;
  replacement_drone: string;
  handover_time: string;
  coverage_continuity: number;
  confidence: number;
  status: 'initiated' | 'in_progress' | 'completed';
}

// ─── Coverage Types ───────────────────────────────────────────────────────────
export interface CoverageZone {
  id: string;
  lat: number;
  lon: number;
  radius: number;
  drone: string;
  coverage: number;
}

export interface CoverageState {
  coverage_percentage: number;
  uncovered_percentage: number;
  predicted_continuity: number;
  active_drones: number;
  zones: CoverageZone[];
  active_handover: ActiveHandover | null;
}

// ─── Telemetry WebSocket Message ──────────────────────────────────────────────
export interface TelemetryMessage {
  type: 'telemetry' | 'pong' | 'keepalive';
  drones?: Drone[];
  anomalies?: Anomaly[];
  events?: IntelEvent[];
  coverage_percentage?: number;
  coverage_metrics?: { overall: number; redundant: number; single: number; gaps: number; status: string };
  active_handover?: ActiveHandover | null;
  tick?: number;
  timestamp?: string;
}

// ─── Simulation State ─────────────────────────────────────────────────────────
export interface SimulationState {
  running: boolean;
  tick: number;
  speed_multiplier: number;
  operational_mode: OperationalMode;
  demo_mode: boolean;
  active_drones: number;
  available_drones: number;
  charging_drones: number;
  returning_drones: number;
  critical_drones: number;
  total_drones: number;
  coverage_percentage: number;
  average_battery: number;
  active_anomalies: number;
  total_events: number;
  active_handover: ActiveHandover | null;
}

// ─── DroneCandidate (for selection) ──────────────────────────────────────────
export interface DroneCandidate {
  drone_id: string;
  score: number;
  energy_score: number;
  distance_score: number;
  distance_km: number;
  health_score: number;
  communication_quality: number;
  feasible: boolean;
  battery_percentage: number;
  status: DroneStatus;
}
