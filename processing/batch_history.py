# processing/batch_history.py
import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class BatchRecord:
    batch_id: str
    timestamp: str
    total_images: int
    successful_images: int
    failed_images: int
    duration_seconds: float
    provider: str
    average_score: float = 0.0

class BatchHistory:
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "batch_history.jsonl"

    def record_batch(self, record: BatchRecord) -> None:
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(record)) + '\n')
            logger.debug(f"Recorded batch history {record.batch_id}")
        except IOError as e:
            logger.error(f"Failed to write batch history: {e}")

    def get_history(self) -> List[BatchRecord]:
        results: List[BatchRecord] = []
        if not self.history_file.exists():
            return results
            
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        results.append(BatchRecord(**data))
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read batch history: {e}")
            
        return sorted(results, key=lambda x: x.timestamp, reverse=True)