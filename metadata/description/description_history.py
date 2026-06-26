# metadata/description/description_history.py
import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class DescriptionRecord:
    image_hash: str
    selected_description: str
    alternative_descriptions: List[str]
    provider: str
    prompt_version: str
    overall_score: float
    seo_score: float
    commercial_score: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class DescriptionHistory:
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "description_history.jsonl"

    def record(self, record: DescriptionRecord) -> None:
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(record)) + '\n')
        except IOError as e:
            logger.error(f"Failed to write description history: {e}")

    def get_history(self, image_hash: str) -> List[DescriptionRecord]:
        results: List[DescriptionRecord] = []
        if not self.history_file.exists():
            return results
            
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data.get('image_hash') == image_hash:
                        results.append(DescriptionRecord(**data))
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read description history: {e}")
            
        return results