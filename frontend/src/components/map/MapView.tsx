import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useAppStore } from '@/store/appStore';
import type { Drone, Anomaly } from '@/types';

const STATUS_COLORS: Record<string, string> = {
  active: '#10b981',
  available: '#64748b',
  returning: '#f59e0b',
  charging: '#3b82f6',
  critical: '#ef4444',
  offline: '#1e293b',
};

const RISK_COLORS: Record<string, string> = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#f97316',
  critical: '#ef4444',
};

function makeDroneIcon(drone: Drone, isSelected: boolean): L.DivIcon {
  const color = STATUS_COLORS[drone.status] || '#64748b';
  const size = isSelected ? 36 : 28;
  const headingRad = (drone.heading * Math.PI) / 180;
  // Arrow pointing in heading direction
  return L.divIcon({
    className: '',
    iconAnchor: [size / 2, size / 2],
    html: `
      <div style="
        width:${size}px; height:${size}px;
        position:relative;
        filter: drop-shadow(0 0 ${isSelected ? 10 : 6}px ${color});
      ">
        <svg width="${size}" height="${size}" viewBox="0 0 36 36" style="transform:rotate(${drone.heading}deg)">
          <polygon points="18,4 26,28 18,23 10,28" fill="${color}" stroke="#080c14" stroke-width="1.5"/>
          <circle cx="18" cy="18" r="3" fill="#080c14"/>
        </svg>
        ${isSelected ? `<div style="
          position:absolute; top:50%; left:50%;
          transform:translate(-50%,-50%);
          width:${size * 2.5}px; height:${size * 2.5}px;
          border:1px solid ${color}33;
          border-radius:50%;
        "></div>` : ''}
        <div style="
          position:absolute; top:-18px; left:50%; transform:translateX(-50%);
          background:#0d1421cc; border:1px solid ${color}55;
          padding:1px 5px; border-radius:2px;
          font:600 9px/1.4 'JetBrains Mono',monospace;
          color:${color}; white-space:nowrap;
        ">${drone.id}</div>
      </div>
    `,
  });
}

function makeAnomalyIcon(anomaly: Anomaly): L.DivIcon {
  const color = RISK_COLORS[anomaly.risk_level] || '#f59e0b';
  const pulse = anomaly.risk_level === 'critical' || anomaly.risk_level === 'high';
  return L.divIcon({
    className: '',
    iconAnchor: [12, 12],
    html: `
      <div style="position:relative; width:24px; height:24px;">
        <div style="
          width:24px; height:24px;
          background:${color}33; border:2px solid ${color};
          border-radius:50%; display:flex; align-items:center; justify-content:center;
          ${pulse ? `animation:pulse 1.5s infinite; box-shadow:0 0 12px ${color}66;` : ''}
        ">
          <div style="width:8px;height:8px;background:${color};border-radius:50%;"></div>
        </div>
        <div style="
          position:absolute; top:-16px; left:50%; transform:translateX(-50%);
          background:#0d1421cc; border:1px solid ${color}55;
          padding:1px 4px; border-radius:2px;
          font:600 8px/1.4 'JetBrains Mono',monospace;
          color:${color}; white-space:nowrap;
        ">${anomaly.object_class.toUpperCase()}</div>
      </div>
    `,
  });
}

function makeBaseIcon(): L.DivIcon {
  return L.divIcon({
    className: '',
    iconAnchor: [14, 14],
    html: `
      <div style="
        width:28px; height:28px;
        background:#1a2235; border:2px solid #3b82f6;
        border-radius:4px; display:flex; align-items:center; justify-content:center;
      ">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      </div>
    `,
  });
}

interface MapViewProps {
  height?: string;
  showControls?: boolean;
}

export function MapView({ height = '100%', showControls = true }: MapViewProps) {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const droneMarkersRef = useRef<Map<string, L.Marker>>(new Map());
  const anomalyMarkersRef = useRef<Map<string, L.Marker>>(new Map());
  const routeLinesRef = useRef<Map<string, L.Polyline>>(new Map());
  const coverageLayersRef = useRef<L.Circle[]>([]);
  const baseMarkersRef = useRef<L.Marker[]>([]);

  const { drones, anomalies, selectedDroneId, setSelectedDrone, coveragePercentage } = useAppStore();

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [29.5000, 73.5000],
      zoom: 13,
      zoomControl: false,
      attributionControl: false,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '',
      maxZoom: 18,
      opacity: 0.6,
    }).addTo(map);

    if (showControls) {
      L.control.zoom({ position: 'bottomright' }).addTo(map);
    }

    // Add grid style overlay (tactical effect)
    map.on('click', () => setSelectedDrone(null));

    mapRef.current = map;

    // Add mission boundary polygon
    const boundary = L.polygon([
      [29.512, 73.488],
      [29.512, 73.512],
      [29.488, 73.512],
      [29.488, 73.488],
    ], {
      color: '#06b6d4',
      weight: 1,
      opacity: 0.5,
      fillColor: '#06b6d4',
      fillOpacity: 0.03,
      dashArray: '6 4',
    }).addTo(map);

    // Label for the zone
    const LabelControl = L.Control.extend({
      onAdd: () => {
        const div = L.DomUtil.create('div');
        div.innerHTML = `
          <div style="background:#ef4444dd; color:#fff; padding:6px 12px; font:700 11px 'Inter',sans-serif; letter-spacing:0.1em; border-radius:4px; border:1px solid #7f1d1d;">
            SIMULATED BORDER SURVEILLANCE ZONE
          </div>
        `;
        return div;
      }
    });
    new LabelControl({ position: 'topright' }).addTo(map);

    // Fit Formation Control
    const FitControl = L.Control.extend({
      onAdd: () => {
        const div = L.DomUtil.create('div');
        div.innerHTML = `
          <button id="fit-formation-btn" style="background:#1e293b; color:#38bdf8; border:1px solid #38bdf8; padding:6px 12px; font:600 11px 'Inter',sans-serif; border-radius:4px; cursor:pointer;">
            FIT FORMATION
          </button>
        `;
        div.onclick = () => {
          map.fitBounds([
            [29.515, 73.485],
            [29.485, 73.515]
          ]);
        };
        return div;
      }
    });
    new FitControl({ position: 'topleft' }).addTo(map);

    // Add base station markers
    const bases = [
      { lat: 29.5000, lon: 73.5000, label: 'BASE-ALPHA' },
    ];
    bases.forEach(base => {
      const marker = L.marker([base.lat, base.lon], { icon: makeBaseIcon() }).addTo(map);
      marker.bindPopup(`<b style="color:#3b82f6">${base.label}</b><br/>Home / Charging Station`);
      baseMarkersRef.current.push(marker);
    });

    // Add legend
    const LegendControl = L.Control.extend({
      onAdd: () => {
        const div = L.DomUtil.create('div');
        div.innerHTML = `
          <div style="
            background:#0d1421ee; border:1px solid #1e293b;
            padding:8px 10px; border-radius:4px; font:11px 'Inter',sans-serif;
          ">
            <div style="color:#94a3b8; font-size:9px; letter-spacing:0.1em; margin-bottom:6px; text-transform:uppercase;">Drone Status</div>
            ${Object.entries(STATUS_COLORS).map(([s, c]) => `
              <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
                <div style="width:8px;height:8px;background:${c};border-radius:50%;"></div>
                <span style="color:#94a3b8;font-size:10px;text-transform:capitalize;">${s}</span>
              </div>
            `).join('')}
            <div style="color:#94a3b8; font-size:9px; letter-spacing:0.1em; margin:8px 0 4px; text-transform:uppercase;">Anomaly Risk</div>
            ${Object.entries(RISK_COLORS).map(([r, c]) => `
              <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
                <div style="width:8px;height:8px;background:${c};border-radius:50%;border:1px solid ${c}66;"></div>
                <span style="color:#94a3b8;font-size:10px;text-transform:capitalize;">${r}</span>
              </div>
            `).join('')}
            <div style="color:#94a3b8; font-size:9px; letter-spacing:0.1em; margin:8px 0 4px; text-transform:uppercase;">Coverage</div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
              <div style="width:8px;height:8px;background:#10b981;border-radius:50%;opacity:0.2;"></div>
              <span style="color:#94a3b8;font-size:10px;">Single Coverage</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
              <div style="width:8px;height:8px;background:#10b981;border-radius:50%;opacity:0.5;"></div>
              <span style="color:#94a3b8;font-size:10px;">Overlapping Coverage</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
              <div style="width:8px;height:8px;background:#10b981;border-radius:50%;opacity:0.8;"></div>
              <span style="color:#94a3b8;font-size:10px;">High Redundancy</span>
            </div>
          </div>
        `;
        return div;
      }
    });
    new LegendControl({ position: 'bottomleft' }).addTo(map);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update drone markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const seenIds = new Set<string>();
    drones.forEach(drone => {
      seenIds.add(drone.id);
      const isSelected = drone.id === selectedDroneId;
      const icon = makeDroneIcon(drone, isSelected);

      if (droneMarkersRef.current.has(drone.id)) {
        const marker = droneMarkersRef.current.get(drone.id)!;
        marker.setLatLng([drone.latitude, drone.longitude]);
        marker.setIcon(icon);
      } else {
        const marker = L.marker([drone.latitude, drone.longitude], { icon })
          .addTo(map)
          .on('click', (e) => {
            e.originalEvent?.stopPropagation();
            setSelectedDrone(drone.id);
          });
        droneMarkersRef.current.set(drone.id, marker);
      }

      // Update popup
      const marker = droneMarkersRef.current.get(drone.id)!;
      const color = STATUS_COLORS[drone.status];
      marker.unbindPopup();
      marker.bindPopup(`
        <div style="min-width:180px;">
          <div style="color:${color};font-weight:700;font-size:13px;margin-bottom:6px;">${drone.id} — ${drone.name}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:11px;">
            <span style="color:#64748b;">Battery</span><span style="color:#f1f5f9;font-family:monospace;">${drone.battery_percentage.toFixed(1)}%</span>
            <span style="color:#64748b;">Status</span><span style="color:${color};text-transform:capitalize;">${drone.status}</span>
            <span style="color:#64748b;">Altitude</span><span style="color:#f1f5f9;font-family:monospace;">${drone.altitude.toFixed(0)}m</span>
            <span style="color:#64748b;">Speed</span><span style="color:#f1f5f9;font-family:monospace;">${drone.airspeed.toFixed(1)} m/s</span>
            <span style="color:#64748b;">Flight Time</span><span style="color:#f1f5f9;font-family:monospace;">${drone.estimated_flight_time.toFixed(0)} min</span>
          </div>
          ${drone.mission_id ? `<div style="margin-top:6px;padding:4px 6px;background:#1a2235;border-radius:2px;font-size:10px;color:#06b6d4;">Mission: ${drone.mission_id}</div>` : ''}
        </div>
      `);

      // Route line for selected drone
      if (isSelected && drone.status === 'active') {
        if (!routeLinesRef.current.has(drone.id)) {
          const line = L.polyline([[drone.home_latitude, drone.home_longitude], [drone.latitude, drone.longitude]], {
            color, weight: 1, opacity: 0.4, dashArray: '4 4',
          }).addTo(map);
          routeLinesRef.current.set(drone.id, line);
        } else {
          routeLinesRef.current.get(drone.id)!.setLatLngs([[drone.home_latitude, drone.home_longitude], [drone.latitude, drone.longitude]]);
        }
      } else if (routeLinesRef.current.has(drone.id) && !isSelected) {
        map.removeLayer(routeLinesRef.current.get(drone.id)!);
        routeLinesRef.current.delete(drone.id);
      }
    });

    // Remove stale markers
    droneMarkersRef.current.forEach((marker, id) => {
      if (!seenIds.has(id)) {
        map.removeLayer(marker);
        droneMarkersRef.current.delete(id);
      }
    });

    // Pan to selected drone
    if (selectedDroneId) {
      const d = drones.find(d => d.id === selectedDroneId);
      if (d) map.panTo([d.latitude, d.longitude], { animate: true, duration: 0.5 });
    }
  }, [drones, selectedDroneId]);

  // Update anomaly markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const seenIds = new Set<string>();
    anomalies.forEach(anomaly => {
      if (anomaly.status === 'dismissed' || anomaly.status === 'resolved') return;
      seenIds.add(anomaly.id);

      if (!anomalyMarkersRef.current.has(anomaly.id)) {
        const marker = L.marker([anomaly.latitude, anomaly.longitude], {
          icon: makeAnomalyIcon(anomaly),
        }).addTo(map);
        marker.bindPopup(`
          <div>
            <div style="color:${RISK_COLORS[anomaly.risk_level]};font-weight:700;margin-bottom:4px;">
              ${anomaly.object_class.toUpperCase()} — Risk ${anomaly.risk_score}/100
            </div>
            <div style="font-size:11px;color:#94a3b8;">${anomaly.description}</div>
            <div style="margin-top:4px;font-size:10px;color:#475569;">Sector ${anomaly.sector} · ${anomaly.detected_by_drone_id}</div>
          </div>
        `);
        anomalyMarkersRef.current.set(anomaly.id, marker);
      }
    });

    anomalyMarkersRef.current.forEach((marker, id) => {
      if (!seenIds.has(id)) {
        map.removeLayer(marker);
        anomalyMarkersRef.current.delete(id);
      }
    });
  }, [anomalies]);

  // Coverage circles
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    coverageLayersRef.current.forEach(l => map.removeLayer(l));
    coverageLayersRef.current = [];

    const activeDrones = drones.filter(d => d.status === 'active' || d.status === 'investigating' || d.status === 'patrolling');
    activeDrones.forEach(drone => {
      const circle = L.circle([drone.latitude, drone.longitude], {
        radius: 1200,
        color: '#10b981',
        weight: 0,
        fillColor: '#10b981',
        fillOpacity: 0.15,
      }).addTo(map);
      coverageLayersRef.current.push(circle);
    });
  }, [drones]);

  return (
    <div
      ref={containerRef}
      style={{ width: '100%', height }}
      className="map-container tactical-grid"
    />
  );
}
