"""
Synthetic Anomaly Behaviour Dataset Generator
===============================================
Generates synthetic trajectory/behaviour features for anomaly detection training.

Method: Isolation Forest (unsupervised) — learns what is "normal" then flags deviations.
For supervised comparison: we also generate labeled anomaly/normal samples.

IMPORTANT: SYNTHETIC data — not real surveillance data.
Features represent what would be extracted from object tracking in a real system.

Run: python scripts/generate_anomaly_dataset.py
Output: data/synthetic/anomaly_dataset.csv (8,000 samples)
"""
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

N_NORMAL = 6000    # normal behaviour samples
N_ANOMALY = 2000   # anomalous behaviour samples

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'synthetic', 'anomaly_dataset.csv'
)


def generate_normal_samples(n):
    """
    Normal behaviour: expected patterns during daytime, outside restricted zones.
    """
    rows = []
    for _ in range(n):
        time_of_day = np.random.normal(13.0, 3.0)  # centered around afternoon
        time_of_day = np.clip(time_of_day, 7, 21)  # daytime hours
        rows.append({
            "duration_minutes": np.random.exponential(4),      # short stays
            "group_size": np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1]),
            "time_of_day": round(time_of_day, 2),
            "day_of_week": np.random.randint(0, 7),
            "in_restricted_zone": 0,                            # not restricted
            "speed_variance": np.random.exponential(0.001),    # consistent speed
            "direction_changes": np.random.choice([0, 1, 2], p=[0.5, 0.35, 0.15]),
            "distance_from_normal_area": np.random.exponential(0.5),
            "is_anomaly": 0,                                    # LABEL: normal
        })
    return rows


def generate_anomaly_samples(n):
    """
    Anomalous behaviour: unexpected patterns.
    """
    rows = []
    anomaly_types = [
        "nighttime_activity",
        "restricted_zone",
        "extended_loitering",
        "erratic_movement",
        "large_group",
        "coordinated_approach",
    ]
    for _ in range(n):
        atype = np.random.choice(anomaly_types)

        if atype == "nighttime_activity":
            time_of_day = np.random.choice(
                list(np.random.uniform(0, 5, 50)) + list(np.random.uniform(22, 24, 50))
            )
            row = {
                "duration_minutes": np.random.exponential(8),
                "group_size": np.random.randint(1, 4),
                "time_of_day": round(time_of_day, 2),
                "day_of_week": np.random.randint(0, 7),
                "in_restricted_zone": np.random.choice([0, 1]),
                "speed_variance": np.random.exponential(0.005),
                "direction_changes": np.random.randint(0, 5),
                "distance_from_normal_area": np.random.exponential(2.0),
            }
        elif atype == "restricted_zone":
            row = {
                "duration_minutes": np.random.uniform(2, 30),
                "group_size": np.random.randint(1, 6),
                "time_of_day": np.random.uniform(6, 22),
                "day_of_week": np.random.randint(0, 7),
                "in_restricted_zone": 1,                         # KEY feature
                "speed_variance": np.random.exponential(0.003),
                "direction_changes": np.random.randint(0, 8),
                "distance_from_normal_area": np.random.exponential(3.0),
            }
        elif atype == "extended_loitering":
            row = {
                "duration_minutes": np.random.uniform(20, 90),  # long duration
                "group_size": np.random.randint(1, 3),
                "time_of_day": np.random.uniform(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "in_restricted_zone": np.random.choice([0, 1], p=[0.4, 0.6]),
                "speed_variance": np.random.exponential(0.001),
                "direction_changes": np.random.randint(0, 3),
                "distance_from_normal_area": np.random.exponential(1.5),
            }
        elif atype == "erratic_movement":
            row = {
                "duration_minutes": np.random.uniform(5, 20),
                "group_size": np.random.randint(1, 4),
                "time_of_day": np.random.uniform(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "in_restricted_zone": np.random.choice([0, 1]),
                "speed_variance": np.random.uniform(0.02, 0.1),  # high variance
                "direction_changes": np.random.randint(8, 20),   # many changes
                "distance_from_normal_area": np.random.exponential(2.0),
            }
        elif atype == "large_group":
            row = {
                "duration_minutes": np.random.uniform(5, 30),
                "group_size": np.random.randint(6, 15),           # large group
                "time_of_day": np.random.uniform(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "in_restricted_zone": np.random.choice([0, 1], p=[0.3, 0.7]),
                "speed_variance": np.random.exponential(0.004),
                "direction_changes": np.random.randint(2, 10),
                "distance_from_normal_area": np.random.exponential(2.5),
            }
        else:  # coordinated_approach
            row = {
                "duration_minutes": np.random.uniform(3, 15),
                "group_size": np.random.randint(3, 8),
                "time_of_day": np.random.choice(
                    list(np.random.uniform(0, 6, 30)) + list(np.random.uniform(20, 24, 30))
                ),
                "day_of_week": np.random.randint(0, 7),
                "in_restricted_zone": 1,
                "speed_variance": np.random.exponential(0.008),
                "direction_changes": np.random.randint(3, 12),
                "distance_from_normal_area": np.random.exponential(4.0),
            }

        row["is_anomaly"] = 1
        rows.append(row)

    return rows


if __name__ == "__main__":
    print("Generating synthetic anomaly behaviour dataset...")
    print(f"  Normal samples: {N_NORMAL}")
    print(f"  Anomaly samples: {N_ANOMALY}")
    print(f"  Total: {N_NORMAL + N_ANOMALY}")
    print("  Data type: SYNTHETIC — not real surveillance data")
    print()

    rows = generate_normal_samples(N_NORMAL) + generate_anomaly_samples(N_ANOMALY)
    df = pd.DataFrame(rows)

    # Shuffle
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # Clip and clean
    df["duration_minutes"] = df["duration_minutes"].clip(0, 120)
    df["speed_variance"] = df["speed_variance"].clip(0, 1)
    df["distance_from_normal_area"] = df["distance_from_normal_area"].clip(0, 20)
    df["time_of_day"] = df["time_of_day"].clip(0, 23.99)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✓ Saved: {OUTPUT_PATH}")
    print(f"  Shape: {df.shape}")
    print(f"  Anomaly rate: {df['is_anomaly'].mean():.1%}")
    print()
    print("Dataset summary:")
    print(df.describe().to_string())
