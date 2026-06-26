# ai/orchestration/token_accountant.py
import logging
from threading import Lock
from dataclasses import dataclass
from typing import Dict
from ai.models import TokenUsage

logger = logging.getLogger("TokenAccountant")

@dataclass
class TokenLedger:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    image_tokens: int = 0
    total_tokens: int = 0

class TokenAccountant:
    """
    Centralized ledger for tracking exact token consumption across all providers,
    segmented by workspace and globally. Handles unknown estimations safely.
    """

    def __init__(self):
        self._lock = Lock()
        self._workspace_ledgers: Dict[str, TokenLedger] = {}
        self._provider_ledgers: Dict[str, TokenLedger] = {}
        self._global_ledger = TokenLedger()

    def record_usage(self, workspace: str, provider: str, usage: TokenUsage) -> None:
        """Commits transaction usage metrics to the active in-memory ledgers."""
        with self._lock:
            # Ensure records exist
            if workspace not in self._workspace_ledgers:
                self._workspace_ledgers[workspace] = TokenLedger()
            if provider not in self._provider_ledgers:
                self._provider_ledgers[provider] = TokenLedger()

            # We use standard isinstance/type checks if providers returned "unknown" strings,
            # but AI models strictly type TokenUsage as ints based on previous sprints.
            p_tokens = usage.prompt_tokens if isinstance(usage.prompt_tokens, int) else 0
            c_tokens = usage.response_tokens if isinstance(usage.response_tokens, int) else 0
            t_tokens = usage.total_tokens if isinstance(usage.total_tokens, int) else 0

            # Update Workspace Ledger
            self._workspace_ledgers[workspace].prompt_tokens += p_tokens
            self._workspace_ledgers[workspace].completion_tokens += c_tokens
            self._workspace_ledgers[workspace].total_tokens += t_tokens

            # Update Provider Ledger
            self._provider_ledgers[provider].prompt_tokens += p_tokens
            self._provider_ledgers[provider].completion_tokens += c_tokens
            self._provider_ledgers[provider].total_tokens += t_tokens

            # Update Global Ledger
            self._global_ledger.prompt_tokens += p_tokens
            self._global_ledger.completion_tokens += c_tokens
            self._global_ledger.total_tokens += t_tokens

    def get_workspace_totals(self, workspace: str) -> TokenLedger:
        with self._lock:
            return self._workspace_ledgers.get(workspace, TokenLedger())

    def get_provider_totals(self, provider: str) -> TokenLedger:
        with self._lock:
            return self._provider_ledgers.get(provider, TokenLedger())