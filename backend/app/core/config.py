"""
Application Configuration & Settings Placeholder

Defines path constants, similarity thresholds, and configuration settings.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR.parent / "data" / "sample_data"

# Dataset Paths in data/sample_data/
RESOLVED_TICKETS_CSV = DATA_DIR / "resolved_tickets.csv"
NEW_TICKETS_CSV = DATA_DIR / "new_tickets.csv"
ORDERS_CONTEXT_CSV = DATA_DIR / "orders_context.csv"

# Alternative 8.3 short filenames fallback if needed
RESOLVED_TICKETS_SHORT_CSV = DATA_DIR / "RESOLV~1.CSV"
NEW_TICKETS_SHORT_CSV = DATA_DIR / "NEW_TI~1.CSV"
ORDERS_CONTEXT_SHORT_CSV = DATA_DIR / "ORDERS~1.CSV"

# Business & Similarity Thresholds (Placeholders)
SIMILARITY_THRESHOLD_HIGH = 0.75  # High precedent confidence
TOP_K_PRECEDENTS = 3              # Top 3 historical precedents

