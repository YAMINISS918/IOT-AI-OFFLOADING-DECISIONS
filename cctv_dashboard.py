import streamlit as st
import pandas as pd
import time

from streamlit_autorefresh import st_autorefresh
from cctv_offloading_manager import process_cctv_system
from resource_monitor import get_edge_resources


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Intelligent CCTV Offloading System",
    page_icon="📹",
    layout="wide"
)



# ==========================================
# SESSION STATE
# ==========================================

if "running" not in st.session_state:
    st.session_state.running = False

if "history" not in st.session_state:
    st.session_state.history = []

if "iteration" not in st.session_state:
    st.session_state.iteration = 0

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("⚙️ System Control")

start = st.sidebar.button(
    "▶ Start Monitoring",
    use_container_width=True
)

stop = st.sidebar.button(
    "⏹ Stop Monitoring",
    use_container_width=True
)

reset = st.sidebar.button(
    "🔄 Reset Dashboard",
    use_container_width=True
)


# ==========================================
# BUTTON ACTIONS
# ==========================================

if start:
    st.session_state.running = True


if stop:
    st.session_state.running = False


if reset:

    st.session_state.running = False
    st.session_state.history = []
    st.session_state.iteration = 0
    st.session_state.latest_result = None

    st.rerun()


# ==========================================
# TITLE
# ==========================================

st.title("📹 Intelligent IoT Edge-Cloud Offloading System")

st.markdown(
    "### Real-Time CCTV Task Monitoring, AI Latency Prediction & Intelligent Offloading"
)

st.divider()


# ==========================================
# SYSTEM STATUS
# ==========================================

if st.session_state.running:
    st_autorefresh(
    interval=2000,
    key="realtime_refresh"
)

    status_col1, status_col2, status_col3 = st.columns(3)

    status_col1.metric(
        "System Status",
        "ACTIVE"
    )

    status_col2.metric(
        "Monitoring Mode",
        "Real-Time"
    )

    status_col3.metric(
        "Iteration",
        st.session_state.iteration
    )

else:

    status_col1, status_col2, status_col3 = st.columns(3)

    status_col1.metric(
        "System Status",
        "STOPPED"
    )

    status_col2.metric(
        "Monitoring Mode",
        "Idle"
    )

    status_col3.metric(
        "Iteration",
        st.session_state.iteration
    )


st.divider()


# ==========================================
# MAIN MONITORING SYSTEM
# ==========================================

if st.session_state.running:

    try:

        # ==========================================
        # RUN CCTV OFFLOADING SYSTEM
        # ==========================================

        result = process_cctv_system()


        # Store result

        st.session_state.latest_result = result

        st.session_state.iteration += 1


        # ==========================================
        # EXTRACT SYSTEM DATA
        # ==========================================

        status = result.get(
            "status",
            "unknown"
        )

        predicted_latency = result.get(
            "predicted_latency",
            0
        )

        network_condition = result.get(
            "network_condition",
            "Unknown"
        )

        cctv_decisions = result.get(
    "camera_results",
    []
)

        # ==========================================
        # AI PREDICTION SECTION
        # ==========================================

        st.subheader("🧠 AI Network Prediction")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Predicted Future Latency",
            f"{predicted_latency:.2f} ms"
        )

        col2.metric(
            "Network Condition",
            str(network_condition)
        )

        col3.metric(
            "AI Status",
            status
        )


        st.divider()


        # ==========================================
        # EDGE RESOURCE MONITORING
        # ==========================================

        st.subheader("💻 Edge Device Resource Monitoring")

        resources = get_edge_resources()


        # Extract values safely

        cpu_usage = resources.get(
            "cpu_usage",
            0
        )

        ram_usage = resources.get(
            "ram_usage",
            0
        )

        available_storage = resources.get(
            "available_storage",
            0
        )


        resource_col1, resource_col2, resource_col3 = st.columns(3)

        resource_col1.metric(
            "CPU Usage",
            f"{cpu_usage:.1f}%"
        )

        resource_col2.metric(
            "RAM Usage",
            f"{ram_usage:.1f}%"
        )

        resource_col3.metric(
            "Available Storage",
            f"{available_storage:.2f} GB"
        )


        st.divider()


        # ==========================================
        # CCTV OFFLOADING DECISIONS
        # ==========================================

        st.subheader("📹 CCTV Intelligent Offloading Decisions")


        # IMPORTANT
        # Initialize counters BEFORE using them

        edge_count = 0
        cloud_count = 0


        # If system is collecting data

        if status == "collecting_data":

            records_collected = result.get(
                "records_collected",
                0
            )

            records_needed = result.get(
                "records_needed",
                10
            )

            st.warning(
                f"🔄 Collecting Network History: "
                f"{records_collected}/{records_needed}"
            )

            progress = records_collected / records_needed

            st.progress(progress)


        # ==========================================
        # DISPLAY CCTV DECISIONS
        # ==========================================

        elif len(cctv_decisions) > 0:


            table_data = []


            for camera in cctv_decisions:


                # Extract camera information safely

                camera_id = camera.get(
                    "camera_id",
                    "Unknown"
                )

                location = camera.get(
                    "location",
                    "Unknown"
                )

                priority = camera.get(
                    "priority",
                    "Unknown"
                )

                decision = camera.get(
                    "decision",
                    "Unknown"
                )


                # ==========================================
                # COUNT EDGE / CLOUD
                # ==========================================

                if decision == "EDGE":

                    edge_count += 1

                elif decision == "CLOUD":

                    cloud_count += 1


                # Add to table

                table_data.append({

                    "Camera ID": camera_id,

                    "Location": location,

                    "Priority": priority,

                    "Execution Decision": decision

                })


            # ==========================================
            # DISPLAY TABLE
            # ==========================================

            df = pd.DataFrame(
                table_data
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


            st.divider()


            # ==========================================
            # OFFLOADING SUMMARY
            # ==========================================

            st.subheader("📊 Offloading Decision Summary")


            summary_col1, summary_col2, summary_col3 = st.columns(3)


            summary_col1.metric(
                "🖥️ EDGE Tasks",
                edge_count
            )


            summary_col2.metric(
                "☁️ CLOUD Tasks",
                cloud_count
            )


            total_tasks = edge_count + cloud_count


            summary_col3.metric(
                "📹 Total CCTV Tasks",
                total_tasks
            )


            # ==========================================
            # SAVE HISTORY
            # ==========================================

            st.session_state.history.append({

                "Iteration":
                    st.session_state.iteration,

                "Predicted Latency":
                    predicted_latency,

                "EDGE Tasks":
                    edge_count,

                "CLOUD Tasks":
                    cloud_count

            })


        else:

            st.info(
                "Waiting for CCTV offloading decisions..."
            )


        # ==========================================
        # REAL-TIME GRAPH
        # ==========================================

        if len(st.session_state.history) > 1:


            st.divider()

            st.subheader(
                "📈 Real-Time AI Latency Prediction"
            )


            history_df = pd.DataFrame(
                st.session_state.history
            )


            st.line_chart(
                history_df.set_index(
                    "Iteration"
                )[
                    "Predicted Latency"
                ]
            )


            # ==========================================
            # OFFLOADING GRAPH
            # ==========================================

            st.subheader(
                "📊 Edge vs Cloud Task Distribution"
            )


            st.bar_chart(
                history_df.set_index(
                    "Iteration"
                )[
                    [
                        "EDGE Tasks",
                        "CLOUD Tasks"
                    ]
                ]
            )


    except Exception as e:

        st.error(
            f"System Error: {e}"
        )


    # ==========================================
    # AUTO REFRESH
    # ==========================================

    


# ==========================================
# SYSTEM NOT RUNNING
# ==========================================

else:

    st.info(
        "👈 Click **Start Monitoring** to begin "
        "real-time CCTV network analysis and "
        "AI-based Edge-Cloud offloading."
    )


    st.markdown(
        """
        ### 🔄 System Workflow

        **CCTV Cameras**
        → Generate Video Processing Tasks
        → Monitor Network
        → Monitor Edge Resources
        → LSTM Predicts Future Latency
        → AI Decision Engine
        → EDGE or CLOUD Recommendation
        """
    )