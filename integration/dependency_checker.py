# integration/dependency_checker.py
import logging
import importlib
from typing import List, Tuple

logger = logging.getLogger(__name__)

class DependencyChecker:
    def __init__(self):
        self.required_modules = [
            "core.ai.ai_manager",
            "metadata.vision.vision_pipeline",
            "metadata.title.title_engine",
            "metadata.description.description_engine",
            "metadata.keywords.keyword_engine",
            "metadata.review.review_engine",
            "metadata.compliance.compliance_engine",
            "metadata.workspace.workspace_manager",
            "processing.batch_manager"
        ]

    def check_dependencies(self) -> Tuple[bool, List[str]]:
        missing = []
        for module_name in self.required_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                logger.error(f"Missing dependency: {module_name} ({e})")
                missing.append(module_name)
                
        is_ready = len(missing) == 0
        if is_ready:
            logger.info("All pipeline dependencies verified successfully.")
            
        return is_ready, missing