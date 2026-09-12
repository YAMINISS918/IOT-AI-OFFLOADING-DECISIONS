from cctv_simulator import generate_all_cctv_tasks
from resource_monitor import get_edge_resources
from decision_engine import make_offloading_decision
from lstm_predictor import predict_future_latency

import random


# ==========================================
# STORE LAST 10 NETWORK STATES
# ==========================================

network_history = []


# ==========================================
# SIMULATE NETWORK CONDITION
# ==========================================

def get_network_condition():

    scenario = random.choice([
        "Stable",
        "Fluctuating",
        "Congested"
    ])

    if scenario == "Stable":

        bandwidth = random.randint(70, 100)
        latency = random.randint(10, 30)

    elif scenario == "Fluctuating":

        bandwidth = random.randint(30, 70)
        latency = random.randint(30, 80)

    else:

        bandwidth = random.randint(5, 30)
        latency = random.randint(80, 200)

    return {
        "scenario": scenario,
        "bandwidth": bandwidth,
        "latency": latency
    }


# ==========================================
# PROCESS CCTV SYSTEM
# ==========================================

def process_cctv_system():

    global network_history


    # --------------------------------------
    # GET CURRENT NETWORK CONDITION
    # --------------------------------------

    network = get_network_condition()


    # --------------------------------------
    # GET REAL EDGE RESOURCES
    # --------------------------------------

    edge_resources = get_edge_resources()


    # --------------------------------------
    # CREATE NETWORK STATE
    # --------------------------------------

    # Using average task size temporarily
    # for network history

    network_state = [

        network["bandwidth"],

        network["latency"],

        edge_resources["cpu_usage"],

        random.randint(1, 10)

    ]


    # --------------------------------------
    # STORE NETWORK HISTORY
    # --------------------------------------

    network_history.append(
        network_state
    )


    # Keep only latest 10 records

    if len(network_history) > 10:

        network_history.pop(0)


    # --------------------------------------
    # GENERATE CCTV TASKS
    # --------------------------------------

    cctv_tasks = generate_all_cctv_tasks()


    # --------------------------------------
    # WAIT FOR LSTM DATA
    # --------------------------------------

    if len(network_history) < 10:

        return {

            "status": "collecting_data",

            "records_collected":
                len(network_history),

            "records_needed": 10,

            "network":
                network,

            "edge_resources":
                edge_resources,

            "camera_results": []

        }


    # ======================================
    # REAL LSTM PREDICTION
    # ======================================

    predicted_latency = predict_future_latency(
        network_history
    )


    results = []


    # ======================================
    # PROCESS EACH CCTV CAMERA
    # ======================================

    for task in cctv_tasks:


        # Get CCTV task size

        task_size = task["task_size"]


        # ----------------------------------
        # MAKE OFFLOADING DECISION
        # ----------------------------------

        decision_result = make_offloading_decision(

            predicted_latency,

            edge_resources["cpu_usage"],

            task_size

        )


        # ----------------------------------
        # PRIORITY IMPROVEMENT
        # ----------------------------------

        # High priority cameras prefer EDGE
        # when possible for faster response

        decision = decision_result["decision"]


        if (
            task["priority"] == "HIGH"
            and predicted_latency < 80
            and edge_resources["cpu_usage"] < 85
        ):

            decision = "EDGE"


        # ----------------------------------
        # STORE CAMERA RESULT
        # ----------------------------------

        results.append({

            "camera_id":
                task["camera_id"],

            "location":
                task["location"],

            "priority":
                task["priority"],

            "resolution":
                task["resolution"],

            "frame_count":
                task["frame_count"],

            "task_size_mb":
                task_size,

            "bandwidth":
                network["bandwidth"],

            "current_latency":
                network["latency"],

            "predicted_latency":
                predicted_latency,

            "cpu_usage":
                edge_resources["cpu_usage"],

            "memory_usage":
                edge_resources["memory_usage"],

            "storage_available_gb":

    edge_resources[
        "available_storage_gb"
    ],
            "decision":
                decision,

            "score":
                decision_result["score"],

            "reasons":
                decision_result["reasons"]

        })


    # ======================================
    # RETURN COMPLETE SYSTEM STATUS
    # ======================================

    return {

        "status":
            "prediction_complete",

        "network":
            network,

        "edge_resources":
            edge_resources,

        "predicted_latency":
            predicted_latency,

        "camera_results":
            results

    }