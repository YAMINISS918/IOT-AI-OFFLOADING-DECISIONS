
from statistics import pstdev


def detect_network_status(history, predicted_latency):
    if len(history) < 10:
        return {
            "status": "COLLECTING DATA",
            "recommendation": "WAIT",
            "reasons": [
                f"Need 10 records; currently have {len(history)}"
            ]
        }

    recent = history[-10:]

    # Your api.py stores records as:
    # [bandwidth, latency, cpu, task_size]
    bandwidths = [float(r[0]) for r in recent]
    latencies = [float(r[1]) for r in recent]

    current_bandwidth = bandwidths[-1]
    latency_variation = pstdev(latencies)

    reasons = []
    critical = False
    warning = False

    if predicted_latency > 150:
        critical = True
        reasons.append("Predicted latency is very high")
    elif predicted_latency > 100:
        warning = True
        reasons.append("Predicted latency is elevated")

    if current_bandwidth < 2:
        critical = True
        reasons.append("Bandwidth is critically low")
    elif current_bandwidth < 5:
        warning = True
        reasons.append("Bandwidth is low")

    if latency_variation > 50:
        critical = True
        reasons.append("Latency is highly unstable")
    elif latency_variation > 25:
        warning = True
        reasons.append("Latency is fluctuating")

    average_bandwidth = sum(bandwidths) / len(bandwidths)

    if (
        average_bandwidth > 0
        and current_bandwidth < average_bandwidth * 0.5
    ):
        warning = True
        reasons.append("Bandwidth dropped significantly")

    if critical:
        status = "CRITICAL"
        recommendation = "EDGE"
    elif warning:
        status = "WARNING"
        recommendation = "CHECK NETWORK"
    else:
        status = "NORMAL"
        recommendation = "USE EXISTING DECISION ENGINE"
        reasons.append("No degradation detected")

    return {
        "status": status,
        "recommendation": recommendation,
        "current_bandwidth_mbps": round(current_bandwidth, 2),
        "predicted_latency_ms": round(float(predicted_latency), 2),
        "latency_variation_ms": round(latency_variation, 2),
        "reasons": reasons
    }
