import requests
import random
import time

scenarios = ["Stable", "Fluctuating", "Congested"]

while True:

    scenario = random.choice(scenarios)

    if scenario == "Stable":
        bandwidth = random.randint(70, 100)
        latency = random.randint(10, 30)
        cpu = random.randint(20, 40)

    elif scenario == "Fluctuating":
        bandwidth = random.randint(30, 70)
        latency = random.randint(30, 80)
        cpu = random.randint(40, 70)

    else:
        bandwidth = random.randint(5, 30)
        latency = random.randint(80, 200)
        cpu = random.randint(70, 95)

    task_size = random.randint(1, 10)

    data = {
        "bandwidth": bandwidth,
        "latency": latency,
        "cpu_usage": cpu,
        "task_size": task_size
    }

    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json=data
    )

    print(response.json())

    time.sleep(2)