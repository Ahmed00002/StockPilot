# ai/orchestration/provider_priority.py
import logging
from threading import Lock
from typing import List

logger = logging.getLogger("ProviderPriority")

class ProviderPriority:
    """
    Maintains the global ordered priority list for AI providers.
    Allows dynamic reordering via the user interface.
    """

    def __init__(self):
        self._lock = Lock()
        self._priority_list: List[str] = [
            "Google Gemini",
            "OpenAI Engine",
            "Anthropic Claude",
            "Groq LPU Engine",
            "DeepSeek",
            "OpenRouter Gateway System"
        ]

    def get_priority_list(self) -> List[str]:
        with self._lock:
            return list(self._priority_list)

    def set_priority_list(self, new_list: List[str]) -> None:
        with self._lock:
            self._priority_list = list(new_list)
        logger.info(f"Provider priority updated: {self._priority_list}")

    def sort_providers(self, available_providers: List[str]) -> List[str]:
        """
        Sorts a subset of available providers according to the master priority list.
        Unknown providers are appended to the end.
        """
        with self._lock:
            priority_map = {name: index for index, name in enumerate(self._priority_list)}
            
            # Providers not in the priority list get a high index so they sort to the bottom
            max_index = len(self._priority_list)
            
            return sorted(
                available_providers, 
                key=lambda p: priority_map.get(p, max_index)
            )