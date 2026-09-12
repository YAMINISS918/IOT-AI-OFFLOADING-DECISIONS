import psutil
import platform
import subprocess
import time


# ============================================================
# NETWORK LATENCY
# ============================================================

def get_network_latency(host="8.8.8.8"):

    try:

        system = platform.system()

        if system == "Windows":

            command = [
                "ping",
                "-n",
                "1",
                "-w",
                "1000",
                host
            ]

        else:

            command = [
                "ping",
                "-c",
                "1",
                "-W",
                "1",
                host
            ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.returncode != 0:
            return None

        output = result.stdout

        # ----------------------------------------------------
        # Windows: time=XXms
        # Linux: time=XX ms
        # ----------------------------------------------------

        import re

        match = re.search(
            r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms",
            output,
            re.IGNORECASE
        )

        if match:

            return float(
                match.group(1)
            )

        return None

    except Exception:

        return None


# ============================================================
# NETWORK TRAFFIC
# ============================================================

def get_network_throughput():

    try:

        first = psutil.net_io_counters()

        time.sleep(0.5)

        second = psutil.net_io_counters()

        bytes_sent = (
            second.bytes_sent -
            first.bytes_sent
        )

        bytes_received = (
            second.bytes_recv -
            first.bytes_recv
        )

        total_bytes = (
            bytes_sent +
            bytes_received
        )

        # Bytes → Megabits
        mbps = (
            total_bytes * 8
        ) / (
            0.5 * 1024 * 1024
        )

        return round(
            mbps,
            2
        )

    except Exception:

        return 0.0


# ============================================================
# REAL-TIME DEVICE DATA
# ============================================================

def get_realtime_data(task_size=0.01):

    # --------------------------------------------------------
    # CPU
    # --------------------------------------------------------

    cpu_usage = psutil.cpu_percent(
        interval=0.3
    )


    # --------------------------------------------------------
    # RAM
    # --------------------------------------------------------

    memory_usage = psutil.virtual_memory().percent


    # --------------------------------------------------------
    # STORAGE
    # --------------------------------------------------------

    try:

        storage = psutil.disk_usage("C:/")

        available_storage_gb = (
            storage.free /
            (1024 ** 3)
        )

    except Exception:

        available_storage_gb = 0.0


    # --------------------------------------------------------
    # NETWORK THROUGHPUT
    # --------------------------------------------------------

    bandwidth = get_network_throughput()


    # --------------------------------------------------------
    # NETWORK LATENCY
    # --------------------------------------------------------

    latency = get_network_latency()


    return {

        "cpu_usage":
            round(cpu_usage, 2),

        "memory_usage":
            round(memory_usage, 2),

        "available_storage_gb":
            round(
                available_storage_gb,
                2
            ),

        "bandwidth":
            round(
                bandwidth,
                2
            ),

        "latency":
            latency,

        "task_size":
            round(
                float(task_size),
                2
            )
    }