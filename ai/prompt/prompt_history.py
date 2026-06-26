# ai/prompt/prompt_history.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from threading import Lock
import logging

logger = logging.getLogger("PromptHistory")

@dataclass
class PromptHistoryEntry:
    entry_id: str
    timestamp: datetime
    workspace: str
    provider: str
    marketplace: str
    template_name: str
    final_prompt: str
    prompt_length: int
    estimated_tokens: int

class PromptHistory:
    """Thread-safe ledger maintaining chronological tracking records of all dispatched prompts."""

    def __init__(self, max_history_size: int = 1000):
        self._history: List[PromptHistoryEntry] = []
        self._max_size = max_history_size
        self._lock = Lock()

    def record(self, entry: PromptHistoryEntry) -> None:
        with self._lock:
            self._history.insert(0, entry)
            if len(self._history) > self._max_size:
                self._history.pop()

    def get_recent(self, limit: int = 50) -> List[PromptHistoryEntry]:
        with self._lock:
            return self._history[:limit]
            
    def get_by_workspace(self, workspace: str) -> List[PromptHistoryEntry]:
        with self._lock:
            return [e for e in self._history if e.workspace == workspace]