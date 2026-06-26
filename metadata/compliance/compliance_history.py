# metadata/compliance/compliance_history.py
import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class ComplianceRecord:
    image_hash: str
    marketplace: str
    status: str
    overall_score: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class ComplianceHistory:
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "compliance_history.jsonl"

    def record(self, record: ComplianceRecord) -> None:
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(record)) + '\n')
        except IOError as e:
            logger.error(f"Failed to write compliance history: {e}")