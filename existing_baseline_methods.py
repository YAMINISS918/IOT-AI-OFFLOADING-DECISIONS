import pandas as pd
import os


# =========================================================
# EXISTING SYSTEM - HEURISTIC BASELINE
# =========================================================
# This represents a traditional static-threshold
# edge-cloud offloading approach.
#
# IMPORTANT:
# It uses CURRENT latency.
# It does NOT use LSTM prediction.
# =========================================================


DATASET_PATH = "data/raw/network_dataset.csv"
OUTPUT_PATH = "data/existing_baseline_results.csv"


def existing_heuristic_decision(latency, cpu_usage, task_size):

    score = 0
    reasons = []

    # -----------------------------------------------------
    # CURRENT LATENCY
    # -----------------------------------------------------
    if latency > 100:
        score += 2
        reasons.append("High current latency")

    elif latency > 50:
        score += 1
        reasons.append("Moderate current latency")

    else:
        reasons.append("Low current latency")

    # -----------------------------------------------------
    # CPU USAGE
    # -----------------------------------------------------
    if cpu_usage > 70:
        score += 2
        reasons.append("High CPU utilization")

    elif cpu_usage > 50:
        score += 1
        reasons.append("Moderate CPU utilization")

    else:
        reasons.append("Low CPU utilization")

    # -----------------------------------------------------
    # TASK SIZE
    # -----------------------------------------------------
    if task_size > 7:
        score += 2
        reasons.append("Large computational task")

    elif task_size > 4:
        score += 1
        reasons.append("Medium computational task")

    else:
        reasons.append("Small computational task")

    # -----------------------------------------------------
    # FINAL DECISION
    # -----------------------------------------------------
    if score >= 3:
        decision = "CLOUD"
    else:
        decision = "EDGE"

    return decision, score, "; ".join(reasons)


def main():

    print("=" * 60)
    print("EXISTING SYSTEM - HEURISTIC BASELINE")
    print("=" * 60)

    # -----------------------------------------------------
    # CHECK DATASET
    # -----------------------------------------------------
    if not os.path.exists(DATASET_PATH):

        print()
        print("ERROR: Dataset not found.")
        print(f"Expected location: {DATASET_PATH}")
        return

    # -----------------------------------------------------
    # LOAD DATASET
    # -----------------------------------------------------
    df = pd.read_csv(DATASET_PATH)

    print()
    print("Dataset loaded successfully.")
    print(f"Number of records: {len(df)}")

    # -----------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # -----------------------------------------------------
    required_columns = [
        "Time",
        "Scenario",
        "Bandwidth_Mbps",
        "Latency_ms",
        "CPU_Usage_percent",
        "Task_Size_MB"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print()
        print("ERROR: Missing columns:")
        print(missing_columns)

        print()
        print("Available columns:")
        print(df.columns.tolist())

        return

    # -----------------------------------------------------
    # APPLY EXISTING HEURISTIC METHOD
    # -----------------------------------------------------

    results = []

    for _, row in df.iterrows():

        latency = float(row["Latency_ms"])
        cpu_usage = float(row["CPU_Usage_percent"])
        task_size = float(row["Task_Size_MB"])

        decision, score, reasons = existing_heuristic_decision(
            latency,
            cpu_usage,
            task_size
        )

        results.append({
            "Time": row["Time"],
            "Scenario": row["Scenario"],
            "Bandwidth_Mbps": row["Bandwidth_Mbps"],
            "Latency_ms": latency,
            "CPU_Usage_percent": cpu_usage,
            "Task_Size_MB": task_size,
            "Existing_Decision": decision,
            "Decision_Score": score,
            "Reasons": reasons
        })

    # -----------------------------------------------------
    # CREATE RESULTS DATAFRAME
    # -----------------------------------------------------

    results_df = pd.DataFrame(results)

    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    results_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # DISPLAY SUMMARY
    # -----------------------------------------------------

    total = len(results_df)

    edge_count = (
        results_df["Existing_Decision"] == "EDGE"
    ).sum()

    cloud_count = (
        results_df["Existing_Decision"] == "CLOUD"
    ).sum()

    print()
    print("=" * 60)
    print("EXISTING SYSTEM RESULTS")
    print("=" * 60)

    print(f"Total tasks       : {total}")
    print(f"EDGE decisions    : {edge_count}")
    print(f"CLOUD decisions   : {cloud_count}")

    if total > 0:

        edge_percentage = (edge_count / total) * 100
        cloud_percentage = (cloud_count / total) * 100

        print(
            f"EDGE percentage   : {edge_percentage:.2f}%"
        )

        print(
            f"CLOUD percentage  : {cloud_percentage:.2f}%"
        )

    print()
    print("First 10 results:")
    print()

    print(
        results_df[
            [
                "Time",
                "Scenario",
                "Latency_ms",
                "CPU_Usage_percent",
                "Task_Size_MB",
                "Existing_Decision"
            ]
        ].head(10).to_string(index=False)
    )

    print()
    print("=" * 60)
    print("Results saved to:")
    print(OUTPUT_PATH)
    print("=" * 60)


if __name__ == "__main__":
    main()