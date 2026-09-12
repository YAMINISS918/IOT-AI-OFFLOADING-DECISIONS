import streamlit as st
import requests
import random
import time
import pandas as pd


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="IoT Intelligent Offloading",
    page_icon="🌐",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

[data-testid="stSidebar"] {
    background-color: #262730;
}

.metric-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #161b22;
}

.edge-box {
    background-color: #123d2b;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    color: #7ee787;
    font-size: 25px;
    font-weight: bold;
}

.cloud-box {
    background-color: #4a2525;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    color: #ff8b8b;
    font-size: 25px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "running" not in st.session_state:
    st.session_state.running = False

if "latency_history" not in st.session_state:
    st.session_state.latency_history = []

if "decision_history" not in st.session_state:
    st.session_state.decision_history = []

if "records" not in st.session_state:
    st.session_state.records = 0


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("⚙ Simulation Control")

start_button = st.sidebar.button(
    "▶ Start Real-Time Simulation",
    use_container_width=True
)

stop_button = st.sidebar.button(
    "■ Stop Simulation",
    use_container_width=True
)


# ==========================================
# USER TASK CONFIGURATION
# ==========================================

st.sidebar.markdown("---")

st.sidebar.subheader("📦 User Task Configuration")

task_size = st.sidebar.slider(
    "Task Size (MB)",
    min_value=1,
    max_value=10,
    value=5
)

cpu_usage = st.sidebar.slider(
    "CPU Usage (%)",
    min_value=10,
    max_value=100,
    value=50
)

application_type = st.sidebar.selectbox(
    "Application Type",
    [
        "IoT Sensor Data",
        "Image Processing",
        "Video Processing",
        "Smart Healthcare",
        "Industrial IoT"
    ]
)


st.sidebar.markdown("---")

st.sidebar.info(
    "Network parameters are simulated in real-time. "
    "Task parameters are provided by the user."
)


# ==========================================
# BUTTON CONTROL
# ==========================================

if start_button:

    st.session_state.running = True

    # Reset API history

    try:

        requests.post(
            "http://127.0.0.1:8000/reset"
        )

    except:
        pass

    st.session_state.latency_history = []
    st.session_state.decision_history = []
    st.session_state.records = 0


if stop_button:

    st.session_state.running = False


# ==========================================
# MAIN TITLE
# ==========================================

st.title("🤖 Intelligent IoT Edge-Cloud Offloading System")

st.subheader(
    "Real-Time AI-Based Network Monitoring & Offloading Decision"
)


# ==========================================
# APPLICATION INFORMATION
# ==========================================

st.info(
    f"📱 Application: {application_type} | "
    f"📦 User Task Size: {task_size} MB | "
    f"💻 Device CPU Usage: {cpu_usage}%"
)


# ==========================================
# SIMULATION
# ==========================================

if st.session_state.running:


    # --------------------------------------
    # GENERATE NETWORK CONDITIONS
    # --------------------------------------

    bandwidth = random.randint(20, 100)

    latency = random.randint(15, 200)


    # --------------------------------------
    # SEND DATA TO API
    # --------------------------------------

    payload = {

        "bandwidth": bandwidth,

        "latency": latency,

        "cpu_usage": cpu_usage,

        "task_size": task_size

    }


    try:

        response = requests.post(

            "http://127.0.0.1:8000/predict",

            json=payload

        )

        result = response.json()


    except Exception as e:

        st.error(
            "Cannot connect to FastAPI backend. "
            "Make sure api.py is running."
        )

        st.stop()


    # ======================================
    # DISPLAY NETWORK METRICS
    # ======================================

    st.markdown("## 🌐 Real-Time Network Status")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "📶 Bandwidth",
            f"{bandwidth} Mbps"
        )


    with col2:

        st.metric(
            "⏱ Current Latency",
            f"{latency} ms"
        )


    with col3:

        st.metric(
            "💻 CPU Usage",
            f"{cpu_usage}%"
        )


    with col4:

        st.metric(
            "📦 Task Size",
            f"{task_size} MB"
        )


    st.markdown("---")


    # ======================================
    # COLLECTING DATA STATUS
    # ======================================

    if result["status"] == "collecting_data":

        collected = result["records_collected"]

        needed = result["records_needed"]

        st.warning(
            f"🤖 AI is collecting network history... "
            f"{collected}/{needed} records"
        )

        st.progress(
            collected / needed
        )


    # ======================================
    # PREDICTION RESULT
    # ======================================

    else:

        predicted_latency = result[
            "predicted_latency"
        ]

        decision = result[
            "recommended_execution"
        ]

        reasons = result["reasons"]

        score = result["decision_score"]


        # ----------------------------------
        # PREDICTION DISPLAY
        # ----------------------------------

        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "🔮 Predicted Future Latency",
                f"{predicted_latency} ms"
            )


        with col2:

            if decision == "EDGE":

                st.markdown(
                    """
                    <div class="edge-box">
                    🟢 RECOMMENDED EXECUTION: EDGE
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="cloud-box">
                    🔵 RECOMMENDED EXECUTION: CLOUD
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ----------------------------------
        # AI DECISION EXPLANATION
        # ----------------------------------

        st.markdown("## 🧠 AI Decision Explanation")

        st.write(
            f"**Decision Score:** {score}"
        )

        for reason in reasons:

            st.write(f"• {reason}")


        # ----------------------------------
        # STORE HISTORY
        # ----------------------------------

        st.session_state.latency_history.append(
            {
                "Current Latency": latency,
                "Predicted Latency": predicted_latency
            }
        )


        st.session_state.decision_history.append(
            {
                "Bandwidth": bandwidth,
                "Current Latency": latency,
                "CPU Usage": cpu_usage,
                "Task Size": task_size,
                "Predicted Latency": predicted_latency,
                "Decision": decision
            }
        )


        # Keep last 30 records

        if len(st.session_state.latency_history) > 30:

            st.session_state.latency_history.pop(0)


        if len(st.session_state.decision_history) > 30:

            st.session_state.decision_history.pop(0)


        # ----------------------------------
        # LATENCY GRAPH
        # ----------------------------------

        st.markdown("## 📊 Real-Time Latency Monitoring")

        latency_df = pd.DataFrame(
            st.session_state.latency_history
        )

        st.line_chart(
            latency_df
        )


        # ----------------------------------
        # DECISION HISTORY
        # ----------------------------------

        st.markdown("## 📋 Offloading Decision History")

        history_df = pd.DataFrame(
            st.session_state.decision_history
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )


else:

    st.markdown(
        """
        ### 🚀 System Ready

        Configure the IoT task from the sidebar and click:

        **▶ Start Real-Time Simulation**

        The system will:

        1. Simulate real-time network conditions
        2. Collect the last 10 network states
        3. Send data to the LSTM model
        4. Predict future network latency
        5. Analyze CPU usage and task size
        6. Recommend EDGE or CLOUD execution
        """
    )