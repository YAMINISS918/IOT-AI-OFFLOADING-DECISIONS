import psutil


def get_edge_resources():

    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=0.5)

    # RAM usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Storage
    disk = psutil.disk_usage("C:/")
    available_storage = disk.free / (1024 ** 3)

    return {
        "cpu_usage": round(cpu_usage, 2),

        "memory_usage": round(
            memory_usage,
            2
        ),

        # Current standard name
        "available_storage_gb": round(
            available_storage,
            2
        ),

        # Dashboard compatibility
        "available_storage": round(
            available_storage,
            2
        ),

        # Old CCTV compatibility
        "storage_available_gb": round(
            available_storage,
            2
        )
    }