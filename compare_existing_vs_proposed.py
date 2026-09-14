
import os
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
API_URL = "http://127.0.0.1:8000"
DATASET_PATH = "data/raw/network_dataset.csv"
OUTPUT_CSV = "data/comparison_results.csv"
OUTPUT_GRAPH = "data/graphs/existing_vs_proposed_decisions.png"


# ---------------------------------------------------------
# EXISTING SYSTEM: STATIC-THRESHOLD HEURISTIC
# Same rules as existing_baseline.py
# ---------------------------------------------------------
def existing_heuristic_decision(latency, cpu_usage, task_size):
    score = 0

    if latency > 100:
        score += 2
    elif latency > 50:
        score += 1

    if cpu_usage > 70:
        score += 2
    elif cpu_usage > 50:
        score += 1

    if task_size > 7:
        score += 2
    elif task_size > 4:
        score += 1

    return "CLOUD" if score >= 3 else "EDGE"


def main():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    required_columns = [
        "Time",
        "Scenario",
        "Bandwidth_Mbps",
        "Latency_ms",
        "CPU_Usage_percent",
        "Task_Size_MB",
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    # Preserve the dataset's original row order.
    df = df.reset_index(drop=True)

    # Check that the API is running.
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            "Could not connect to the API. Keep uvicorn running at "
            "http://127.0.0.1:8000 and run this script again."
        ) from error

    # Reset any previous real-time history.
    reset_response = requests.post(f"{API_URL}/realtime/reset", timeout=15)
    reset_response.raise_for_status()

    # /realtime/start requires a file upload.
    # Upload the dataset file to register the test task.
    with open(DATASET_PATH, "rb") as dataset_file:
        start_response = requests.post(
            f"{API_URL}/realtime/start",
            files={
                "file": (
                    os.path.basename(DATASET_PATH),
                    dataset_file,
                    "text/csv",
                )
            },
            timeout=30,
        )

    start_response.raise_for_status()
    print("API monitoring session started.")

    results = []

    # Replay every CSV row through the proposed API in time order.
    for index, row in df.iterrows():
        measurement = {
            "bandwidth": float(row["Bandwidth_Mbps"]),
            "latency": float(row["Latency_ms"]),
            "cpu_usage": float(row["CPU_Usage_percent"]),
            "task_size": float(row["Task_Size_MB"]),
        }

        # Existing method uses current latency and fixed thresholds.
        existing_decision = existing_heuristic_decision(
            measurement["latency"],
            measurement["cpu_usage"],
            measurement["task_size"],
        )

        # Proposed method receives the same row through the API.
        api_response = requests.post(
            f"{API_URL}/realtime/measure",
            json=measurement,
            timeout=60,
        )
        api_response.raise_for_status()
        proposed_result = api_response.json()

        proposed_decision = proposed_result.get("recommended_execution")

        # API only returns a proposed decision after it has 10 observations.
        results.append({
            "Time": row["Time"],
            "Scenario": row["Scenario"],
            "Bandwidth_Mbps": measurement["bandwidth"],
            "Latency_ms": measurement["latency"],
            "CPU_Usage_percent": measurement["cpu_usage"],
            "Task_Size_MB": measurement["task_size"],
            "Existing_Decision": existing_decision,
            "Proposed_Decision": proposed_decision,
            "Proposed_Status": proposed_result.get("status"),
            "Proposed_Predicted_Latency_ms": proposed_result.get(
                "predicted_latency"
            ),
        })

        print(
            f"Row {index + 1}/{len(df)} | "
            f"Existing: {existing_decision} | "
            f"Proposed: {proposed_decision or 'Collecting first 10 rows'}"
        )

        # Small pause between API requests.
        time.sleep(0.05)

    results_df = pd.DataFrame(results)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)

    # Compare only rows where the proposed system produced a decision.
    comparable = results_df.dropna(subset=["Proposed_Decision"]).copy()

    if comparable.empty:
        print(
            "\nNo proposed decisions were returned. Check the API output "
            "and confirm the dataset contains at least 10 valid rows."
        )
        print(f"Raw results saved to: {OUTPUT_CSV}")
        return

    # Fair decision-count comparison on the same rows.
    counts = pd.DataFrame({
        "Existing heuristic": comparable["Existing_Decision"].value_counts(),
        "Proposed LSTM": comparable["Proposed_Decision"].value_counts(),
    }).reindex(["EDGE", "CLOUD"], fill_value=0)

    os.makedirs(os.path.dirname(OUTPUT_GRAPH), exist_ok=True)

    ax = counts.plot(kind="bar", rot=0)
    ax.set_title("Existing Heuristic vs Proposed LSTM: Decisions")
    ax.set_xlabel("Execution location")
    ax.set_ylabel("Number of tasks")
    ax.legend(title="Method")
    plt.tight_layout()
    plt.savefig(OUTPUT_GRAPH, dpi=200)
    plt.close()

    print("\nComparison completed.")
    print(f"Rows in dataset: {len(df)}")
    print(f"Rows compared after LSTM warm-up: {len(comparable)}")
    print("\nDecision counts on the same rows:")
    print(counts)
    print(f"\nResults CSV: {OUTPUT_CSV}")
    print(f"Graph: {OUTPUT_GRAPH}")
    print(
        "\nNote: this graph compares decisions only. It does not measure "
        "latency reduction or speed improvement."
    )


if __name__ == "__main__":
    main()