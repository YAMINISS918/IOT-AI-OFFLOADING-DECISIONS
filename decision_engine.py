
def make_offloading_decision(predicted_latency, cpu_usage, task_size):
    score = 0
    reasons = []

    # 1. Network latency
    if predicted_latency > 150:
        score -= 2
        reasons.append(
            "Very high predicted network latency — avoid offloading"
        )
    elif predicted_latency > 80:
        score -= 1
        reasons.append(
            "High predicted network latency — offloading is risky"
        )
    else:
        reasons.append(
            "Low or moderate predicted network latency"
        )

    # 2. Device CPU utilization
    if cpu_usage > 85:
        score += 2
        reasons.append(
            "Very high CPU utilization — device is overloaded"
        )
    elif cpu_usage > 65:
        score += 1
        reasons.append("High CPU utilization")
    else:
        reasons.append(
            "Low or moderate CPU utilization — device can handle work locally"
        )

    # 3. Task size
    if task_size > 10:
        score += 2
        reasons.append(
            "Very large computational task — cloud computing may help"
        )
    elif task_size > 6:
        score += 1
        reasons.append("Large computational task")
    else:
        reasons.append(
            "Small or medium task — edge processing may be sufficient"
        )

    # 4. Final basic decision
    if predicted_latency > 150:
        decision = "EDGE"
        reasons.append(
            "Safety override: high latency prevents cloud offloading"
        )
    else:
        decision = "CLOUD" if score >= 2 else "EDGE"

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons
    }


def make_adaptive_offloading_decision(
    predicted_latency,
    cpu_usage,
    task_size,
    network_condition="STABLE",
    task_priority="normal",
    data_is_fresh=True,
    prediction_error_ms=None,
    edge_available=True,
):
    reasons = []

    # 1. Check prediction reliability
    unreliable = not data_is_fresh

    if (
        prediction_error_ms is not None
        and prediction_error_ms > 30
    ):
        unreliable = True

    if unreliable:
        reasons.append(
            "Prediction reliability warning: use a cautious decision"
        )
    else:
        reasons.append(
            "Network data and prediction pass the reliability checks"
        )

    # 2. Normalize network condition and task priority
    network_condition = str(network_condition).strip().upper()
    task_priority = str(task_priority).strip().lower()

    network_unstable = network_condition == "UNSTABLE"

    if network_unstable:
        reasons.append(
            "Network condition is UNSTABLE: avoid CLOUD offloading"
        )

    # 3. Handle edge-device unavailability first
    if not edge_available:
        reasons.append("Edge device is unavailable")

        # If conditions require EDGE, do not silently send to CLOUD.
        if (
            unreliable
            or predicted_latency > 150
            or network_unstable
            or task_priority == "urgent"
        ):
            return {
                "decision": "NO_SAFE_DESTINATION",
                "status": "WARNING",
                "reasons": reasons + [
                    "EDGE is unavailable and current conditions do not "
                    "safely support automatic CLOUD offloading"
                ]
            }

        # EDGE is unavailable; use the basic decision to assess CLOUD.
        result = make_offloading_decision(
            predicted_latency,
            cpu_usage,
            task_size
        )

        if result["decision"] == "EDGE":
            return {
                "decision": "NO_SAFE_DESTINATION",
                "status": "WARNING",
                "reasons": reasons + result["reasons"] + [
                    "EDGE was recommended but is unavailable"
                ]
            }

        return {
            "decision": "CLOUD",
            "status": "WARNING",
            "reasons": reasons + result["reasons"] + [
                "Using CLOUD because EDGE is unavailable"
            ]
        }

    # 4. Adaptive decision when EDGE is available
    if unreliable:
        decision = "EDGE"
        reasons.append(
            "Fallback: use EDGE because prediction reliability is uncertain"
        )

    elif predicted_latency > 150:
        decision = "EDGE"
        reasons.append(
            "High predicted latency: avoid cloud offloading"
        )

    elif network_unstable:
        decision = "EDGE"
        reasons.append(
            "Adaptive safety rule: unstable network selects EDGE"
        )

    elif task_priority == "urgent":
        decision = "EDGE"
        reasons.append(
            "Urgent task: prefer nearby processing"
        )

    else:
        result = make_offloading_decision(
            predicted_latency,
            cpu_usage,
            task_size
        )

        decision = result["decision"]
        reasons.extend(result["reasons"])

    # 5. Return the complete result
    return {
        "decision": decision,
        "status": "WARNING" if unreliable else "NORMAL",
        "reasons": reasons
    }


# 6. Run basic tests when this file is executed directly
if __name__ == "__main__":

    test_cases = [
        {
            "name": "Normal network",
            "predicted_latency": 50,
            "cpu_usage": 40,
            "task_size": 2,
            "network_condition": "STABLE",
            "task_priority": "normal",
            "data_is_fresh": True,
            "prediction_error_ms": 5,
            "edge_available": True,
        },
        {
            "name": "Unstable network",
            "predicted_latency": 70,
            "cpu_usage": 90,
            "task_size": 12,
            "network_condition": "UNSTABLE",
            "task_priority": "normal",
            "data_is_fresh": True,
            "prediction_error_ms": 5,
            "edge_available": True,
        },
        {
            "name": "Unreliable prediction",
            "predicted_latency": 50,
            "cpu_usage": 40,
            "task_size": 2,
            "network_condition": "STABLE",
            "task_priority": "normal",
            "data_is_fresh": False,
            "prediction_error_ms": 5,
            "edge_available": True,
        },
        {
            "name": "Edge unavailable",
            "predicted_latency": 50,
            "cpu_usage": 40,
            "task_size": 2,
            "network_condition": "STABLE",
            "task_priority": "normal",
            "data_is_fresh": True,
            "prediction_error_ms": 5,
            "edge_available": False,
        },
        {
            "name": "Urgent task",
            "predicted_latency": 50,
            "cpu_usage": 40,
            "task_size": 2,
            "network_condition": "STABLE",
            "task_priority": "urgent",
            "data_is_fresh": True,
            "prediction_error_ms": 5,
            "edge_available": True,
        },
    ]

    for test in test_cases:
        name = test.pop("name")
        result = make_adaptive_offloading_decision(**test)

        print("\n" + "=" * 45)
        print("TEST:", name)
        print("Decision:", result["decision"])
        print("Status:", result["status"])
        print("Reasons:")

        for reason in result["reasons"]:
            print("-", reason)
