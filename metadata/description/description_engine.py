# metadata/description/description_engine.py
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from metadata.description.description_generator import DescriptionGenerator, DescriptionGenerationContext
from metadata.description.description_validator import DescriptionValidator, ValidationReport
from metadata.description.description_ranker import DescriptionRanker, RankedDescription
from metadata.description.description_optimizer import DescriptionOptimizer
from metadata.description.description_cache import DescriptionCache
from metadata.description.description_history import DescriptionHistory, DescriptionRecord
from metadata.description.description_statistics import DescriptionStatistics
from metadata.description.description_rules import DEFAULT_DESCRIPTION_RULES

logger = logging.getLogger(__name__)

class DescriptionIntelligenceEngine:
    def __init__(self, ai_manager: Any, base_dir: Path):
        self.generator = DescriptionGenerator(ai_manager)
        self.validator = DescriptionValidator(DEFAULT_DESCRIPTION_RULES)
        self.optimizer = DescriptionOptimizer()
        self.ranker = DescriptionRanker()
        self.cache = DescriptionCache(base_dir / "cache")
        self.history = DescriptionHistory(base_dir / "history")
        self.statistics = DescriptionStatistics(base_dir / "stats.json")
        self.prompt_version = "v1.0"
        logger.info("DescriptionIntelligenceEngine initialized.")

    def process_asset(self, image_hash: str, subject: str, scene: str, objects: str, style: str, concepts: str, keywords: str, marketplace: str = "adobe_stock", language: str = "en") -> Dict[str, Any]:
        start_time = time.time()
        provider = self.generator.ai_manager.current_provider
        
        cached_descriptions = self.cache.get(image_hash, self.prompt_version, marketplace, language, provider)
        if cached_descriptions:
            candidates = cached_descriptions
            logger.info(f"Using cached descriptions for {image_hash}")
        else:
            context = DescriptionGenerationContext(
                subject=subject, scene=scene, objects=objects, 
                style=style, concepts=concepts, keywords=keywords, 
                marketplace=marketplace, language=language
            )
            raw_candidates = self.generator.generate_candidates(context)
            candidates = [self.optimizer.optimize(c) for c in raw_candidates]
            self.cache.set(image_hash, self.prompt_version, marketplace, language, provider, candidates)

        valid_candidates = []
        for desc in candidates:
            report = self.validator.validate(desc)
            if report.is_valid:
                valid_candidates.append(desc)
            else:
                for error in report.errors:
                    self.statistics.log_validation_failure(error)

        if not valid_candidates:
            logger.warning(f"No valid descriptions generated for {image_hash}. Falling back to default.")
            fallback = self.optimizer.optimize(f"{subject} in {scene} featuring {objects}. {concepts}")
            valid_candidates = [fallback]

        ranked_results = self.ranker.rank(valid_candidates)
        best_desc = ranked_results[0]
        alternative_descs = [r.description for r in ranked_results[1:]]

        duration = time.time() - start_time

        history_record = DescriptionRecord(
            image_hash=image_hash,
            selected_description=best_desc.description,
            alternative_descriptions=alternative_descs,
            provider=provider,
            prompt_version=self.prompt_version,
            overall_score=best_desc.score,
            seo_score=best_desc.seo_quality,
            commercial_score=best_desc.commercial_value
        )
        self.history.record(history_record)
        self.statistics.log_generation(len(best_desc.description), best_desc.seo_quality, best_desc.commercial_score, duration)

        logger.info(f"Successfully processed description for {image_hash}. Best score: {best_desc.score}")

        return {
            "description": best_desc.description,
            "score": best_desc.score,
            "alternatives": alternative_descs,
            "ranked_details": [
                {
                    "description": r.description, 
                    "score": r.score, 
                    "seo": r.seo_quality, 
                    "comm": r.commercial_value,
                    "readability": r.readability
                } 
                for r in ranked_results
            ]
        }