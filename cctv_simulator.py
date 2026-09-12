import random


# ==========================================
# CCTV CAMERA CONFIGURATION
# ==========================================

CAMERAS = [
    {
        "camera_id": "CCTV_01",
        "location": "Main Entrance",
        "priority": "HIGH"
    },
    {
        "camera_id": "CCTV_02",
        "location": "Parking Area",
        "priority": "MEDIUM"
    },
    {
        "camera_id": "CCTV_03",
        "location": "Lobby",
        "priority": "HIGH"
    },
    {
        "camera_id": "CCTV_04",
        "location": "Corridor",
        "priority": "LOW"
    },
    {
        "camera_id": "CCTV_05",
        "location": "Storage Room",
        "priority": "MEDIUM"
    }
]


# ==========================================
# GENERATE CCTV TASK
# ==========================================

def generate_cctv_task(camera):

    # Simulated video processing task size
    task_size = random.randint(1, 10)

    # Video resolution
    resolution = random.choice([
        "720p",
        "1080p",
        "4K"
    ])

    # Simulated frame batch
    frame_count = random.randint(
        20,
        100
    )

    return {

        "camera_id": camera["camera_id"],

        "location": camera["location"],

        "priority": camera["priority"],

        "task_size": task_size,

        "resolution": resolution,

        "frame_count": frame_count
    }


# ==========================================
# GENERATE SIMULTANEOUS CCTV TASKS
# ==========================================

def generate_all_cctv_tasks():

    tasks = []

    for camera in CAMERAS:

        task = generate_cctv_task(
            camera
        )

        tasks.append(task)

    return tasks