import { useEffect, useRef } from 'react';
import { useAppStore } from '@/store/appStore';
import type { TelemetryMessage } from '@/types';

const WS_URL = 'ws://localhost:8000/ws/telemetry';
const RECONNECT_DELAY = 3000;

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const {
    setDrones, setAnomalies, setEvents, setCoverage, setCoverageMetrics, setActiveHandover,
    setTick, setWsConnected, setLastUpdate,
  } = useAppStore();

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
      console.log('[WS] Connected to PERSIST-AIR telemetry');
    };

    ws.onmessage = (evt) => {
      try {
        const msg: TelemetryMessage = JSON.parse(evt.data);
        if (msg.type === 'telemetry') {
          if (msg.drones) setDrones(msg.drones);
          if (msg.anomalies) setAnomalies(msg.anomalies);
          if (msg.events) setEvents(msg.events);
          if (msg.coverage_percentage !== undefined) setCoverage(msg.coverage_percentage);
          if (msg.coverage_metrics !== undefined) setCoverageMetrics(msg.coverage_metrics);
          if (msg.active_handover !== undefined) setActiveHandover(msg.active_handover ?? null);
          if (msg.tick !== undefined) setTick(msg.tick);
          if (msg.timestamp) setLastUpdate(msg.timestamp);
        }
      } catch (e) {
        console.warn('[WS] Parse error', e);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
      console.warn('[WS] Disconnected. Reconnecting in 3s...');
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
    };

    ws.onerror = () => {
      ws.close();
    };

    // Ping every 20s to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 20000);

    return () => clearInterval(pingInterval);
  };

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);
}
