def make_offloading_decision(
    predicted_latency,
    cpu_usage,
    task_size
):

    score = 0

    # High latency
    if predicted_latency > 100:
        score += 2
    elif predicted_latency > 50:
        score += 1

    # High CPU load
    if cpu_usage > 70:
        score += 2
    elif cpu_usage > 50:
        score += 1

    # Large task
    if task_size > 7:
        score += 2
    elif task_size > 4:
        score += 1

    if score >= 3:
        return "CLOUD"
    else:
        return "EDGE"