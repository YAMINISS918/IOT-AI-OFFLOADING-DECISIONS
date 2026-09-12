import numpy as np


def analyze_network(network_history):

    # Need enough records
    if len(network_history) < 5:
        return {
            "condition": "INSUFFICIENT_DATA",
            "average_latency": 0,
            "latency_variation": 0,
            "average_bandwidth": 0
        }

    # Extract values
    bandwidths = [record[0] for record in network_history]
    latencies = [record[1] for record in network_history]

    # Calculate statistics
    avg_bandwidth = np.mean(bandwidths)
    avg_latency = np.mean(latencies)

    latency_std = np.std(latencies)

    # ======================================
    # NETWORK CONDITION CLASSIFICATION
    # ======================================

    # Congested Network
    if avg_latency > 100 or avg_bandwidth < 25:

        condition = "CONGESTED"

    # Fluctuating Network
    elif latency_std > 20:

        condition = "FLUCTUATING"

    # Stable Network
    else:

        condition = "STABLE"


    return {

        "condition": condition,

        "average_latency": round(
            float(avg_latency),
            2
        ),

        "latency_variation": round(
            float(latency_std),
            2
        ),

        "average_bandwidth": round(
            float(avg_bandwidth),
            2
        )
    }