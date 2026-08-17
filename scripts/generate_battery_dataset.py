"""
Synthetic Battery Degradation Dataset Generator
=================================================
Generates synthetic LiPo battery degradation data for SoH (State of Health) prediction.

Based on: empirical LiPo degradation research
- ~500 full cycles to reach 80% SoH under nominal conditions
- Temperature accelerates degradation above 35°C
- Deep discharge (>80% DoD) accelerates degradation
- Voltage sag under load correlates with health

IMPORTANT: SYNTHETIC data — not real battery cycle data.

Run: python scripts/generate_battery_dataset.py
Output: data/synthetic/battery_dataset.csv (5,000 samples)
"""
import numpy as np
import pandas as pd
import os
import sys

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

N_SAMPLES = 5000
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'synthetic', 'battery_dataset.csv'
)


def compute_soh(cycle_count, avg_temp, dod, voltage_sag):
    """
    Physics-inspired State of Health calculation.
    SoH = 100% when new, degrades with cycles, temperature, and DoD.
    """
    # Base degradation per cycle at nominal conditions (25°C, 80% DoD)
    base_degradation = 0.040  # % SoH per cycle

    # Temperature multiplier: linear above 35°C, moderate below 0°C
    if avg_temp > 35:
        temp_factor = 1.0 + (avg_temp - 35) * 0.025
    elif avg_temp < 5:
        temp_factor = 1.0 + (5 - avg_temp) * 0.010
    else:
        temp_factor = 1.0

    # DoD multiplier: deep discharge accelerates degradation
    dod_factor = 1.0 + max(0, (dod - 80)) * 0.015

    # Voltage sag multiplier: high sag = degraded internal resistance
    voltage_sag_factor = 1.0 + max(0, voltage_sag - 0.2) * 0.5

    degradation_per_cycle = base_degradation * temp_factor * dod_factor * voltage_sag_factor
    total_degradation = cycle_count * degradation_per_cycle

    # SoH: start at 100, floor at 50 (battery should be replaced by then)
    soh = max(50.0, 100.0 - total_degradation)

    return soh, degradation_per_cycle


if __name__ == "__main__":
    print("Generating synthetic battery degradation dataset...")
    print(f"  N samples: {N_SAMPLES}")
    print(f"  Random seed: {RANDOM_SEED}")
    print("  Data type: SYNTHETIC — not real battery cycle data")
    print()

    rows = []
    for _ in range(N_SAMPLES):
        cycle_count = int(np.random.exponential(200))
        cycle_count = np.clip(cycle_count, 1, 800)

        avg_temp = np.random.normal(28, 8)
        avg_temp = np.clip(avg_temp, -10, 55)

        dod = np.random.normal(75, 12)   # depth of discharge %
        dod = np.clip(dod, 20, 100)

        nominal_capacity = 5200.0  # mAh
        voltage_sag = np.random.exponential(0.15) + 0.05
        voltage_sag = np.clip(voltage_sag, 0.05, 1.5)

        soh, deg_rate = compute_soh(cycle_count, avg_temp, dod, voltage_sag)

        # Add noise
        soh += np.random.normal(0, 1.0)
        soh = np.clip(soh, 50, 100)

        current_capacity = nominal_capacity * soh / 100

        rows.append({
            "cycle_count": cycle_count,
            "average_temperature": round(avg_temp, 1),
            "depth_of_discharge": round(dod, 1),
            "current_capacity_ratio": round(current_capacity / nominal_capacity, 4),
            "voltage_sag": round(voltage_sag, 3),
            "state_of_health": round(soh, 2),     # TARGET
        })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✓ Saved: {OUTPUT_PATH}")
    print(f"  Shape: {df.shape}")
    print()
    print("Dataset summary:")
    print(df.describe().to_string())
    print()
    print("SoH distribution:")
    print(pd.cut(df["state_of_health"], bins=[50, 70, 80, 90, 100]).value_counts().sort_index())
