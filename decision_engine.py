def make_offloading_decision(predicted_latency, cpu_usage, task_size):

    score = 0          # positive → CLOUD, negative → EDGE
    reasons = []

    # --- Predicted network latency (VETO signal only — never earns CLOUD points) ---
    if predicted_latency > 150:
        score -= 2
        reasons.append("Very high predicted network latency — avoid offloading")
    elif predicted_latency > 80:
        score -= 1
        reasons.append("High predicted network latency — offloading is risky")
    else:
        reasons.append("Low or moderate predicted network latency — network can support offloading")
        # no score change: a healthy network is not, by itself, a reason to offload

    # --- CPU usage (reason TO offload) ---
    if cpu_usage > 85:
        score += 2
        reasons.append("Very high CPU utilization — device is overloaded")
    elif cpu_usage > 65:
        score += 1
        reasons.append("High CPU utilization")
    else:
        reasons.append("Low or moderate CPU utilization — device can handle it locally")
        # no score change: normal CPU load isn't a reason to send work away

    # --- Task size (reason TO offload) ---
    if task_size > 10:
        score += 2
        reasons.append("Very large computational task — needs cloud-scale compute")
    elif task_size > 6:
        score += 1
        reasons.append("Large computational task")
    else:
        reasons.append("Small or medium computational task — edge is sufficient")
        # no score change: a small task isn't itself evidence the edge can't handle it

    # --- Hard override: never send to cloud over a badly degraded network ---
    if predicted_latency > 150:
        decision = "EDGE"
        reasons.append("Override: network too degraded for cloud offloading regardless of other factors")
    else:
        decision = "CLOUD" if score >= 2 else "EDGE"

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons
    }


# ------------------------------------------------------------------------
# Self-test
# ------------------------------------------------------------------------
if __name__ == "__main__":
    scenarios = [
        ("Everything fine, light task", 60, 40, 3),
        ("Healthy network, heavy CPU + large task", 60, 90, 12),
        ("Elevated latency, otherwise light", 100, 50, 3),
        ("Moderate latency, moderate load", 50, 70, 7),
        ("Very high latency, big task (override case)", 184.05, 33.6, 44.95),
    ]

    for label, latency, cpu, task in scenarios:
        result = make_offloading_decision(latency, cpu, task)
        print(f"\n--- {label} ---")
        print(f"  latency={latency}, cpu={cpu}, task={task}MB")
        print(f"  → decision={result['decision']}  score={result['score']}")
        for r in result["reasons"]:
            print(f"    • {r}")
