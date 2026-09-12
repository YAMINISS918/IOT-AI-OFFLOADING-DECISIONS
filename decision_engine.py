def make_offloading_decision(predicted_latency, cpu_usage, task_size):

    score = 0
    reasons = []

    # Predicted latency factor
    if predicted_latency > 100:
        score += 2
        reasons.append("High predicted network latency")
    elif predicted_latency > 50:
        score += 1
        reasons.append("Moderate predicted network latency")
    else:
        reasons.append("Low predicted network latency")

    # CPU usage factor
    if cpu_usage > 70:
        score += 2
        reasons.append("High CPU utilization")
    elif cpu_usage > 50:
        score += 1
        reasons.append("Moderate CPU utilization")
    else:
        reasons.append("Low CPU utilization")

    # Task size factor
    if task_size > 7:
        score += 2
        reasons.append("Large computational task")
    elif task_size > 4:
        score += 1
        reasons.append("Medium computational task")
    else:
        reasons.append("Small computational task")

    # Final decision
    if score >= 3:
        decision = "CLOUD"
    else:
        decision = "EDGE"

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons
    }