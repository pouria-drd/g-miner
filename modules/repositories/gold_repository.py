import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from modules.configs import get_settings


class GoldRepository:
    """
    Repository for storing/retrieving gold prices as a list of entries.
    Each entry has a timestamp and a unique UUID.
    """

    def __init__(self):
        """
        Args:
            db_file (Path): Path to the JSON DB file.
            timestamp_func (Callable): Function returning a timestamp string. Default is UTC now.
        """
        settings = get_settings()
        self.db_file = settings["GOLD_DB_FILE"]
        self.timestamp_func = lambda: datetime.now(timezone.utc).isoformat()

        if not self.db_file.exists():
            self._write([])

    def create(self, price_data: Dict[str, Optional[int]]):
        """
        Add a new price entry with a timestamp and unique UUID,
        but keep ONLY the last 3 records in the file.
        """
        db = self._read()

        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": self.timestamp_func(),
            **price_data,
        }

        db.append(entry)
        db = db[-3:]  # Keep only the last 3 records

        self._write(db)

    def get_latest(self) -> Optional[Dict[str, Optional[int]]]:
        """Return the latest price entry."""
        db = self._read()
        if not db:
            return None
        return db[-1]

    def get_all(self) -> List[Dict[str, Optional[int]]]:
        """Return all stored price entries."""
        return self._read()

    def _read(self) -> List[Dict]:
        """Read the JSON DB as a list of entries."""
        try:
            with self.db_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write(self, data: List[Dict]):
        """Write list of entries to JSON DB."""
        with self.db_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
