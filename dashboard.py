import streamlit as st
import requests
import pandas as pd

from streamlit_autorefresh import st_autorefresh
from realtime_monitor import get_realtime_data
from cctv_offloading_manager import process_cctv_system
from resource_monitor import get_edge_resources


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="IoT Intelligent Offloading",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🤖 Intelligent IoT Edge-Cloud Offloading System"
)

st.markdown(
    "### Real-Time AI-Based Network Monitoring & Intelligent Offloading"
)

st.caption(
    "Real-time monitoring → LSTM prediction → EDGE/CLOUD recommendation"
)


# ============================================================
# SESSION STATE
# ============================================================

if "running" not in st.session_state:
    st.session_state.running = False

if "history" not in st.session_state:
    st.session_state.history = []

if "task_size" not in st.session_state:
    st.session_state.task_size = None

if "task_name" not in st.session_state:
    st.session_state.task_name = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ System Control")

mode = st.sidebar.radio(
    "Select Input Mode",
    [
        "Real-Time Monitoring",
        "Manual IoT Input",
        "CCTV Monitoring"
    ]
)


# ============================================================
# API BASE URL
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# REGISTER FILE WITH API
# ============================================================

def start_api_monitoring(uploaded_file):

    try:

        uploaded_file.seek(0)

        response = requests.post(

            f"{API_URL}/realtime/start",

            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                    or "application/octet-stream"
                )
            },

            timeout=30
        )


        response.raise_for_status()

        return response.json()


    except Exception as e:

        st.error(
            f"❌ Could not start API monitoring: {e}"
        )

        return None


# ============================================================
# SEND REAL-TIME MEASUREMENT
# ============================================================

def send_measurement(data):

    try:

        response = requests.post(

            f"{API_URL}/realtime/measure",

            json={

                "bandwidth":
                    float(data["bandwidth"]),

                "latency":
                    float(data["latency"]),

                "cpu_usage":
                    float(data["cpu_usage"]),

                "task_size":
                    float(data["task_size"])
            },

            timeout=10
        )


        response.raise_for_status()

        return response.json()


    except Exception as e:

        st.error(
            f"❌ Measurement API Error: {e}"
        )

        return None


# ============================================================
# RESET API
# ============================================================

def reset_api():

    try:

        requests.post(
            f"{API_URL}/realtime/reset",
            timeout=5
        )

    except Exception:
        pass


# ============================================================
# DISPLAY LIVE DATA
# ============================================================

def display_live_data(data):

    st.subheader(
        "📊 Live Device & Network Measurement"
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💻 CPU Usage",
            f"{data['cpu_usage']:.1f}%"
        )


    with col2:

        if data["latency"] is not None:

            st.metric(
                "⏱ Current Latency",
                f"{data['latency']:.2f} ms"
            )

        else:

            st.metric(
                "⏱ Current Latency",
                "Unavailable"
            )


    with col3:

        st.metric(
            "📶 Network Traffic",
            f"{data['bandwidth']:.2f} Mbps"
        )


    with col4:

        st.metric(
            "📦 Task Size",
            f"{data['task_size']:.2f} MB"
        )


    col5, col6 = st.columns(2)


    with col5:

        st.metric(
            "🧠 RAM Usage",
            f"{data['memory_usage']:.1f}%"
        )


    with col6:

        st.metric(
            "💾 Available Storage",
            f"{data['available_storage_gb']:.2f} GB"
        )


# ============================================================
# DISPLAY LSTM PROGRESS
# ============================================================

def display_lstm_progress(result):

    records = int(
        result.get(
            "records_collected",
            0
        )
    )

    required = int(
        result.get(
            "records_needed",
            10
        )
    )


    if result.get("status") == "collecting_data":

        st.divider()

        st.subheader(
            "🧠 LSTM Network History Collection"
        )

        st.warning(
            f"Collecting real-time observations: "
            f"**{records} / {required}**"
        )


        progress = (
            records / required
            if required > 0
            else 0
        )


        st.progress(
            min(
                progress,
                1.0
            )
        )


        # ----------------------------------------------------
        # Observation indicators
        # ----------------------------------------------------

        indicators = []

        for i in range(
            1,
            required + 1
        ):

            if i <= records:

                indicators.append(
                    f"🟢 {i}"
                )

            else:

                indicators.append(
                    f"⚪ {i}"
                )


        st.write(
            "   ".join(indicators)
        )


        st.info(
            "The LSTM requires 10 recent real-time "
            "network observations."
        )


        return


    if result.get("status") == "prediction_complete":

        st.divider()

        st.success(
            "✅ LSTM prediction completed using "
            "10 real-time observations."
        )


# ============================================================
# DISPLAY AI DECISION
# ============================================================

def display_decision(result):

    if result.get("status") != "prediction_complete":

        return


    predicted_latency = float(
        result.get(
            "predicted_latency",
            0
        )
    )


    decision = result.get(
        "recommended_execution",
        "UNKNOWN"
    )


    score = result.get(
        "decision_score",
        0
    )


    # ========================================================
    # AI DECISION
    # ========================================================

    st.header(
        "🤖 AI Offloading Decision"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "🔮 Predicted Future Latency",
            f"{predicted_latency:.2f} ms"
        )


    with col2:

        st.metric(
            "🎯 Decision Score",
            str(score)
        )


    # ========================================================
    # EDGE / CLOUD
    # ========================================================

    if decision == "EDGE":

        st.success(
            "🟢 RECOMMENDED EXECUTION: EDGE"
        )

        st.markdown(
            """
            <div style="
                padding:25px;
                border-radius:15px;
                text-align:center;
                border:2px solid #00c853;
            ">
                <h1>🟢 EXECUTE ON EDGE</h1>
                <p style="font-size:18px;">
                The AI recommends processing this
                IoT task on the Edge device.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


    elif decision == "CLOUD":

        st.info(
            "☁️ RECOMMENDED EXECUTION: CLOUD"
        )

        st.markdown(
            """
            <div style="
                padding:25px;
                border-radius:15px;
                text-align:center;
                border:2px solid #2196f3;
            ">
                <h1>☁️ OFFLOAD TO CLOUD</h1>
                <p style="font-size:18px;">
                The AI recommends sending this
                IoT task to the Cloud.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


    else:

        st.warning(
            f"Unknown decision: {decision}"
        )


    # ========================================================
    # NETWORK CONDITION
    # ========================================================

    st.subheader(
        "🌐 Network Condition"
    )


    network_condition = result.get(
        "network_condition",
        {}
    )


    if isinstance(
        network_condition,
        dict
    ):

        condition = network_condition.get(
            "condition",
            "UNKNOWN"
        )

        avg_latency = float(
            network_condition.get(
                "average_latency",
                0
            )
        )

        variation = float(
            network_condition.get(
                "latency_variation",
                0
            )
        )

        avg_bandwidth = float(
            network_condition.get(
                "average_bandwidth",
                0
            )
        )


        c1, c2, c3, c4 = st.columns(4)


        with c1:

            st.metric(
                "Condition",
                condition
            )


        with c2:

            st.metric(
                "Average Latency",
                f"{avg_latency:.2f} ms"
            )


        with c3:

            st.metric(
                "Latency Variation",
                f"{variation:.2f} ms"
            )


        with c4:

            st.metric(
                "Average Traffic",
                f"{avg_bandwidth:.2f} Mbps"
            )


    # ========================================================
    # REASONS
    # ========================================================

    st.subheader(
        "🧠 AI Decision Explanation"
    )


    reasons = result.get(
        "reasons",
        []
    )


    for reason in reasons:

        st.write(
            "•",
            reason
        )


# ============================================================
# SAVE HISTORY
# ============================================================

def save_history(data, result):

    if result.get(
        "status"
    ) != "prediction_complete":

        return


    predicted_latency = float(
        result.get(
            "predicted_latency",
            0
        )
    )


    decision = result.get(
        "recommended_execution",
        "UNKNOWN"
    )


    record = {

        "Bandwidth":
            data["bandwidth"],

        "Current Latency":
            data["latency"],

        "Predicted Latency":
            predicted_latency,

        "CPU Usage":
            data["cpu_usage"],

        "Task Size":
            data["task_size"],

        "Decision":
            decision
    }


    st.session_state.history.append(
        record
    )


# ============================================================
# REAL-TIME MONITORING MODE
# ============================================================

if mode == "Real-Time Monitoring":

    st.header(
        "📡 Real-Time Network Monitoring"
    )


    st.write(
        "Upload the IoT task once. "
        "The system then continuously monitors "
        "real-time device and network conditions."
    )


    # ========================================================
    # FILE UPLOAD
    # ========================================================

    uploaded_file = st.file_uploader(
        "📁 Upload IoT Task / File",
        type=None,
        key="realtime_file"
    )


    # ========================================================
    # FILE INFORMATION
    # ========================================================

    if uploaded_file is not None:

        file_size = (
            len(
                uploaded_file.getvalue()
            )
            /
            (1024 * 1024)
        )


        st.success(
            f"📦 **{uploaded_file.name}**  |  "
            f"Size: **{file_size:.2f} MB**"
        )


    else:

        file_size = None

        st.warning(
            "⚠️ Upload an IoT task/file first."
        )


    # ========================================================
    # START / STOP
    # ========================================================

    st.subheader(
        "🎛️ Monitoring Control"
    )


    col1, col2 = st.columns(2)


    with col1:

        start = st.button(
            "▶ Start Real-Time Monitoring",
            type="primary",
            use_container_width=True
        )


    with col2:

        stop = st.button(
            "⏹ Stop Monitoring",
            use_container_width=True
        )


    # ========================================================
    # START
    # ========================================================

    if start:

        if uploaded_file is None:

            st.error(
                "❌ Please upload an IoT task/file first."
            )

        else:

            # -----------------------------------------------
            # Register file with API ONCE
            # -----------------------------------------------

            start_result = start_api_monitoring(
                uploaded_file
            )


            if start_result is not None:

                st.session_state.running = True

                st.session_state.task_size = (
                    start_result.get(
                        "task_size_mb",
                        file_size
                    )
                )

                st.session_state.task_name = (
                    start_result.get(
                        "file_name",
                        uploaded_file.name
                    )
                )

                st.session_state.history = []

                st.session_state.last_result = None

                st.success(
                    "✅ Monitoring started. "
                    "The file was uploaded only once."
                )


    # ========================================================
    # STOP
    # ========================================================

    if stop:

        st.session_state.running = False

        reset_api()

        st.warning(
            "⏹ Real-Time Monitoring Stopped."
        )


    # ========================================================
    # ACTIVE MONITORING
    # ========================================================

    if st.session_state.running:

        st.success(
            f"🟢 Monitoring ACTIVE  |  "
            f"Task: {st.session_state.task_name}  |  "
            f"Size: {st.session_state.task_size:.2f} MB"
        )


        # ====================================================
        # AUTO REFRESH
        # ====================================================

        st_autorefresh(
            interval=2000,
            key="realtime_monitor_refresh"
        )


        # ====================================================
        # REAL-TIME DATA
        # ====================================================

        try:

            data = get_realtime_data(
                task_size=st.session_state.task_size
            )


            # ------------------------------------------------
            # DISPLAY ONLY LATEST MEASUREMENT
            # ------------------------------------------------

            display_live_data(
                data
            )


            # ------------------------------------------------
            # SEND ONLY SMALL JSON
            # ------------------------------------------------

            if data["latency"] is not None:

                result = send_measurement(
                    data
                )


                if result is not None:

                    st.session_state.last_result = result


                    # ----------------------------------------
                    # LSTM PROGRESS
                    # ----------------------------------------

                    display_lstm_progress(
                        result
                    )


                    # ----------------------------------------
                    # AI DECISION
                    # ----------------------------------------

                    display_decision(
                        result
                    )


                    # ----------------------------------------
                    # SAVE HISTORY
                    # ----------------------------------------

                    save_history(
                        data,
                        result
                    )


            else:

                st.error(
                    "❌ Network latency could not be measured."
                )


        except Exception as e:

            st.error(
                f"❌ Monitoring Error: {e}"
            )


    else:

        st.info(
            "⏸ Monitoring is stopped."
        )


# ============================================================
# MANUAL MODE
# ============================================================

elif mode == "Manual IoT Input":

    st.header(
        "🎛️ Manual IoT Device Input"
    )


    st.write(
        "Use this mode for testing different "
        "network and task conditions."
    )


    col1, col2 = st.columns(2)


    with col1:

        bandwidth = st.number_input(
            "Bandwidth (Mbps)",
            min_value=1.0,
            max_value=1000.0,
            value=50.0
        )


        latency = st.number_input(
            "Current Latency (ms)",
            min_value=0.0,
            max_value=10000.0,
            value=30.0
        )


    with col2:

        cpu_usage = st.number_input(
            "CPU Usage (%)",
            min_value=0.0,
            max_value=100.0,
            value=50.0
        )


        task_size = st.number_input(
            "Task Size (MB)",
            min_value=0.1,
            max_value=1000.0,
            value=5.0
        )


    if st.button(
        "🤖 Analyze & Predict",
        type="primary",
        use_container_width=True
    ):

        data = {

            "bandwidth":
                bandwidth,

            "latency":
                latency,

            "cpu_usage":
                cpu_usage,

            "task_size":
                task_size,

            "memory_usage":
                0,

            "available_storage_gb":
                0
        }


        # Send manual input to the /predict endpoint
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={
                    "bandwidth": float(bandwidth),
                    "latency": float(latency),
                    "cpu_usage": float(cpu_usage),
                    "task_size": float(task_size)
                },
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            if result.get("status") == "prediction_complete":
                st.success("✅ Prediction completed!")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "🔮 Predicted Future Latency",
                        f"{float(result.get('predicted_latency', 0)):.2f} ms"
                    )

                with col2:
                    st.metric(
                        "🎯 Decision Score",
                        str(result.get("decision_score", 0))
                    )

                decision = result.get(
                    "recommended_execution", "UNKNOWN"
                )

                if decision == "EDGE":
                    st.success("🟢 RECOMMENDED EXECUTION: EDGE")
                    st.markdown(
                        """
                        <div style="padding:25px;border-radius:15px;text-align:center;border:2px solid #00c853;">
                            <h1>🟢 EXECUTE ON EDGE</h1>
                            <p style="font-size:18px;">
                            The AI recommends processing this IoT task on the Edge device.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                elif decision == "CLOUD":
                    st.info("☁️ RECOMMENDED EXECUTION: CLOUD")
                    st.markdown(
                        """
                        <div style="padding:25px;border-radius:15px;text-align:center;border:2px solid #2196f3;">
                            <h1>☁️ OFFLOAD TO CLOUD</h1>
                            <p style="font-size:18px;">
                            The AI recommends sending this IoT task to the Cloud.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                network_condition = result.get("network_condition", {})

                if isinstance(network_condition, dict):
                    st.subheader("🌐 Network Condition")
                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        st.metric("Condition", network_condition.get("condition", "UNKNOWN"))

                    with c2:
                        st.metric(
                            "Average Latency",
                            f"{float(network_condition.get('average_latency', 0)):.2f} ms"
                        )

                    with c3:
                        st.metric(
                            "Latency Variation",
                            f"{float(network_condition.get('latency_variation', 0)):.2f} ms"
                        )

                    with c4:
                        st.metric(
                            "Average Traffic",
                            f"{float(network_condition.get('average_bandwidth', 0)):.2f} Mbps"
                        )

                st.subheader("🧠 AI Decision Explanation")

                for reason in result.get("reasons", []):
                    st.write("•", reason)

            else:
                st.error(result.get("message", "Prediction failed."))

        except Exception as e:
            st.error(f"❌ Prediction API Error: {e}")



elif mode == "CCTV Monitoring":

    st.header("📹 Intelligent CCTV Offloading")
    st.write("Monitor CCTV tasks and view Edge/Cloud recommendations.")

    if "cctv_running" not in st.session_state:
        st.session_state.cctv_running = False
    if "cctv_history" not in st.session_state:
        st.session_state.cctv_history = []
    if "cctv_iteration" not in st.session_state:
        st.session_state.cctv_iteration = 0

    start_cctv, stop_cctv = st.columns(2)
    with start_cctv:
        if st.button("▶ Start CCTV Monitoring", type="primary", use_container_width=True):
            st.session_state.cctv_running = True
    with stop_cctv:
        if st.button("⏹ Stop CCTV Monitoring", use_container_width=True):
            st.session_state.cctv_running = False

    if st.session_state.cctv_running:
        st_autorefresh(interval=2000, key="cctv_monitor_refresh")
        try:
            result = process_cctv_system()
            st.session_state.cctv_iteration += 1
            status = result.get("status", "unknown")
            latency_value = float(result.get("predicted_latency") or 0)
            cameras = result.get("camera_results", [])

            a, b, c = st.columns(3)
            a.metric("System Status", str(status).upper())
            b.metric("Iteration", st.session_state.cctv_iteration)
            c.metric("Predicted Future Latency", f"{latency_value:.2f} ms")

            st.subheader("💻 Edge Device Resources")
            resources = get_edge_resources()
            r1, r2, r3 = st.columns(3)
            r1.metric("CPU Usage", f"{float(resources.get('cpu_usage') or 0):.1f}%")
            r2.metric("RAM Usage", f"{float(resources.get('ram_usage') or 0):.1f}%")
            storage = resources.get("available_storage_gb", resources.get("available_storage", 0))
            r3.metric("Available Storage", f"{float(storage or 0):.2f} GB")

            if status == "collecting_data":
                collected = int(result.get("records_collected", 0) or 0)
                required = int(result.get("records_needed", 10) or 10)
                st.warning(f"Collecting network history: {collected}/{required}")
                st.progress(min(collected / required, 1.0) if required else 0)
            elif cameras:
                rows, edge_count, cloud_count = [], 0, 0
                for camera in cameras:
                    decision = str(camera.get("decision", "UNKNOWN")).upper()
                    edge_count += decision == "EDGE"
                    cloud_count += decision == "CLOUD"
                    rows.append({
                        "Camera ID": camera.get("camera_id", "Unknown"),
                        "Location": camera.get("location", "Unknown"),
                        "Priority": camera.get("priority", "Unknown"),
                        "Execution Decision": decision
                    })
                st.subheader("📋 CCTV Offloading Decisions")
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                x, y, z = st.columns(3)
                x.metric("🖥️ EDGE Tasks", edge_count)
                y.metric("☁️ CLOUD Tasks", cloud_count)
                z.metric("📹 Total CCTV Tasks", edge_count + cloud_count)
                st.session_state.cctv_history.append({
                    "Iteration": st.session_state.cctv_iteration,
                    "Predicted Latency": latency_value,
                    "EDGE Tasks": edge_count,
                    "CLOUD Tasks": cloud_count
                })
                st.session_state.cctv_history = st.session_state.cctv_history[-100:]
            else:
                st.info("Waiting for CCTV offloading decisions.")

            if len(st.session_state.cctv_history) > 1:
                hist = pd.DataFrame(st.session_state.cctv_history).set_index("Iteration")
                st.subheader("📈 CCTV Latency History")
                st.line_chart(hist["Predicted Latency"])
                st.subheader("📊 Edge vs Cloud CCTV Tasks")
                st.bar_chart(hist[["EDGE Tasks", "CLOUD Tasks"]])
        except Exception as e:
            st.error(f"CCTV monitoring error: {e}")
    else:
        st.info("CCTV monitoring is stopped. Click Start CCTV Monitoring to begin.")



# ============================================================
# HISTORY
# ============================================================

if len(
    st.session_state.history
) > 1:

    st.divider()

    st.header(
        "📊 Prediction History"
    )


    df = pd.DataFrame(
        st.session_state.history
    )


    st.subheader(
        "🔮 Current vs Predicted Latency"
    )


    st.line_chart(
        df[
            [
                "Current Latency",
                "Predicted Latency"
            ]
        ]
    )


    st.subheader(
        "📋 Recent Offloading Decisions"
    )


    st.dataframe(
        df.tail(10),
        use_container_width=True,
        hide_index=True
    )


    csv = df.to_csv(
        index=False
    )


    st.download_button(
        "⬇ Download Prediction History",
        data=csv,
        file_name="iot_offloading_predictions.csv",
        mime="text/csv"
    )