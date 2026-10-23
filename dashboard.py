import time
import uuid
import platform
import subprocess
import re

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from realtime_monitor import get_realtime_data

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="NEXUS | IoT Monitoring",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_DEFAULT = "http://127.0.0.1:8000"
REFRESH_MS = 2000
MAX_HISTORY = 150

# =========================================================
# SESSION STATE
# =========================================================
DEFAULTS = {
    "device_id": f"iot_{uuid.uuid4().hex[:6]}",
    "live_running": False,
    "live_history": [],
    "live_result": None,
    "manual_result": None,
    "last_error": None,
    "last_success": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# PASTEL NEXUS STYLING — PINK / INDIGO / BLUE / GREEN
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --page: #f7f6fc;
      --ink: #292b45;
      --muted: #747894;
      --pink: #f5c8dc;
      --pink-strong: #d978a8;
      --indigo: #dcdcff;
      --indigo-strong: #7776d9;
      --blue: #cce8ff;
      --blue-strong: #5a9fe0;
      --green: #d3f2df;
      --green-strong: #56a982;
      --border: #e4e3f1;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp {
      background:
        radial-gradient(ellipse at 8% 0%, rgba(245,200,220,.55), transparent 34%),
        radial-gradient(ellipse at 90% 5%, rgba(204,232,255,.65), transparent 32%),
        radial-gradient(ellipse at 60% 100%, rgba(211,242,223,.42), transparent 36%),
        linear-gradient(145deg, #fbfaff 0%, #f5f7ff 55%, #f8fcfa 100%);
      color: var(--ink);
    }
    .stApp::before {
      content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
      background-image: linear-gradient(rgba(119,118,217,.045) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(119,118,217,.045) 1px, transparent 1px);
      background-size: 36px 36px;
      mask-image: linear-gradient(to bottom, black, transparent 78%);
    }
    .block-container {
      max-width: 1800px; padding-top: 1.6rem; padding-bottom: 3rem;
      position: relative; z-index: 1;
    }
    header[data-testid="stHeader"] { background: rgba(250,249,255,.82); }
    section[data-testid="stSidebar"] {
      background: linear-gradient(180deg, #f8eaf3 0%, #eeeefe 52%, #e9f5ff 100%);
      border-right: 1px solid #e2dff2;
    }
    section[data-testid="stSidebar"] > div { padding-top: 1.8rem; }
    h1, h2, h3 {
      font-family: 'Space Grotesk', sans-serif !important;
      color: #303253 !important; letter-spacing: -.035em;
    }
    h1 { font-size: clamp(2rem, 3vw, 3.1rem) !important; }
    h2 { font-size: 1.7rem !important; }
    h3 { font-size: 1.25rem !important; }
    p, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: #555a78; }
    .top-banner {
      position: relative; overflow: hidden;
      background: linear-gradient(115deg, rgba(255,239,247,.98), rgba(235,236,255,.98) 55%, rgba(229,244,255,.98));
      border: 1px solid #e5dff5; border-radius: 22px;
      padding: 27px 30px; margin-bottom: 20px;
      box-shadow: 0 12px 32px rgba(104,99,163,.10), inset 0 1px rgba(255,255,255,.9);
    }
    .top-banner:after {
      content: ""; position: absolute; width: 300px; height: 300px;
      right: -70px; top: -150px;
      background: radial-gradient(circle, rgba(211,242,223,.95), transparent 68%);
      pointer-events: none;
    }
    .brand {
      color: #7776d9; font: 700 11px 'Space Grotesk', sans-serif;
      letter-spacing: .32em; text-transform: uppercase;
    }
    .subtitle { color: #747894; font-size: 14px; margin-top: 5px; }
    div[data-testid="stMetric"] {
      position: relative; overflow: hidden;
      background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(246,246,255,.96));
      border: 1px solid #e4e3f1; border-radius: 17px;
      padding: 18px 20px; min-height: 124px;
      box-shadow: 0 8px 24px rgba(79,82,140,.08);
      transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
    }
    div[data-testid="stMetric"]:nth-child(1) { border-top: 4px solid #e9a9c9; }
    div[data-testid="stMetric"]:hover {
      transform: translateY(-4px); border-color: #bdbcf0;
      box-shadow: 0 14px 30px rgba(103,100,170,.16);
    }
    div[data-testid="stMetricLabel"] { color: #777894; font-size: .82rem; letter-spacing: .06em; }
    div[data-testid="stMetricValue"] {
      color: #34365b; font-family: 'Space Grotesk', sans-serif;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
      background: rgba(255,255,255,.83);
      border: 1px solid #e4e3f1 !important; border-radius: 18px;
      box-shadow: 0 8px 24px rgba(79,82,140,.06);
      transition: border-color .2s ease, transform .2s ease, box-shadow .2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
      border-color: #c7c6f2 !important;
      box-shadow: 0 12px 28px rgba(103,100,170,.10);
    }
    div.stButton > button, div[data-testid="stDownloadButton"] button,
    button[data-testid="stBaseButton-primary"] {
      border-radius: 11px; border: 1px solid #c9c8f0;
      background: linear-gradient(110deg, #8887df, #76b8e9);
      color: #fff; font-weight: 700; transition: all .2s ease;
      box-shadow: 0 6px 16px rgba(119,118,217,.18);
    }
    div.stButton > button:hover, div[data-testid="stDownloadButton"] button:hover {
      transform: translateY(-2px); border-color: #e7a9ca;
      box-shadow: 0 9px 22px rgba(119,118,217,.22);
    }
    input, textarea, [data-baseweb="select"] > div {
      background-color: #fff !important; border-color: #deddf0 !important;
      border-radius: 10px !important; color: #303253 !important;
    }
    div[data-testid="stAlert"] { border-radius: 13px; border: 1px solid #e4e3f1; }
    div[data-testid="stDataFrame"] {
      border: 1px solid #e4e3f1; border-radius: 13px; overflow: hidden;
    }
    hr { border-color: #e4e3f1; }
    .status-good { color: #32875e; font-weight: 700; letter-spacing: .04em; }
    .status-warn { color: #a16b2d; font-weight: 700; letter-spacing: .04em; }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { transition: none !important; animation: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================
def measure_ping(host="8.8.8.8", timeout_seconds=2):
    """Return measured ping latency in ms, or None when unreachable."""
    system = platform.system().lower()
    try:
        if system == "windows":
            command = ["ping", "-n", "1", "-w", str(timeout_seconds * 1000), host]
        else:
            command = ["ping", "-c", "1", "-W", str(timeout_seconds), host]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 2,
            check=False,
        )
        output = (result.stdout or "") + " " + (result.stderr or "")
        if result.returncode != 0:
            return None

        # Windows usually prints "time=12ms" or "time<1ms".
        match = re.search(r"time\s*[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.I)
        if match:
            return max(float(match.group(1)), 0.1)

        # Linux/macOS usually prints "time=12.3 ms".
        match = re.search(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.I)
        if match:
            return max(float(match.group(1)), 0.1)

        # Some Windows versions report "time<1ms" with no space.
        if re.search(r"time\s*<\s*1\s*ms", output, re.I):
            return 0.5
    except (OSError, subprocess.TimeoutExpired):
        return None
    return None


def safe_float(value, default=None):
    try:
        if value is None:
            return default
        number = float(value)
        return number if pd.notna(number) else default
    except (TypeError, ValueError):
        return default


def metric_text(value, suffix="", digits=1):
    value = safe_float(value)
    return "N/A" if value is None else f"{value:.{digits}f}{suffix}"


def latest_value(df, column):
    if df.empty or column not in df.columns:
        return None
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    return None if values.empty else float(values.iloc[-1])


def call_predict(api_url, device_id, bandwidth, latency, cpu, task_size,
                 priority="normal", edge_available=True):
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
    response = requests.post(
        f"{api_url.rstrip('/')}/predict",
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def render_prediction(result):
    if not result:
        st.info("Waiting for an AI prediction.")
        return

    status = result.get("status")
    if status == "collecting_data":
        collected = int(result.get("records_collected", 0) or 0)
        needed = int(result.get("records_needed", 10) or 10)
        st.warning(f"LSTM warm-up: {collected}/{needed} readings collected")
        st.progress(min(collected / max(needed, 1), 1.0))
        return

    if status != "prediction_complete":
        st.warning(f"Prediction response: {result}")
        return

    net = result.get("network_condition") or {}
    predicted = safe_float(result.get("predicted_latency"))
    a, b, c = st.columns(3)
    a.metric("AI recommendation", result.get("recommended_execution", "UNKNOWN"))
    b.metric("Predicted latency", metric_text(predicted, " ms"))
    c.metric("Decision status", result.get("decision_status", "N/A"))

    condition = net.get("condition", "N/A")
    if condition == "UNSTABLE":
        st.error(f"Network condition: {condition}")
    elif condition == "STABLE":
        st.success(f"Network condition: {condition}")
    else:
        st.info(f"Network condition: {condition}")

    with st.expander("AI decision explanation", expanded=True):
        reasons = result.get("reasons") or []
        if reasons:
            for reason in reasons:
                st.write(f"• {reason}")
        else:
            st.write("No explanation was returned by the API.")


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 📡 NEXUS")
    st.caption("IoT Edge Intelligence Platform")
    st.divider()

    api_url = st.text_input("FastAPI base URL", value=API_DEFAULT).strip().rstrip("/")
    st.text_input("Device ID", key="device_id")

    mode = st.radio(
        "Monitoring mode",
        ["Real-Time Monitoring", "Manual Analysis"],
    )

    st.divider()
    st.markdown("### System controls")

    if st.button("Check API health", use_container_width=True):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            response.raise_for_status()
            st.success("API connected")
            st.json(response.json())
        except requests.RequestException as exc:
            st.error(f"API unavailable: {exc}")

    if mode == "Real-Time Monitoring":
        if not st.session_state.live_running:
            if st.button("▶ Start monitoring", type="primary", use_container_width=True):
                st.session_state.live_running = True
                st.session_state.live_history = []
                st.session_state.live_result = None
                st.session_state.last_error = None
                st.rerun()
        else:
            if st.button("■ Stop monitoring", use_container_width=True):
                st.session_state.live_running = False
                st.rerun()

    if st.button("Clear history", use_container_width=True):
        st.session_state.live_history = []
        st.session_state.last_error = None
        st.rerun()

    st.divider()
    st.caption(f"Refresh interval: {REFRESH_MS / 1000:.0f} seconds")
    st.caption(f"Stored samples: {len(st.session_state.live_history)}")

# =========================================================
# HEADER
# =========================================================
left, right = st.columns([4, 1])
with left:
    st.markdown(
        """
        <div class="top-banner">
          <div class="brand">NEXUS / EDGE INTELLIGENCE</div>
          <h1 style="margin:7px 0">IoT Real-Time Monitoring</h1>
          <div class="subtitle">
            Network telemetry · Predictive analytics · Adaptive task offloading
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.markdown("#### System status")
    if st.session_state.live_running:
        st.markdown('<span class="status-good">● MONITORING</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-warn">● STANDBY</span>', unsafe_allow_html=True)
    st.caption(time.strftime("%d %b %Y"))
    st.caption(time.strftime("%H:%M:%S"))

# =========================================================
# REAL-TIME MODE
# =========================================================
if mode == "Real-Time Monitoring":
    st.markdown("### Overview")
    uploaded = st.file_uploader(
        "Upload a task file to evaluate its offloading destination",
        key="monitor_task",
    )

    task_size_mb = None
    task_name = "No task uploaded"
    if uploaded is not None:
        task_name = uploaded.name
        task_size_mb = len(uploaded.getvalue()) / (1024 * 1024)
        st.caption(f"Selected task: {task_name} · {task_size_mb:.4f} MB")

    if st.session_state.live_running:
        st_autorefresh(interval=REFRESH_MS, key="nexus_live_refresh")

        # Collect a new sample on each refresh while monitoring is running.
        try:
            measured = get_realtime_data(task_size=task_size_mb or 0.0) or {}
            cpu = safe_float(measured.get("cpu_usage"))
            ram = safe_float(measured.get("memory_usage"))
            bandwidth = safe_float(measured.get("bandwidth"))
            latency = safe_float(measured.get("latency"))

            # The monitor's latency is None in some environments; try a real ping.
            if latency is None:
                latency = measure_ping()

            row = {
                "time": time.strftime("%H:%M:%S"),
                "timestamp": time.time(),
                "task": task_name,
                "task_size_mb": task_size_mb,
                "cpu_%": cpu,
                "ram_%": ram,
                "traffic_mbps": bandwidth,
                "latency_ms": latency,
                "model_status": "measurement_only",
                "decision": "Upload a task to request a recommendation",
                "predicted_latency_ms": None,
                "network_condition": "N/A",
            }

            if cpu is None or ram is None or bandwidth is None:
                raise ValueError(f"Monitor returned incomplete metrics: {measured}")

            if uploaded is not None and latency is not None:
                try:
                    result = call_predict(
                        api_url=api_url,
                        device_id=st.session_state.device_id,
                        bandwidth=bandwidth,
                        latency=latency,
                        cpu=cpu,
                        task_size=task_size_mb or 0.0,
                    )
                    st.session_state.live_result = result
                    row["model_status"] = result.get("status", "unknown")
                    row["decision"] = result.get("recommended_execution", "Collecting data")
                    row["predicted_latency_ms"] = safe_float(result.get("predicted_latency"))
                    network = result.get("network_condition") or {}
                    row["network_condition"] = network.get("condition", "N/A")
                    st.session_state.last_error = None
                except requests.RequestException as exc:
                    st.session_state.last_error = f"Prediction API error: {exc}"
                    row["model_status"] = "api_error"
            elif uploaded is not None:
                row["model_status"] = "ping_unavailable"
            else:
                row["model_status"] = "measurement_only"

            st.session_state.live_history.append(row)
            st.session_state.live_history = st.session_state.live_history[-MAX_HISTORY:]
            st.session_state.last_success = time.time()

        except Exception as exc:
            st.session_state.last_error = str(exc)

    if st.session_state.last_error:
        st.error(f"Monitoring issue: {st.session_state.last_error}")

    df = pd.DataFrame(st.session_state.live_history)
    cpu_now = latest_value(df, "cpu_%")
    ram_now = latest_value(df, "ram_%")
    bandwidth_now = latest_value(df, "traffic_mbps")
    latency_now = latest_value(df, "latency_ms")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CPU USAGE", metric_text(cpu_now, "%"))
    m2.metric("RAM USAGE", metric_text(ram_now, "%"))
    m3.metric("NETWORK TRAFFIC", metric_text(bandwidth_now, " Mbps", 2))
    m4.metric("PING LATENCY", metric_text(latency_now, " ms"))

    st.markdown("### Performance telemetry")
    chart_left, chart_right = st.columns([1.6, 1])

    with chart_left:
        with st.container(border=True):
            st.markdown("**Latency over time**")
            if not df.empty and "latency_ms" in df and df["latency_ms"].notna().any():
                chart = df[["timestamp", "latency_ms"]].copy()
                chart["timestamp"] = pd.to_datetime(chart["timestamp"], unit="s")
                chart = chart.dropna().set_index("timestamp")
                st.line_chart(chart, height=260)
            else:
                st.info("Latency readings will appear here. Check that this computer can ping 8.8.8.8.")

        with st.container(border=True):
            st.markdown("**CPU and RAM utilization**")
            if not df.empty:
                usage = df[["timestamp", "cpu_%", "ram_%"]].copy()
                usage["timestamp"] = pd.to_datetime(usage["timestamp"], unit="s")
                usage = usage.dropna(subset=["cpu_%", "ram_%"]).set_index("timestamp")
                if not usage.empty:
                    st.line_chart(usage, height=230)
                else:
                    st.info("No CPU/RAM samples are available yet.")
            else:
                st.info("Click Start monitoring to collect system measurements.")

    with chart_right:
        with st.container(border=True):
            st.markdown("**Current resource utilization**")
            for label, value in [("CPU usage", cpu_now), ("RAM usage", ram_now)]:
                st.write(f"{label}: {metric_text(value, '%')}")
                if value is not None:
                    st.progress(min(max(value / 100.0, 0.0), 1.0))

        with st.container(border=True):
            st.markdown("**Network traffic**")
            if not df.empty and "traffic_mbps" in df:
                traffic = df[["timestamp", "traffic_mbps"]].copy()
                traffic["timestamp"] = pd.to_datetime(traffic["timestamp"], unit="s")
                traffic = traffic.dropna().set_index("timestamp")
                if not traffic.empty:
                    st.line_chart(traffic, height=180)
                else:
                    st.info("No network traffic samples yet.")
            else:
                st.info("No network measurements yet.")

        with st.container(border=True):
            st.markdown("**Network status**")
            latest_condition = (
                df["network_condition"].iloc[-1]
                if not df.empty and "network_condition" in df
                else "N/A"
            )
            if latest_condition == "UNSTABLE":
                st.error("UNSTABLE")
            elif latest_condition == "STABLE":
                st.success("STABLE")
            elif latency_now is not None:
                st.info("Ping measured; AI network condition not available yet")
            else:
                st.info("Waiting for a valid ping measurement")

    st.markdown("### AI offloading and device status")
    ai_col, device_col, alert_col = st.columns([1.25, 1, 1])

    with ai_col:
        with st.container(border=True):
            st.markdown("**AI prediction / offloading**")
            if uploaded is None:
                st.info("Upload a task file and start monitoring to request an EDGE/CLOUD recommendation.")
            elif not st.session_state.live_running:
                st.info("Click Start monitoring to collect readings and request the recommendation.")
            elif st.session_state.live_result:
                render_prediction(st.session_state.live_result)
            else:
                st.info("Collecting readings. The model may require 10 sequential samples before predicting.")

    with device_col:
        with st.container(border=True):
            st.markdown("**Monitored device**")
            st.write("Device ID")
            st.code(st.session_state.device_id)
            st.write("Measurement source")
            st.write("This computer")
            st.write("Last successful reading")
            if st.session_state.last_success:
                st.write(time.strftime("%H:%M:%S", time.localtime(st.session_state.last_success)))
            else:
                st.write("No successful reading yet")
            st.write("ESP32 sensor")
            st.caption("Not connected to this dashboard yet")

    with alert_col:
        with st.container(border=True):
            st.markdown("**Monitoring alerts**")
            alerts = 0
            if cpu_now is not None and cpu_now >= 85:
                st.error("High CPU utilization")
                alerts += 1
            if ram_now is not None and ram_now >= 90:
                st.error("High memory utilization")
                alerts += 1
            if latency_now is not None and latency_now >= 150:
                st.warning("High ping latency")
                alerts += 1
            if not alerts:
                st.success("No configured threshold alerts")
            st.caption("Threshold alerts only; no separate predictive-maintenance model is running.")

    st.markdown("### Recent monitoring history")
    if not df.empty:
        display_cols = [
            "time", "task", "cpu_%", "ram_%", "traffic_mbps",
            "latency_ms", "model_status", "network_condition", "decision",
        ]
        display_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[display_cols].tail(20), use_container_width=True, hide_index=True)
        st.download_button(
            "Download telemetry CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="nexus_telemetry.csv",
            mime="text/csv",
        )
    else:
        st.info("Start monitoring to populate charts and history.")

    st.caption(
        "Packet loss, temperature, humidity, ESP32 telemetry, and remote task execution "
        "are not measured by this version. AI results are recommendations only."
    )

# =========================================================
# MANUAL ANALYSIS MODE — AUTOMATIC 10-SAMPLE COLLECTION
# =========================================================
else:
    st.markdown("### Manual scenario analysis")
    st.write(
        "Enter the scenario once. The dashboard will automatically submit "
        "10 sequential samples to the API using these values."
    )
    st.info(
        "Note: these are repeated manual scenario values, not 10 independent "
        "live sensor measurements. For live readings, use Real-Time Monitoring."
    )

    with st.form("manual_iot_form"):
        c1, c2 = st.columns(2)
        bandwidth = c1.number_input(
            "Bandwidth / traffic (Mbps)", min_value=0.0, value=50.0, step=5.0
        )
        latency = c2.number_input(
            "Observed latency (ms)", min_value=0.0, value=50.0, step=5.0
        )
        cpu = c1.slider("CPU usage (%)", min_value=0, max_value=100, value=50)
        task_size = c2.number_input(
            "Task size (MB)", min_value=0.0, value=1.0, step=0.5
        )
        priority = c1.selectbox("Task priority", ["normal", "urgent"])
        edge_available = c2.toggle("Edge node available", value=True)
        submitted = st.form_submit_button(
            "Collect 10 samples & run AI",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        progress = st.progress(0, text="Starting automatic sample collection...")
        status_area = st.empty()
        final_result = None
        manual_device_id = st.session_state.device_id + "_manual"

        try:
            for sample_number in range(1, 11):
                final_result = call_predict(
                    api_url=api_url,
                    device_id=manual_device_id,
                    bandwidth=bandwidth,
                    latency=latency,
                    cpu=cpu,
                    task_size=task_size,
                    priority=priority,
                    edge_available=edge_available,
                )
                progress.progress(
                    sample_number * 10,
                    text=f"Submitting sample {sample_number}/10...",
                )
                status_area.info(
                    f"Automatic collection: {sample_number}/10 samples submitted."
                )

                # A small pause keeps requests ordered and makes progress visible.
                if sample_number < 10:
                    time.sleep(0.15)

            st.session_state.manual_result = final_result
            progress.progress(100, text="Sample collection complete.")
            status_area.success("10 samples submitted. Latest API result:")
        except requests.RequestException as exc:
            st.error(
                f"API request failed during sample collection. "
                f"Check the FastAPI server and URL. Details: {exc}"
            )
        except Exception as exc:
            st.error(f"Automatic collection failed: {exc}")

    render_prediction(st.session_state.manual_result)

st.divider()
st.caption(
    "NEXUS IoT Offloading | Live computer telemetry + LSTM prediction | "
    "Recommendations only; remote task execution is not implemented."
)