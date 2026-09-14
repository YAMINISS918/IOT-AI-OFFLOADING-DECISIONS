import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# FILES
# ---------------------------------------------------------
INPUT_CSV = "data/comparison_results.csv"
OUTPUT_CSV = "data/performance_simulation_results.csv"
SUMMARY_CSV = "data/performance_simulation_summary.csv"
OUTPUT_GRAPH = "data/graphs/estimated_latency_comparison.png"

# ---------------------------------------------------------
# SIMULATION ASSUMPTIONS
# Replace these with values measured on your own setup
# before reporting performance as a project finding.
# ---------------------------------------------------------
EDGE_BASE_COMPUTE_MS_PER_MB = 80.0
CLOUD_BASE_COMPUTE_MS_PER_MB = 20.0

# Illustrative impact of CPU utilization on compute time.
EDGE_CPU_IMPACT = 1.5
CLOUD_CPU_IMPACT = 0.2

# Assumption: the network latency column represents the
# network delay for the cloud request. This model includes
# input upload time, but not output download time.
# ---------------------------------------------------------


def estimate_edge_latency(task_size_mb, cpu_usage):
    """Estimate completion time when the task runs on EDGE."""
    cpu_factor = 1.0 + EDGE_CPU_IMPACT * (cpu_usage / 100.0)

    return (
        task_size_mb
        * EDGE_BASE_COMPUTE_MS_PER_MB
        * cpu_factor
    )


def estimate_cloud_latency(
    task_size_mb,
    bandwidth_mbps,
    network_latency_ms,
    cpu_usage,
):
    """Estimate completion time when the task runs on CLOUD."""
    if pd.isna(bandwidth_mbps) or bandwidth_mbps <= 0:
        return float("nan")

    upload_time_ms = (task_size_mb * 8.0 / bandwidth_mbps) * 1000.0

    cpu_factor = 1.0 + CLOUD_CPU_IMPACT * (cpu_usage / 100.0)

    cloud_compute_ms = (
        task_size_mb
        * CLOUD_BASE_COMPUTE_MS_PER_MB
        * cpu_factor
    )

    return network_latency_ms + upload_time_ms + cloud_compute_ms


def choose_estimated_latency(decision, edge_ms, cloud_ms):
    """Return the estimated latency for a method's decision."""
    decision = str(decision).strip().upper()

    if decision == "EDGE":
        return edge_ms
    if decision == "CLOUD":
        return cloud_ms

    return float("nan")


def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(
            f"Could not find {INPUT_CSV}. "
            "Run compare_existing_vs_proposed.py first."
        )

    df = pd.read_csv(INPUT_CSV)

    required_columns = [
        "Time",
        "Scenario",
        "Bandwidth_Mbps",
        "Latency_ms",
        "CPU_Usage_percent",
        "Task_Size_MB",
        "Existing_Decision",
        "Proposed_Decision",
    ]

    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    # Keep only rows where both methods made a decision.
    # This excludes the LSTM warm-up rows.
    df = df.dropna(
        subset=["Existing_Decision", "Proposed_Decision"]
    ).copy()

    if df.empty:
        raise ValueError("No rows have decisions from both methods.")

    # Convert numeric input columns safely.
    numeric_columns = [
        "Bandwidth_Mbps",
        "Latency_ms",
        "CPU_Usage_percent",
        "Task_Size_MB",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove rows with missing or invalid required measurements.
    df = df.dropna(subset=numeric_columns).copy()
    df = df[
        (df["Bandwidth_Mbps"] > 0)
        & (df["Task_Size_MB"] >= 0)
        & (df["CPU_Usage_percent"] >= 0)
    ].copy()

    if df.empty:
        raise ValueError("No valid rows remain after input validation.")

    results = []

    for _, row in df.iterrows():
        task_size = float(row["Task_Size_MB"])
        bandwidth = float(row["Bandwidth_Mbps"])
        network_latency = float(row["Latency_ms"])
        cpu_usage = float(row["CPU_Usage_percent"])

        edge_ms = estimate_edge_latency(task_size, cpu_usage)

        cloud_ms = estimate_cloud_latency(
            task_size_mb=task_size,
            bandwidth_mbps=bandwidth,
            network_latency_ms=network_latency,
            cpu_usage=cpu_usage,
        )

        existing_decision = str(row["Existing_Decision"]).strip().upper()
        proposed_decision = str(row["Proposed_Decision"]).strip().upper()

        existing_estimated_ms = choose_estimated_latency(
            existing_decision, edge_ms, cloud_ms
        )
        proposed_estimated_ms = choose_estimated_latency(
            proposed_decision, edge_ms, cloud_ms
        )

        results.append({
            "Time": row["Time"],
            "Scenario": row["Scenario"],
            "Bandwidth_Mbps": bandwidth,
            "Input_Network_Latency_ms": network_latency,
            "CPU_Usage_percent": cpu_usage,
            "Task_Size_MB": task_size,
            "Existing_Decision": existing_decision,
            "Proposed_Decision": proposed_decision,
            "Estimated_EDGE_Latency_ms": edge_ms,
            "Estimated_CLOUD_Latency_ms": cloud_ms,
            "Existing_Estimated_Latency_ms": existing_estimated_ms,
            "Proposed_Estimated_Latency_ms": proposed_estimated_ms,
        })

    results_df = pd.DataFrame(results)

    # Exclude rows where a valid estimated latency could not be calculated.
    results_df = results_df.dropna(
        subset=[
            "Existing_Estimated_Latency_ms",
            "Proposed_Estimated_Latency_ms",
        ]
    ).copy()

    if results_df.empty:
        raise ValueError("No rows have valid estimated latencies for both methods.")

    # -----------------------------------------------------
    # SAVE PER-ROW RESULTS
    # -----------------------------------------------------
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/graphs", exist_ok=True)

    results_df.to_csv(OUTPUT_CSV, index=False)

    # -----------------------------------------------------
    # SUMMARY BY NETWORK SCENARIO
    # -----------------------------------------------------
    summary = (
        results_df.groupby("Scenario")
        .agg(
            Rows_Evaluated=("Scenario", "size"),
            Existing_Mean_Latency_ms=("Existing_Estimated_Latency_ms", "mean"),
            Proposed_Mean_Latency_ms=("Proposed_Estimated_Latency_ms", "mean"),
        )
        .reset_index()
    )

    summary["Estimated_Improvement_percent"] = (
        (
            summary["Existing_Mean_Latency_ms"]
            - summary["Proposed_Mean_Latency_ms"]
        )
        / summary["Existing_Mean_Latency_ms"]
        * 100.0
    )

    summary.to_csv(SUMMARY_CSV, index=False)

    # -----------------------------------------------------
    # GRAPH
    # -----------------------------------------------------
    plot_data = summary.set_index("Scenario")[
        [
            "Existing_Mean_Latency_ms",
            "Proposed_Mean_Latency_ms",
        ]
    ]

    ax = plot_data.plot(kind="bar", rot=0)
    ax.set_title("Existing vs Proposed: Estimated Latency")
    ax.set_xlabel("Network scenario")
    ax.set_ylabel("Mean estimated completion latency (ms)")
    ax.legend(["Existing heuristic", "Proposed LSTM"])
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    plt.tight_layout()
    plt.savefig(OUTPUT_GRAPH, dpi=200)
    plt.close()

    # -----------------------------------------------------
    # CONSOLE REPORT
    # -----------------------------------------------------
    existing_mean = results_df["Existing_Estimated_Latency_ms"].mean()
    proposed_mean = results_df["Proposed_Estimated_Latency_ms"].mean()

    if existing_mean > 0:
        overall_improvement = (
            (existing_mean - proposed_mean) / existing_mean
        ) * 100.0
    else:
        overall_improvement = float("nan")

    print("\nSimulation completed.")
    print(f"Rows evaluated: {len(results_df)}")

    print("\nAverage estimated latency:")
    print(f"Existing heuristic: {existing_mean:.2f} ms")
    print(f"Proposed LSTM:      {proposed_mean:.2f} ms")
    print(f"Estimated change:   {overall_improvement:.2f}%")

    print("\nScenario-wise summary:")
    print(summary.round(2).to_string(index=False))

    print(f"\nResults CSV: {OUTPUT_CSV}")
    print(f"Summary CSV: {SUMMARY_CSV}")
    print(f"Graph: {OUTPUT_GRAPH}")

    print(
        "\nIMPORTANT: These are simulation estimates based on the "
        "compute-time assumptions at the top of this file. "
        "They are not measured execution times or proof of real-world improvement."
    )


if __name__ == "__main__":
    main()
    