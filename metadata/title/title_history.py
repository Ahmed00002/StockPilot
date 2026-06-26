# metadata/title/title_history.py
import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

@dataclass
class TitleRecord:
    image_hash: str
    selected_title: str
    alternative_titles: List[str]
    provider: str
    prompt_version: str
    score: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class TitleHistory:
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "title_history.jsonl"

    def record(self, record: TitleRecord) -> None:
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(record)) + '\n')
            logger.info(f"Recorded title history for image {record.image_hash}")
        except IOError as e:
            logger.error(f"Failed to write title history: {e}")

    def get_history(self, image_hash: str) -> List[TitleRecord]:
        results: List[TitleRecord] = []
        if not self.history_file.exists():
            return results
            
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data.get('image_hash') == image_hash:
                        results.append(TitleRecord(**data))
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read title history: {e}")
            
        return results