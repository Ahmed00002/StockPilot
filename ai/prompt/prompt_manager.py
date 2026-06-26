# ai/prompt/prompt_manager.py
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from .template_loader import TemplateLoader
from .template_registry import TemplateRegistry
from .context_builder import ContextBuilder, PromptContext
from .prompt_builder import PromptBuilder, BuildResult
from .prompt_validator import PromptValidator, ValidationReport
from .prompt_cache import PromptCache
from .prompt_history import PromptHistory, PromptHistoryEntry
from .prompt_statistics import PromptStatistics
import datetime

logger = logging.getLogger("PromptManager")

class PromptManager:
    """High-level Facade controlling all lifecycle events within the Prompt Intelligence Engine."""

    def __init__(self, storage_path: Path):
        self._loader = TemplateLoader(storage_path)
        self.registry = TemplateRegistry(self._loader)
        self.cache = PromptCache()
        self.history = PromptHistory()
        self.statistics = PromptStatistics()

    def initialize(self) -> None:
        logger.info("Initializing Prompt Intelligence Engine...")
        self.registry.initialize()

    def generate_prompt(
        self,
        template_id: str,
        workspace: str,
        language: str,
        marketplace: str,
        provider: str,
        image_path: Optional[Path] = None,
        intelligence_data: Optional[Dict[str, Any]] = None,
        user_prefs: Optional[Dict[str, str]] = None,
        image_hash: str = "unknown"
    ) -> Tuple[Optional[str], Optional[str], ValidationReport]:
        """
        Executes the entire intelligence pipeline to output a verified, optimized string payload.
        Returns: (final_prompt, system_prompt, validation_report)
        """
        
        template = self.registry.get(template_id)
        if not template:
            logger.error(f"Cannot generate prompt. Template ID '{template_id}' is unmapped.")
            return None, None, ValidationReport(is_valid=False, errors=[f"Template {template_id} not found."])

        # Check Cache
        cached_prompt = self.cache.get(workspace, image_hash, marketplace, language, provider, template.version)
        if cached_prompt:
            self.statistics.record_cache_hit()
            # Note: System prompts aren't heavily cached as they are deterministic by provider/language rules
            context = ContextBuilder.build(workspace, language, marketplace, provider, image_path, intelligence_data, user_prefs)
            build_result = PromptBuilder.build(template, context)
            return cached_prompt, build_result.system_prompt, ValidationReport(is_valid=True)
            
        self.statistics.record_cache_miss()

        # Build Context
        context = ContextBuilder.build(
            workspace, language, marketplace, provider, image_path, intelligence_data, user_prefs
        )

        # Build Prompt
        build_result = PromptBuilder.build(template, context)

        # Validate
        validation = PromptValidator.validate(build_result.final_prompt, template.content, context.to_dict())
        if not validation.is_valid:
            self.statistics.record_validation_error()
            logger.warning(f"Prompt Validation failed for template {template_id}: {validation.errors}")
            return build_result.final_prompt, build_result.system_prompt, validation

        # Cache Successful Build
        self.cache.set(workspace, image_hash, marketplace, language, provider, template.version, build_result.final_prompt)

        # Record History
        hist_entry = PromptHistoryEntry(
            entry_id=f"hist_{datetime.datetime.now().timestamp()}",
            timestamp=datetime.datetime.now(),
            workspace=workspace,
            provider=provider,
            marketplace=marketplace,
            template_name=template.name,
            final_prompt=build_result.final_prompt,
            prompt_length=len(build_result.final_prompt),
            estimated_tokens=len(build_result.final_prompt) // 4
        )
        self.history.record(hist_entry)

        # Record Stats
        self.statistics.record_build(len(build_result.final_prompt), build_result.optimization_savings_chars)

        return build_result.final_prompt, build_result.system_prompt, validation