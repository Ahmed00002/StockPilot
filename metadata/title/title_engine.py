# metadata/title/title_engine.py
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from metadata.title.title_generator import TitleGenerator, GenerationContext
from metadata.title.title_validator import TitleValidator, ValidationReport
from metadata.title.title_ranker import TitleRanker, RankedTitle
from metadata.title.title_optimizer import TitleOptimizer
from metadata.title.title_cache import TitleCache
from metadata.title.title_history import TitleHistory, TitleRecord
from metadata.title.title_statistics import TitleStatistics
from metadata.title.title_rules import DEFAULT_RULES

logger = logging.getLogger(__name__)

class TitleIntelligenceEngine:
    def __init__(self, ai_manager: Any, base_dir: Path):
        self.generator = TitleGenerator(ai_manager)
        self.validator = TitleValidator(DEFAULT_RULES)
        self.optimizer = TitleOptimizer()
        self.ranker = TitleRanker()
        self.cache = TitleCache(base_dir / "cache")
        self.history = TitleHistory(base_dir / "history")
        self.statistics = TitleStatistics(base_dir / "stats.json")
        self.prompt_version = "v1.0"
        logger.info("TitleIntelligenceEngine initialized.")

    def process_asset(self, image_hash: str, subject: str, concepts: str, keywords: str, marketplace: str = "adobe_stock", language: str = "en") -> Dict[str, Any]:
        start_time = time.time()
        provider = self.generator.ai_manager.current_provider
        
        cached_titles = self.cache.get(image_hash, self.prompt_version, marketplace, language, provider)
        if cached_titles:
            candidates = cached_titles
            logger.info(f"Using cached titles for {image_hash}")
        else:
            context = GenerationContext(subject=subject, concepts=concepts, keywords=keywords, marketplace=marketplace, language=language)
            raw_candidates = self.generator.generate_candidates(context)
            candidates = [self.optimizer.optimize(c) for c in raw_candidates]
            self.cache.set(image_hash, self.prompt_version, marketplace, language, provider, candidates)

        valid_candidates = []
        for title in candidates:
            report = self.validator.validate(title)
            if report.is_valid:
                valid_candidates.append(title)
            else:
                for error in report.errors:
                    self.statistics.log_validation_failure(error)

        if not valid_candidates:
            logger.warning(f"No valid titles generated for {image_hash}. Falling back to default.")
            valid_candidates = [self.optimizer.optimize(subject)]

        ranked_results = self.ranker.rank(valid_candidates)
        best_title = ranked_results[0]
        alternative_titles = [r.title for r in ranked_results[1:]]

        duration = time.time() - start_time

        history_record = TitleRecord(
            image_hash=image_hash,
            selected_title=best_title.title,
            alternative_titles=alternative_titles,
            provider=provider,
            prompt_version=self.prompt_version,
            score=best_title.score
        )
        self.history.record(history_record)
        self.statistics.log_generation(len(best_title.title), best_title.score, duration)

        logger.info(f"Successfully processed title for {image_hash}. Best score: {best_title.score}")

        return {
            "title": best_title.title,
            "score": best_title.score,
            "alternatives": alternative_titles,
            "ranked_details": [
                {"title": r.title, "score": r.score, "seo": r.seo_quality, "comm": r.commercial_value} 
                for r in ranked_results
            ]
        }