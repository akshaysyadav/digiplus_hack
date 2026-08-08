"""
Application Configuration & Settings

Defines dataset paths, similarity thresholds, environment variables, and configuration constants.
"""

import os
from pathlib import Path
from typing import List

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR.parent / "data" / "sample_data"

# Fallback paths for Windows short filenames vs long filenames
def get_dataset_file(pattern: str, fallback_name: str) -> Path:
    matches = list(DATA_DIR.glob(pattern))
    if matches:
        return matches[0]
    return DATA_DIR / fallback_name

RESOLVED_TICKETS_CSV = get_dataset_file("*RESOLV*", "resolved_tickets.csv")
NEW_TICKETS_CSV = get_dataset_file("*NEW_TI*", "new_tickets.csv")
ORDERS_CONTEXT_CSV = get_dataset_file("*ORDERS*", "orders_context.csv")
SIMULATED_TICKETS_JSON = BASE_DIR.parent / "data" / "simulated_tickets.json"


# Evaluation Thresholds & Weights
SIMILARITY_THRESHOLD = 0.65  # Safety gate for out-of-distribution tickets
TOP_K_PRECEDENTS = 3         # Precedent retrieval count

# Confidence Formula Weights (sum = 1.00)
WEIGHT_SIMILARITY = 0.60
WEIGHT_AGREEMENT = 0.30
WEIGHT_VALIDITY = 0.10

# Fixed simulated policy values
COUPON_AMOUNT_INR = 50

# Server & Network Configuration (Supports cloud environments like Render/Railway/AWS)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Auto-load .env file from workspace root or backend dir if present
def _load_env():
    for env_path in [BASE_DIR.parent / ".env", BASE_DIR / ".env"]:
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass

_load_env()

# Gemini Generative AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

# CORS Configuration
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if raw_origins.strip() == "*":
    ALLOWED_ORIGINS: List[str] = ["*"]
else:
    ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

