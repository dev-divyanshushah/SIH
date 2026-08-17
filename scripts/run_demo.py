"""
PERSIST-AIR Complete SIH Demo Script
=======================================
Single command to run the complete end-to-end demonstration.

Usage:
    python scripts/run_demo.py

This script:
1. Checks backend is running
2. Triggers the 11-step scripted demo scenario
3. Polls and prints live events as they arrive
4. Shows the complete flow in the terminal
5. Reports final simulation state

The frontend should be running at http://localhost:5173 to watch the
visual representation of this demo in real-time.
"""
import time
import json
import sys
import os

try:
    import httpx
except ImportError:
    print("httpx not installed. Run: pip install httpx")
    sys.exit(1)

BACKEND_URL = "http://localhost:8000"
POLL_INTERVAL = 2.0    # seconds between polls
DEMO_DURATION = 90     # seconds to watch the demo

DIVIDER = "─" * 60


def check_backend():
    try:
        r = httpx.get(f"{BACKEND_URL}/api/system/status", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def get_events(after_id=None):
    try:
        r = httpx.get(f"{BACKEND_URL}/api/events", timeout=5)
        events = r.json()
        return events
    except Exception:
        return []


def get_state():
    try:
        r = httpx.get(f"{BACKEND_URL}/api/simulation/state", timeout=5)
        return r.json()
    except Exception:
        return {}


def get_drones():
    try:
        r = httpx.get(f"{BACKEND_URL}/api/drones", timeout=5)
        return r.json()
    except Exception:
        return []


def start_demo():
    try:
        r = httpx.post(f"{BACKEND_URL}/api/simulation/demo", json={}, timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def print_state(state, drones):
    print(f"\n{'=' * 60}")
    print(f"  PERSIST-AIR — LIVE SIMULATION STATE")
    print(f"{'=' * 60}")
    print(f"  Simulated Time:   {state.get('simulated_mission_time', '00:00:00')}")
    print(f"  Coverage:         {state.get('coverage_percentage', 0):.1f}%")
    print(f"  Active Drones:    {state.get('active_drones', 0)} / {state.get('total_drones', 0)}")
    print(f"  Anomalies:        {state.get('active_anomalies', 0)} active")
    print(f"  Events logged:    {state.get('total_events', 0)}")
    if state.get("active_handover"):
        h = state["active_handover"]
        print(f"  HANDOVER:         {h['active_drone']} → {h['replacement_drone']} ({h['status']})")
    print()
    print(f"  {'DRONE':<8} {'STATUS':<16} {'BATTERY':>8} {'ENDURANCE':>10}")
    print(f"  {'-'*50}")
    for d in drones:
        status = d.get("status", "?")
        batt = d.get("battery_percentage", 0)
        eft = d.get("estimated_flight_time", 0)
        batt_str = f"{batt:.1f}%"
        if batt < 20:
            batt_str = f"⚠ {batt:.1f}%"
        print(f"  {d['id']:<8} {status:<16} {batt_str:>8} {eft:>9.1f}m")
    print()


def main():
    print(DIVIDER)
    print("  PERSIST-AIR — SIH DEMONSTRATION")
    print("  AI-Powered Persistent Aerial Intelligence")
    print(DIVIDER)
    print()

    # Check backend
    print("Checking backend...")
    if not check_backend():
        print("❌ Backend not running!")
        print()
        print("Start it with:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    print("✓ Backend online")
    print()

    # Initial state
    state = get_state()
    drones = get_drones()
    print_state(state, drones)

    # Start demo
    print(DIVIDER)
    print("  STARTING 11-STEP DEMO SCENARIO")
    print(DIVIDER)
    result = start_demo()
    print(f"Demo initiated: {result}")
    print()

    # Monitor events
    seen_event_ids = set()
    start_time = time.time()

    print("Monitoring events (watching for 90 seconds)...")
    print("Open http://localhost:5173 to watch the visual dashboard")
    print(DIVIDER)

    while time.time() - start_time < DEMO_DURATION:
        events = get_events()
        for evt in events:
            eid = evt.get("id")
            if eid and eid not in seen_event_ids:
                seen_event_ids.add(eid)
                etype = evt.get("event_type", "?").upper()
                title = evt.get("title", "")
                risk = evt.get("risk_level", "")
                ts = evt.get("timestamp", "")[:19]
                risk_badge = f"[{risk.upper()}]" if risk else ""
                print(f"  [{ts}] {etype:<28} {risk_badge:<12} {title}")

        time.sleep(POLL_INTERVAL)

    # Final state
    print()
    print(DIVIDER)
    print("  DEMO COMPLETE — FINAL STATE")
    print(DIVIDER)
    final_state = get_state()
    final_drones = get_drones()
    print_state(final_state, final_drones)

    print(DIVIDER)
    print("  DEMO SUMMARY")
    print(DIVIDER)
    print(f"  Total events logged: {final_state.get('total_events', 0)}")
    print(f"  Final coverage:      {final_state.get('coverage_percentage', 0):.1f}%")
    print(f"  Active anomalies:    {final_state.get('active_anomalies', 0)}")
    print()
    print("  The demo demonstrated:")
    print("  ✓ Object detection & anomaly generation")
    print("  ✓ AI behaviour analysis & risk scoring")
    print("  ✓ Mission feasibility assessment")
    print("  ✓ AI drone selection (weighted scoring)")
    print("  ✓ Energy-aware mission assignment")
    print("  ✓ Predictive handover (battery-based)")
    print("  ✓ Human verification workflow")
    print("  ✓ Persistent coverage maintenance")
    print()
    print("  Open http://localhost:5173 for the full visual experience.")
    print(DIVIDER)


if __name__ == "__main__":
    main()
