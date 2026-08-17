const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json();
}

// ─── Drones ───────────────────────────────────────────────────────────────────
export const api = {
  drones: {
    list: () => request('/drones'),
    get: (id: string) => request(`/drones/${id}`),
    telemetry: (id: string) => request(`/drones/${id}/telemetry`),
  },

  missions: {
    list: () => request('/missions'),
    get: (id: string) => request(`/missions/${id}`),
    create: (data: object) => request('/missions', { method: 'POST', body: JSON.stringify(data) }),
  },

  anomalies: {
    list: () => request('/anomalies'),
    get: (id: string) => request(`/anomalies/${id}`),
    verify: (id: string, action: 'confirm' | 'dismiss') =>
      request(`/anomalies/${id}/verify`, { method: 'POST', body: JSON.stringify({ action }) }),
  },

  ai: {
    detectionsList: () => request('/ai/detections/list', { method: 'POST', body: '{}' }),
    detect: (data: object) => request('/ai/detect', { method: 'POST', body: JSON.stringify(data) }),
    behaviour: (data: object) => request('/ai/behaviour', { method: 'POST', body: JSON.stringify(data) }),
    risk: (data: object) => request('/ai/risk', { method: 'POST', body: JSON.stringify(data) }),
  },

  energy: {
    predict: (data: object) => request('/energy/predict', { method: 'POST', body: JSON.stringify(data) }),
    feasibility: (data: object) => request('/mission/feasibility', { method: 'POST', body: JSON.stringify(data) }),
    selectDrone: (data: object) => request('/mission/select-drone', { method: 'POST', body: JSON.stringify(data) }),
    planPath: (data: object) => request('/path/plan', { method: 'POST', body: JSON.stringify(data) }),
    predictHandover: (data: object) => request('/handover/predict', { method: 'POST', body: JSON.stringify(data) }),
  },

  system: {
    status: () => request('/system/status'),
    events: () => request('/events'),
    coverage: () => request('/coverage'),
    simulationState: () => request('/simulation/state'),
    start: () => request('/simulation/start', { method: 'POST', body: '{}' }),
    pause: () => request('/simulation/pause', { method: 'POST', body: '{}' }),
    reset: () => request('/simulation/reset', { method: 'POST', body: '{}' }),
    setSpeed: (multiplier: number) =>
      request('/simulation/speed', { method: 'POST', body: JSON.stringify({ multiplier }) }),
    startDemo: () => request('/simulation/demo', { method: 'POST', body: '{}' }),
    setMode: (mode: string) =>
      request('/simulation/mode', { method: 'POST', body: JSON.stringify({ mode }) }),
  },
};
