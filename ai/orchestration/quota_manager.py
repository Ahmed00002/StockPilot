# ai/orchestration/quota_manager.py
import logging
from threading import Lock
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger("QuotaManager")

@dataclass
class QuotaConfig:
    daily_requests_cap: int = 1000
    monthly_cost_cap: float = 100.00
    
@dataclass
class QuotaUsage:
    daily_requests: int = 0
    monthly_cost: float = 0.0

class QuotaManager:
    """
    Enforces localized budget and usage restrictions across workspaces to prevent
    runaway API costs and exhaustion of provider accounts.
    """

    def __init__(self):
        self._lock = Lock()
        self._configs: Dict[str, QuotaConfig] = {}
        self._usage: Dict[str, QuotaUsage] = {}

    def set_workspace_quota(self, workspace: str, config: QuotaConfig) -> None:
        with self._lock:
            self._configs[workspace] = config
            if workspace not in self._usage:
                self._usage[workspace] = QuotaUsage()

    def record_request(self, workspace: str, cost: float = 0.0) -> None:
        with self._lock:
            if workspace not in self._usage:
                self._usage[workspace] = QuotaUsage()
            self._usage[workspace].daily_requests += 1
            self._usage[workspace].monthly_cost += cost

    def check_quota(self, workspace: str) -> bool:
        with self._lock:
            config = self._configs.get(workspace)
            if not config:
                return True # Unrestricted if no config exists
                
            usage = self._usage.get(workspace, QuotaUsage())
            
            if usage.daily_requests >= config.daily_requests_cap:
                logger.warning(f"Workspace '{workspace}' has exceeded daily request quota.")
                return False
                
            if usage.monthly_cost >= config.monthly_cost_cap:
                logger.warning(f"Workspace '{workspace}' has exceeded monthly monetary quota.")
                return False
                
            return True
            
    def reset_daily_quota(self) -> None:
        with self._lock:
            for usage in self._usage.values():
                usage.daily_requests = 0