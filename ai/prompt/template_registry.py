# ai/prompt/template_registry.py
import logging
from threading import Lock
from typing import List, Dict, Optional
from datetime import datetime

from .prompt_template import PromptTemplate
from .template_loader import TemplateLoader
from .template_version import TemplateVersion

logger = logging.getLogger("TemplateRegistry")

class TemplateRegistry:
    """In-memory thread-safe state manager for active prompt templates and their historical versions."""

    def __init__(self, loader: TemplateLoader):
        self._loader = loader
        self._templates: Dict[str, PromptTemplate] = {}
        self._versions: Dict[str, List[TemplateVersion]] = {}
        self._lock = Lock()

    def initialize(self) -> None:
        """Loads all templates from the storage boundary into operational memory."""
        with self._lock:
            loaded = self._loader.load_all()
            for t in loaded:
                self._templates[t.id] = t
                if t.id not in self._versions:
                    self._versions[t.id] = []
            logger.info(f"Template Registry initialized with {len(self._templates)} templates.")

    def get(self, template_id: str) -> Optional[PromptTemplate]:
        with self._lock:
            return self._templates.get(template_id)

    def get_all_active(self) -> List[PromptTemplate]:
        with self._lock:
            return [t for t in self._templates.values() if t.is_active]

    def save(self, template: PromptTemplate, change_summary: str = "Updated via editor") -> bool:
        with self._lock:
            template.updated_at = datetime.now()
            if self._loader.save(template):
                self._templates[template.id] = template
                self._record_version(template, change_summary)
                return True
            return False

    def _record_version(self, template: PromptTemplate, summary: str) -> None:
        version = TemplateVersion(
            version_id=f"{template.id}_{template.version}_{datetime.now().timestamp()}",
            template_id=template.id,
            content=template.content,
            version_tag=template.version,
            change_summary=summary
        )
        if template.id not in self._versions:
            self._versions[template.id] = []
        self._versions[template.id].append(version)

    def get_versions(self, template_id: str) -> List[TemplateVersion]:
        with self._lock:
            return sorted(self._versions.get(template_id, []), key=lambda v: v.created_at, reverse=True)