import os
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/existing_baseline_results.csv"
OUTPUT_DIR = "data/graphs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Could not find {INPUT_FILE}. Run existing_baseline.py first."
    )

df = pd.read_csv(INPUT_FILE)

required = ["Existing_Decision", "Scenario", "Latency_ms"]
missing = [column for column in required if column not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

# -------------------------------
# Graph 1: EDGE vs CLOUD decisions
# -------------------------------
decision_counts = (
    df["Existing_Decision"]
    .value_counts()
    .reindex(["EDGE", "CLOUD"], fill_value=0)
)

ax = decision_counts.plot(kind="bar", rot=0)
ax.set_title("Existing Heuristic: Offloading Decisions")
ax.set_xlabel("Execution location")
ax.set_ylabel("Number of tasks")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "existing_decision_counts.png"),
    dpi=200
)
plt.close()

# ---------------------------------------
# Graph 2: Average dataset latency by scenario
# ---------------------------------------
scenario_latency = df.groupby("Scenario")["Latency_ms"].mean()

ax = scenario_latency.plot(kind="bar", rot=0)
ax.set_title("Existing Dataset: Average Input Latency by Scenario")
ax.set_xlabel("Network scenario")
ax.set_ylabel("Average input latency (ms)")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "existing_latency_by_scenario.png"),
    dpi=200
)
plt.close()

print("Graphs created successfully:")
print(os.path.join(OUTPUT_DIR, "existing_decision_counts.png"))
print(os.path.join(OUTPUT_DIR, "existing_latency_by_scenario.png"))