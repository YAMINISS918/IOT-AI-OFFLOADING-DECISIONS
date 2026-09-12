from cctv_offloading_manager import process_cctv_system
import time


for i in range(12):

    result = process_cctv_system()

    print("\n================================")
    print(f"ITERATION: {i + 1}")
    print("================================")

    print("Status:", result["status"])

    if result["status"] == "collecting_data":

        print(
            "Collecting:",
            result["records_collected"],
            "/",
            result["records_needed"]
        )

    else:

        print(
            "Predicted Latency:",
            result["predicted_latency"],
            "ms"
        )

        print("\nCCTV OFFLOADING DECISIONS")

        for camera in result["camera_results"]:

            print(
                camera["camera_id"],
                "|",
                camera["location"],
                "|",
                camera["priority"],
                "|",
                camera["decision"]
            )

    time.sleep(1)