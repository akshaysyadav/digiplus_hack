"""
Data Service

Responsible for:
- Loading raw CSV datasets from `data/sample_data/`
- Parsing, validating, and caching data in memory
- Providing fast lookup methods for tickets, orders, and resolved precedent datasets
"""

import pandas as pd
from typing import List, Dict, Optional
from app.core.config import RESOLVED_TICKETS_CSV, NEW_TICKETS_CSV, ORDERS_CONTEXT_CSV
from app.models.schemas import RawNewTicket, OrderContext, PrecedentMatch


class DataService:
    def __init__(self):
        self._resolved_df: Optional[pd.DataFrame] = None
        self._new_tickets_df: Optional[pd.DataFrame] = None
        self._orders_df: Optional[pd.DataFrame] = None
        self.load_all_data()

    def load_all_data(self) -> None:
        """Loads and caches all three datasets into memory."""
        self._resolved_df = pd.read_csv(RESOLVED_TICKETS_CSV)
        self._new_tickets_df = pd.read_csv(NEW_TICKETS_CSV)
        self._orders_df = pd.read_csv(ORDERS_CONTEXT_CSV)

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

    def get_all_new_tickets(self) -> List[Dict]:
        """Returns all incoming tickets as list of dictionaries."""
        return self.new_tickets_df.to_dict(orient="records")

    def get_new_ticket_by_id(self, ticket_id: str) -> Optional[Dict]:
        """Lookup a single incoming ticket by ticket_id."""
        matches = self.new_tickets_df[self.new_tickets_df["ticket_id"] == ticket_id]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

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

    def get_resolved_ticket_by_id(self, ticket_id: str) -> Optional[Dict]:
        """Lookup historical resolved ticket by ticket_id."""
        matches = self.resolved_tickets_df[self.resolved_tickets_df["ticket_id"] == ticket_id]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()


# Global singleton instance
data_service = DataService()
