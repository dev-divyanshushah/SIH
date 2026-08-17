"""
Synthetic Energy Dataset Generator
======================================
Generates a physics-inspired synthetic dataset for UAV energy endurance prediction.

IMPORTANT: This is SYNTHETIC data, not real UAV flight data.
All relationships are physically motivated but not calibrated on real hardware.
Any model trained on this must be labeled: "Synthetic/Simulation-based evaluation"

Physics assumptions:
- Base drain: ~1.4% battery per minute at 14 m/s cruise at 120m altitude
- Speed effect: drag ~ v^1.5 (simplified)
- Altitude effect: +0.05% drain per 10m above 100m (thinner air)
- Temperature: >30°C increases battery resistance, slightly faster drain
- Wind: headwind factor > 1.0 increases drain linearly
- Payload: each 100g payload ~ +2% drain increase
- Battery voltage: linearly related to charge level
- Temperature: hot battery degrades voltage under load

Run: python scripts/generate_energy_dataset.py
Output: data/synthetic/energy_dataset.csv (12,000 samples)
"""
import numpy as np
import pandas as pd
import os
import sys
import random

# Fix path for running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

N_SAMPLES = 12000
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'synthetic', 'energy_dataset.csv')


def simulate_endurance(
    battery_pct, battery_voltage, current_consumption,
    temperature, airspeed, altitude, distance_from_base,
    wind_factor, payload_weight
):
    """
    Physics-based endurance calculation.
    Returns remaining_endurance_minutes.
    """
    # Base drain rate (%/min) at nominal conditions
    base_drain = 1.4

    # Speed factor: higher speed = more drag = more power
    speed_factor = (airspeed / 14.0) ** 1.5

    # Altitude factor: thinner air at altitude = less lift efficiency
    altitude_factor = 1.0 + max(0, (altitude - 100)) / 2000.0

    # Temperature factor: hot batteries discharge faster under load
    temp_factor = 1.0 + max(0, (temperature - 30)) * 0.012

    # Wind factor: headwind directly increases energy cost
    wind_eff = wind_factor

    # Payload factor: each kg of payload ~+8% drain
    payload_factor = 1.0 + payload_weight * 0.08

    effective_drain = (base_drain * speed_factor * altitude_factor *
                       temp_factor * wind_eff * payload_factor)

    # Usable battery (keep 8% reserve)
    usable_pct = max(0, battery_pct - 8.0)
    endurance = usable_pct / effective_drain

    return endurance


def generate_dataset(n=N_SAMPLES):
    rows = []
    for _ in range(n):
        # Sample input features
        battery_pct = np.random.uniform(10, 100)
        battery_voltage = 19.0 + (battery_pct / 100) * 3.2 + np.random.normal(0, 0.05)
        current_consumption = np.random.normal(18.5, 1.5)
        temperature = np.random.uniform(5, 45)
        airspeed = np.random.uniform(8, 22)
        altitude = np.random.uniform(50, 300)
        distance_from_base = np.random.uniform(50, 5000)   # metres
        wind_factor = np.random.uniform(0.8, 2.0)          # 1.0 = no wind
        payload_weight = np.random.choice(
            [0.0, 0.1, 0.2, 0.3, 0.5, 1.0],
            p=[0.5, 0.15, 0.15, 0.1, 0.07, 0.03]
        )

        endurance = simulate_endurance(
            battery_pct, battery_voltage, current_consumption,
            temperature, airspeed, altitude, distance_from_base,
            wind_factor, payload_weight
        )

        # Add realistic measurement noise
        endurance += np.random.normal(0, 0.5)
        endurance = max(0, endurance)

        rows.append({
            "battery_percentage": round(battery_pct, 2),
            "battery_voltage": round(battery_voltage, 3),
            "current_consumption": round(current_consumption, 2),
            "temperature": round(temperature, 1),
            "airspeed": round(airspeed, 2),
            "altitude": round(altitude, 1),
            "distance_from_base": round(distance_from_base, 1),
            "wind_factor": round(wind_factor, 3),
            "payload_weight": payload_weight,
            "remaining_endurance_minutes": round(endurance, 2),  # TARGET
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Generating synthetic energy endurance dataset...")
    print(f"  N samples: {N_SAMPLES}")
    print(f"  Random seed: {RANDOM_SEED}")
    print("  Data type: SYNTHETIC (physics-inspired, not real UAV data)")
    print()

    df = generate_dataset(N_SAMPLES)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✓ Saved: {OUTPUT_PATH}")
    print(f"  Shape: {df.shape}")
    print()
    print("Dataset summary:")
    print(df.describe().to_string())
    print()
    print("Correlation with target (remaining_endurance_minutes):")
    corr = df.corr()["remaining_endurance_minutes"].sort_values()
    print(corr.to_string())
