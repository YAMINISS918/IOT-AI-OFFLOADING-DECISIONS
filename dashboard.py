import time
import uuid
import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from realtime_monitor import get_realtime_data

st.set_page_config(page_title="NEXUS IoT Offloading", page_icon="📡", layout="wide")

API_DEFAULT = "http://127.0.0.1:8000"
for key, default in {
    "device_id": f"iot_{uuid.uuid4().hex[:6]}",
    "live_running": False,
    "live_history": [],
    "live_result": None,
    "manual_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
.stApp {background:radial-gradient(circle at 85% 0%,#17223b 0,#090e19 48%,#080b13 100%);color:#edf3ff}
section[data-testid="stSidebar"] {background:#0e1626}
.hero {padding:1.5rem 1.8rem;border:1px solid #26364e;border-radius:22px;background:#101929;margin-bottom:1.2rem}
.kicker {letter-spacing:.18em;color:#55f2df;font-family:monospace}
.hero h1 {font-size:2.35rem;margin:.5rem 0}
.hero p {color:#a9bad2;font-size:1.05rem}
div[data-testid="stMetric"] {background:#111b2b;border:1px solid #283951;padding:14px;border-radius:14px}
</style>
<div class="hero">
<div class="kicker">NEXUS / EDGE INTELLIGENCE PLATFORM</div>
<h1>Intelligent IoT <span style="color:#55f2df">Offloading Console</span></h1>
<p>Upload a task, measure its size, inspect real device/network telemetry, and obtain an EDGE/CLOUD recommendation.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### System setup")
    api_url = st.text_input("FastAPI base URL", API_DEFAULT).strip().rstrip("/")
    st.text_input("Device ID", key="device_id")
    mode = st.radio("Select mode", ["Real-Time Task Upload", "Manual IoT Input"])
    st.caption("Keep `python main.py` running in a separate terminal.")
    if st.button("Check API health", use_container_width=True):
        try:
            r = requests.get(f"{api_url}/health", timeout=5)
            r.raise_for_status()
            st.success(f"API reachable: {r.json()}")
        except requests.RequestException as exc:
            st.error(f"API health check failed: {exc}")

def call_predict(api_url, device_id, bandwidth, latency, cpu, task_size, priority="normal", edge_available=True):
    payload = {
        "device_id": str(device_id),
        "bandwidth": max(float(bandwidth), 0.0),
        "latency": max(float(latency), 0.0),
        "cpu_usage": min(max(float(cpu), 0.0), 100.0),
        "task_size": max(float(task_size), 0.0),
        "task_priority": priority,
        "data_is_fresh": True,
        "edge_available": bool(edge_available),
    }
    response = requests.post(f"{api_url}/predict", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()

def show_prediction(result):
    if not result:
        return
    status = result.get("status")
    if status == "collecting_data":
        n = int(result.get("records_collected", 0) or 0)
        need = int(result.get("records_needed", 10) or 10)
        st.info(f"LSTM warm-up: {n}/{need} readings collected. The model needs a sequence before predicting.")
        st.progress(min(n / max(need, 1), 1.0))
        return
    if status != "prediction_complete":
        st.warning(f"API response: {result}")
        return
    net = result.get("network_condition") or {}
    decision = result.get("recommended_execution", "UNKNOWN")
    a, b, c = st.columns(3)
    a.metric("Recommended execution", decision)
    b.metric("Predicted latency", f"{float(result.get('predicted_latency') or 0):.2f} ms")
    c.metric("Decision status", str(result.get("decision_status", "N/A")))
    st.write(f"**Network condition:** {net.get('condition', 'N/A')}")
    if result.get("reasons"):
        st.markdown("**Decision reasons**")
        for reason in result["reasons"]:
            st.write(f"- {reason}")

# MODE 1: task upload + live measurements
if mode == "Real-Time Task Upload":
    st.markdown("### 01 / Upload a task and monitor it")
    st.write("Upload the actual file to measure its size. While monitoring runs, this computer's CPU, RAM, traffic throughput and ping latency are sampled automatically.")
    uploaded = st.file_uploader("Choose the task/file to analyse", key="live_task_file")
    task_size_mb = None
    if uploaded is not None:
        file_bytes = uploaded.getvalue()
        task_size_mb = len(file_bytes) / (1024 * 1024)
        st.success(f"**{uploaded.name}** · {len(file_bytes):,} bytes · **{task_size_mb:.4f} MB**")
        st.caption("The file size is measured from the uploaded file. This demo recommends an execution destination; it does not transfer or execute the file on a remote node.")
    else:
        st.info("Upload a task file to begin.")
    x1, x2 = st.columns(2)
    with x1:
        if st.button("▶ Start live monitoring", type="primary", use_container_width=True, disabled=uploaded is None or st.session_state.live_running):
            st.session_state.live_running = True
            st.session_state.live_history = []
            st.session_state.live_result = None
            st.rerun()
    with x2:
        if st.button("■ Stop monitoring", use_container_width=True, disabled=not st.session_state.live_running):
            st.session_state.live_running = False
            st.rerun()

    if st.session_state.live_running and uploaded is not None:
        st_autorefresh(interval=2000, key="real_task_live_refresh")
        try:
            measured = get_realtime_data(task_size=task_size_mb)
            st.markdown("#### Current measurements")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("CPU usage", f"{measured['cpu_usage']:.1f}%")
            m2.metric("RAM usage", f"{measured['memory_usage']:.1f}%")
            m3.metric("Network traffic", f"{measured['bandwidth']:.2f} Mbps")
            m4.metric("Ping latency", "Unavailable" if measured["latency"] is None else f"{measured['latency']:.1f} ms")
            if measured["latency"] is None:
                st.warning("Ping failed, so this reading was not sent to the AI API. Check connectivity or try again.")
            else:
                result = call_predict(api_url, st.session_state.device_id, measured["bandwidth"], measured["latency"], measured["cpu_usage"], task_size_mb)
                st.session_state.live_result = result
                row = {
                    "time": time.strftime("%H:%M:%S"),
                    "task": uploaded.name,
                    "task_size_mb": round(task_size_mb, 4),
                    "cpu_%": measured["cpu_usage"],
                    "ram_%": measured["memory_usage"],
                    "traffic_mbps": measured["bandwidth"],
                    "latency_ms": measured["latency"],
                    "model_status": result.get("status"),
                    "decision": result.get("recommended_execution", "Collecting data"),
                    "predicted_latency_ms": result.get("predicted_latency"),
                }
                st.session_state.live_history.append(row)
                st.session_state.live_history = st.session_state.live_history[-100:]
                show_prediction(result)
        except requests.RequestException as exc:
            st.error(f"Could not reach the prediction API: {exc}")
        except Exception as exc:
            st.error(f"Live measurement failed: {exc}")
    elif not st.session_state.live_running:
        st.caption("Monitoring is stopped. Start it to collect real readings every 2 seconds.")
    if st.session_state.live_history:
        st.markdown("#### Recent task telemetry")
        df = pd.DataFrame(st.session_state.live_history)
        chart_cols = [c for c in ["cpu_%", "ram_%", "traffic_mbps", "latency_ms"] if c in df.columns]
        st.line_chart(df.set_index("time")[chart_cols])
        st.dataframe(df.tail(15), use_container_width=True, hide_index=True)

# MODE 2: manual values
else:
    st.markdown("### 02 / Manual what-if analysis")
    st.write("Enter a network snapshot to test a scenario. This is manual testing, separate from live measurements.")
    with st.form("manual_iot_form"):
        c1, c2 = st.columns(2)
        bandwidth = c1.number_input("Bandwidth / traffic (Mbps)", min_value=0.0, value=50.0, step=5.0)
        latency = c2.number_input("Observed latency (ms)", min_value=0.0, value=50.0, step=5.0)
        cpu = c1.slider("CPU usage (%)", 0, 100, 50)
        task_size = c2.number_input("Task size (MB)", min_value=0.0, value=1.0, step=0.5)
        priority = c1.selectbox("Task priority", ["normal", "urgent"])
        edge_available = c2.toggle("Edge node available", value=True)
        submitted = st.form_submit_button("Run AI offloading recommendation", type="primary", use_container_width=True)
    if submitted:
        try:
            st.session_state.manual_result = call_predict(api_url, st.session_state.device_id + "_manual", bandwidth, latency, cpu, task_size, priority, edge_available)
        except requests.RequestException as exc:
            st.error(f"Prediction API error: {exc}")
    show_prediction(st.session_state.manual_result)

st.caption("NEXUS demo: live mode measures this computer; manual mode accepts user-supplied values. Recommendations do not physically migrate/execute tasks.")
