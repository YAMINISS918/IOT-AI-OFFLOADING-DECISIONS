"""
Central configuration for the confidence- and privacy-aware offloading module.

Every constant below is documented with *where it comes from*. Nothing here is
a tuned "magic weight": values are either taken from existing project code,
derived from the trained artefacts, or are explicit simulation assumptions
that must be replaced with measurements before reporting real-world results.

Most values can be overridden with environment variables (see README).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return float(value)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _project_path(env_name: str, relative: str) -> Path:
    raw = _env_str(env_name, relative)
    path = Path(raw)
    return path if path.is_absolute() else PROJECT_ROOT / path


MODEL_PATH = _project_path("IOT_MODEL_PATH", "models/main_lstm_model.keras")
SCALER_PATH = _project_path("IOT_SCALER_PATH", "models/main_feature_scaler.pkl")
CALIBRATION_PATH = _project_path(
    "IOT_CALIBRATION_PATH", "models/uncertainty_calibration.json"
)
DATASET_PATH = _project_path("IOT_DATASET_PATH", "data/raw/network_dataset.csv")
RESULTS_DIR = _project_path("IOT_RESULTS_DIR", "results")

# Dashboard -> API base URL. Never hard-code localhost for deployments;
# set IOT_API_URL instead.
API_URL = _env_str("IOT_API_URL", "http://127.0.0.1:8000").rstrip("/")


# ---------------------------------------------------------------------------
# LSTM input contract (verified from existing code; DO NOT change)
# ---------------------------------------------------------------------------
# Source: external_validation/create_main_sequences.py, train_main_lstm.py,
# api.py. Input shape (1, 10, 4), MinMax-scaled, output = scaled latency of the
# next time step, inverted through feature index 1.

SEQUENCE_LENGTH = 10
FEATURE_ORDER = ("bandwidth", "latency", "cpu_usage", "task_size")
DATASET_FEATURE_COLUMNS = (
    "Bandwidth_Mbps",
    "Latency_ms",
    "CPU_Usage_percent",
    "Task_Size_MB",
)
LATENCY_FEATURE_INDEX = 1

# Source: train_main_lstm.py -> train_size = int(len(X) * 0.8) (chronological).
TRAIN_FRACTION = 0.8

# The held-out windows (last 20 %) are split chronologically into a
# calibration half (used to fit the conformal quantile) and a test half (used
# only to measure coverage / MAE / RMSE). Because the CSV is stored in
# Stable -> Fluctuating -> Congested blocks, BOTH halves are Congested only.
CALIBRATION_FRACTION_OF_HOLDOUT = 0.5


# ---------------------------------------------------------------------------
# Input validation bounds
# ---------------------------------------------------------------------------
# Generous physical sanity limits, not model limits. They exist to reject
# NaN/inf/negative/garbage input, not to restrict normal operation.

MAX_BANDWIDTH_MBPS = 100_000.0
MAX_LATENCY_MS = 60_000.0
MAX_TASK_SIZE_MB = 100_000.0
MAX_DEADLINE_MS = 3_600_000.0


# ---------------------------------------------------------------------------
# Uncertainty
# ---------------------------------------------------------------------------

# Miscoverage level for split-conformal intervals (target 90 % coverage on
# exchangeable data from the calibrated regime).
CONFORMAL_ALPHA = _env_float("IOT_CONFORMAL_ALPHA", 0.10)

# Floor for the per-window latency standard deviation used to normalise
# conformal scores. Prevents a zero-width interval when all 10 observed
# latencies are identical. 1 ms is below the dataset's integer resolution.
SIGMA_FLOOR_MS = 1.0

# Network conditions (from network_analyzer.analyze_network) for which the
# calibration is valid. Only CONGESTED data exists in the held-out split.
CALIBRATED_CONDITIONS = ("CONGESTED",)

# Uncertainty levels that make the engine use the pessimistic network bound
# instead of the point prediction.
PESSIMISTIC_LEVELS = ("moderate", "high", "uncalibrated", "unavailable")

# Uncertainty levels that trigger the conservative EDGE fallback for
# latency-sensitive (critical/high priority) tasks.
FALLBACK_LEVELS = ("high", "uncalibrated", "unavailable")


# ---------------------------------------------------------------------------
# Edge feasibility / network state thresholds (reused from existing code)
# ---------------------------------------------------------------------------

# Source: decision_engine.py treats CPU > 85 % as "device is overloaded".
EDGE_CPU_OVERLOAD_PCT = _env_float("IOT_EDGE_CPU_OVERLOAD_PCT", 85.0)

# Source: decision_engine.py latency bands (>80 ms "high", >150 ms "very
# high"). Used only for the Normal / Warning / Critical display state.
LATENCY_WARNING_MS = 80.0
LATENCY_CRITICAL_MS = 150.0


# ---------------------------------------------------------------------------
# Completion-time cost model (SIMULATION ASSUMPTIONS)
# ---------------------------------------------------------------------------
# Source: performance_simulation.py. Values are duplicated here (rather than
# imported) because performance_simulation.py imports matplotlib at module
# level; tests/test_decision.py asserts that the two stay identical.


@dataclass(frozen=True)
class CostModel:
    edge_ms_per_mb: float = 80.0  # EDGE_BASE_COMPUTE_MS_PER_MB
    cloud_ms_per_mb: float = 20.0  # CLOUD_BASE_COMPUTE_MS_PER_MB
    edge_cpu_impact: float = 1.5  # EDGE_CPU_IMPACT
    cloud_cpu_impact: float = 0.2  # CLOUD_CPU_IMPACT


DEFAULT_COST_MODEL = CostModel()


# ---------------------------------------------------------------------------
# Synthetic workload assumptions (used by simulation / evaluation only)
# ---------------------------------------------------------------------------
# Default deadlines per priority. Chosen to span the range of completion
# times produced by the cost model above for 1-10 MB tasks (edge roughly
# 80-2000 ms, cloud roughly 30-900 ms), so that deadlines are neither
# trivially met nor impossible. They are NOT taken from a real deployment.

DEFAULT_DEADLINE_MS = {
    "critical": 500.0,
    "high": 1000.0,
    "normal": 2000.0,
    "low": None,  # no deadline
}

