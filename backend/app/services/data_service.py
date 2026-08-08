"""
Data Service

Responsible for:
- Loading raw CSV datasets from `data/sample_data/`
- Parsing, validating, and caching data in memory
- Providing fast lookup methods for tickets, orders, and resolved precedent datasets
"""

import os
import json
import logging
from datetime import datetime, timezone
import pandas as pd
from typing import List, Dict, Optional
from app.core.config import (
    RESOLVED_TICKETS_CSV,
    NEW_TICKETS_CSV,
    ORDERS_CONTEXT_CSV,
    SIMULATED_TICKETS_JSON
)
from app.models.schemas import RawNewTicket, OrderContext, PrecedentMatch

logger = logging.getLogger(__name__)


class DataService:
    def __init__(self):
        self._resolved_df: Optional[pd.DataFrame] = None
        self._new_tickets_df: Optional[pd.DataFrame] = None
        self._orders_df: Optional[pd.DataFrame] = None
        self._simulated_tickets: List[Dict] = []
        self.load_all_data()

    def load_all_data(self) -> None:
        """Loads CSV datasets and restores persisted simulated tickets into memory."""
        self._resolved_df = pd.read_csv(RESOLVED_TICKETS_CSV)
        self._new_tickets_df = pd.read_csv(NEW_TICKETS_CSV)
        self._orders_df = pd.read_csv(ORDERS_CONTEXT_CSV)
        self._load_simulated_tickets()

    def _load_simulated_tickets(self) -> None:
        """Safely loads simulated tickets from local JSON storage without crashing on missing or corrupted files."""
        self._simulated_tickets = []
        if not SIMULATED_TICKETS_JSON.exists():
            return

        try:
            with open(SIMULATED_TICKETS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._simulated_tickets = data
                else:
                    logger.warning(
                        f"Warning: {SIMULATED_TICKETS_JSON} format invalid (expected list), falling back to empty collection."
                    )
        except Exception as ex:
            logger.warning(
                f"Warning: Failed to load simulated tickets from {SIMULATED_TICKETS_JSON}: {ex}. Starting with empty collection."
            )
            self._simulated_tickets = []

    def _save_simulated_tickets(self) -> None:
        """Atomically saves simulated tickets to local JSON storage."""
        try:
            SIMULATED_TICKETS_JSON.parent.mkdir(parents=True, exist_ok=True)
            temp_file = SIMULATED_TICKETS_JSON.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._simulated_tickets, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, SIMULATED_TICKETS_JSON)
        except Exception as ex:
            logger.error(f"Error saving simulated tickets to {SIMULATED_TICKETS_JSON}: {ex}")

    @property
    def resolved_tickets_df(self) -> pd.DataFrame:
        if self._resolved_df is None:
            self.load_all_data()
        return self._resolved_df

    @property
    def new_tickets_df(self) -> pd.DataFrame:
        if self._new_tickets_df is None:
            self.load_all_data()
        return self._new_tickets_df

    @property
    def orders_df(self) -> pd.DataFrame:
        if self._orders_df is None:
            self.load_all_data()
        return self._orders_df

    def add_simulated_ticket(self, description: str, order_id: str) -> Dict:
        """Creates, numbers sequentially, and persists a simulated ticket."""
        max_num = 0
        for t in self._simulated_tickets:
            tid = str(t.get("ticket_id", ""))
            if tid.startswith("SIM-"):
                try:
                    num = int(tid.split("-")[1])
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    pass

        sim_id = f"SIM-{str(max_num + 1).zfill(3)}"
        ticket_dict = {
            "ticket_id": sim_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "order_id": order_id,
            "description": description.strip()
        }
        self._simulated_tickets.append(ticket_dict)
        self._save_simulated_tickets()
        return ticket_dict

    def save_simulated_ticket_detail(self, ticket_id: str, detail_dict: dict) -> None:
        """Updates and persists complete evaluation detail for a simulated ticket."""
        if "order_id" not in detail_dict:
            order_info = detail_dict.get("order")
            if isinstance(order_info, dict):
                detail_dict["order_id"] = order_info.get("order_id", "")
            elif hasattr(order_info, "order_id"):
                detail_dict["order_id"] = getattr(order_info, "order_id", "")

        for i, t in enumerate(self._simulated_tickets):
            if t.get("ticket_id") == ticket_id:
                if "order_id" not in detail_dict and "order_id" in t:
                    detail_dict["order_id"] = t["order_id"]
                self._simulated_tickets[i] = detail_dict
                self._save_simulated_tickets()
                return
        self._simulated_tickets.append(detail_dict)
        self._save_simulated_tickets()

    def clear_simulated_tickets(self, delete_storage: bool = True) -> None:
        """Clears in-memory collection and removes persistent test file if requested."""
        self._simulated_tickets.clear()
        if delete_storage and SIMULATED_TICKETS_JSON.exists():
            try:
                SIMULATED_TICKETS_JSON.unlink()
            except Exception:
                pass

    def get_all_new_tickets(self) -> List[Dict]:
        """Returns all incoming tickets (CSV datasets + in-memory simulated tickets)."""
        csv_tickets = self.new_tickets_df.to_dict(orient="records")
        return csv_tickets + list(self._simulated_tickets)

    def get_new_ticket_by_id(self, ticket_id: str) -> Optional[Dict]:
        """Lookup a single incoming ticket by ticket_id (checks CSV first, then in-memory simulated tickets)."""
        matches = self.new_tickets_df[self.new_tickets_df["ticket_id"] == ticket_id]
        if not matches.empty:
            return matches.iloc[0].to_dict()
        
        for sim_ticket in self._simulated_tickets:
            if sim_ticket.get("ticket_id") == ticket_id:
                res = dict(sim_ticket)
                if "order_id" not in res and isinstance(res.get("order"), dict):
                    res["order_id"] = res["order"].get("order_id", "")
                return res
        return None


    def get_order_context(self, order_id: str) -> Optional[OrderContext]:
        """Lookup order context by order_id."""
        matches = self.orders_df[self.orders_df["order_id"] == order_id]
        if matches.empty:
            return None
        row = matches.iloc[0]
        return OrderContext(
            order_id=str(row["order_id"]),
            items=int(row["items"]),
            value_inr=int(row["value_inr"]),
            delivery_time_min=int(row["delivery_time_min"]),
            delivery_status=str(row["delivery_status"])
        )

    def get_all_orders(self) -> List[OrderContext]:
        """Returns all order contexts from the dataset."""
        order_list: List[OrderContext] = []
        for _, row in self.orders_df.iterrows():
            order_list.append(
                OrderContext(
                    order_id=str(row["order_id"]),
                    items=int(row["items"]),
                    value_inr=int(row["value_inr"]),
                    delivery_time_min=int(row["delivery_time_min"]),
                    delivery_status=str(row["delivery_status"])
                )
            )
        return order_list

    def get_resolved_ticket_by_id(self, ticket_id: str) -> Optional[Dict]:
        """Lookup historical resolved ticket by ticket_id."""
        matches = self.resolved_tickets_df[self.resolved_tickets_df["ticket_id"] == ticket_id]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()


# Global singleton instance
data_service = DataService()

