# metadata/review/review_engine.py
import logging
from typing import Any, List, Optional
from datetime import datetime

from metadata.review.review_models import MetadataPackage, ReviewReport, ComponentScores, ReviewSeverity, ReviewRecommendation
from metadata.review.review_validator import ReviewValidator
from metadata.review.seo_score import SEOScoreCalculator
from metadata.review.commercial_score import CommercialScoreCalculator
from metadata.review.readability_score import ReadabilityCalculator
from metadata.review.quality_score import QualityScoreCalculator
from metadata.review.confidence_score import ConfidenceScoreCalculator
from metadata.review.self_improvement import SelfImprovementEngine

logger = logging.getLogger(__name__)

class MetadataReviewEngine:
    def __init__(self, ai_manager: Any):
        self.validator = ReviewValidator()
        self.seo_calc = SEOScoreCalculator()
        self.comm_calc = CommercialScoreCalculator()
        self.read_calc = ReadabilityCalculator()
        self.quality_calc = QualityScoreCalculator()
        self.conf_calc = ConfidenceScoreCalculator()
        self.self_improve = SelfImprovementEngine(ai_manager)

    def review(self, package: MetadataPackage, base_confidence: float = 0.8, revision_count: int = 0) -> ReviewReport:
        logger.info(f"Starting metadata review (revision {revision_count})")
        
        recommendations = self.validator.run_validation(package)
        
        critical_errors = [r for r in recommendations if r.severity == ReviewSeverity.CRITICAL]
        warnings = [r for r in recommendations if r.severity == ReviewSeverity.WARNING]
        infos = [r for r in recommendations if r.severity == ReviewSeverity.INFO]

        seo_score = self.seo_calc.calculate(package)
        comm_score = self.comm_calc.calculate(package)
        read_score = self.read_calc.calculate(package.description)
        
        validation_penalty_count = len(critical_errors) * 3 + len(warnings)
        
        grammar_score = self.quality_calc.calculate_component_score(100.0, len([r for r in warnings if r.category == "Grammar"]))
        market_score = self.quality_calc.calculate_component_score(100.0, len(critical_errors), penalty_weight=20.0)
        conf_score = self.conf_calc.calculate(base_confidence, validation_penalty_count)

        components = ComponentScores(
            title=100.0 if not any("Title" in r.message for r in critical_errors + warnings) else 70.0,
            description=100.0 if not any("Description" in r.message for r in critical_errors + warnings) else 70.0,
            keywords=100.0 if not any("Keyword" in r.message for r in critical_errors + warnings) else 70.0,
            seo=seo_score,
            commercial=comm_score,
            grammar=grammar_score,
            readability=read_score,
            marketplace=market_score,
            confidence=conf_score
        )

        overall_score = self.quality_calc.calculate_overall(components)
        
        is_approved = len(critical_errors) == 0 and overall_score >= 70.0

        if seo_score < 70:
            infos.append(ReviewRecommendation(category="SEO", message="Overall SEO score is low.", severity=ReviewSeverity.INFO, explanation="Improve title length, description detail, and keyword relevance.", actionable=True))
        if comm_score < 60:
            infos.append(ReviewRecommendation(category="Commercial", message="Commercial value is weak.", severity=ReviewSeverity.INFO, explanation="Add business, corporate, or industry-specific terms.", actionable=True))

        report = ReviewReport(
            is_approved=is_approved,
            overall_score=overall_score,
            component_scores=components,
            recommendations=infos,
            warnings=warnings,
            critical_errors=critical_errors,
            original_package=package,
            revision_count=revision_count
        )
        
        logger.info(f"Review complete. Score: {overall_score}, Approved: {is_approved}")
        return report

    def request_improvement(self, report: ReviewReport) -> ReviewReport:
        if report.revision_count >= 1:
            logger.info("Max revisions reached. Cannot improve further.")
            return report
            
        improved_package = self.self_improve.refine(report.original_package, report)
        
        if improved_package:
            new_report = self.review(improved_package, base_confidence=0.9, revision_count=report.revision_count + 1)
            new_report.improved_package = improved_package
            return new_report
            
        return report