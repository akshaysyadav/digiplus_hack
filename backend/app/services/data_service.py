"""
Data Service Placeholder

Future Responsibility:
- Loading raw CSV datasets directly from `data/sample_data/`:
  - `resolved_tickets.csv` (`ticket_id`, `category`, `description`, `resolution_action`, `resolution_note`, `time_to_resolve_min`, `csat`)
  - `new_tickets.csv` (`ticket_id`, `created_at`, `order_id`, `description`)
  - `orders_context.csv` (`order_id`, `items`, `value_inr`, `delivery_time_min`, `delivery_status`)
- Parsing, validating, and caching data in memory
- Providing dataset queries for downstream services

TO BE IMPLEMENTED BY BACKEND DEVELOPER
"""


class DataService:
    def __init__(self):
        # Placeholder for loaded dataframes / records
        pass

    def load_resolved_tickets(self):
        """Loads historical 300 resolved tickets."""
        pass

    def load_new_tickets(self):
        """Loads 30 incoming test tickets."""
        pass

    def load_orders_context(self):
        """Loads 30 order context records."""
        pass
